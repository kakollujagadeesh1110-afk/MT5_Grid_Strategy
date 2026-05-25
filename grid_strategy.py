//+------------------------------------------------------------------+
//| AUTO GRID + AUTO HEDGE RECOVERY ENGINE - PRICE ONLY HARDENED     |
//| No indicators. Price/grid/hedge based logic only.                 |
//+------------------------------------------------------------------+
#property strict

#include <Trade/Trade.mqh>
CTrade trade;

//================ INPUTS =================//

input ulong  MagicNumber              = 26052501;

input double LotSize                  = 0.01;
input int    GridDistancePoints       = 100;
input double GridTriggerRatio         = 1.00;
input int    MaxTrades                = 50;
input double MaxGridLots              = 0.50;

input double BasketProfit             = 10.0;
input double BasketLossLimit          = -100.0;
input double CloseBufferUSD           = 2.0;

input int    RestartAfterHours        = 2;

input double HedgeTriggerUSD          = 100.0;
input double HedgeCoverageRatio       = 0.50;
input double MinHedgeLot              = 0.01;
input double MaxHedgeLot              = 1.00;

input double HedgeFixedLossUSD        = 100.0;
input double HedgeTrailStart          = 40.0;
input double HedgeTrailStep           = 25.0;

input double StopTradingBalance       = 100000.0;

input int    MaxSpreadPoints          = 80;
input double MinMarginLevelPercent    = 300.0;

input int    TradeCooldownSeconds     = 5;

input bool   EnablePriceShockGuard    = true;
input int    ShockWindowSeconds       = 60;
input int    ShockMovePoints          = 500;
input int    PauseAfterShockMinutes   = 30;

input bool   AllowHedgeDuringPause    = true;

//================ GLOBALS =================//

// -1 = not initialized, 0 = buy grid, 1 = sell grid
int currentDirection = -1;

double hedgeProfitPool = 0.0;
double hedgeLossPool   = 0.0;
double hedgePeakProfit = 0.0;

ENUM_ORDER_TYPE hedgeSignalType = ORDER_TYPE_BUY;

datetime PauseTradingUntil = 0;
datetime lastTradeTime     = 0;

double lastHedgeOpenPrice = 0.0;
bool hedgeLossMode        = false;

bool closeAllPending      = false;
bool closeAfterLoss       = false;

datetime shockWindowStart = 0;
double   shockWindowPrice = 0.0;

//+------------------------------------------------------------------+
//| GLOBAL VARIABLE PREFIX                                           |
//+------------------------------------------------------------------+
string GVPrefix()
{
   return "AGH_" + _Symbol + "_" + IntegerToString((int)MagicNumber) + "_";
}

//+------------------------------------------------------------------+
//| SAVE STATE                                                       |
//+------------------------------------------------------------------+
void SaveState()
{
   string p = GVPrefix();

   GlobalVariableSet(p + "currentDirection", currentDirection);
   GlobalVariableSet(p + "hedgeProfitPool", hedgeProfitPool);
   GlobalVariableSet(p + "hedgeLossPool", hedgeLossPool);
   GlobalVariableSet(p + "hedgePeakProfit", hedgePeakProfit);
   GlobalVariableSet(p + "PauseTradingUntil", (double)PauseTradingUntil);
   GlobalVariableSet(p + "lastHedgeOpenPrice", lastHedgeOpenPrice);
   GlobalVariableSet(p + "hedgeLossMode", hedgeLossMode ? 1.0 : 0.0);
}

//+------------------------------------------------------------------+
//| LOAD STATE                                                       |
//+------------------------------------------------------------------+
void LoadState()
{
   string p = GVPrefix();

   if(GlobalVariableCheck(p + "currentDirection"))
      currentDirection = (int)GlobalVariableGet(p + "currentDirection");

   if(GlobalVariableCheck(p + "hedgeProfitPool"))
      hedgeProfitPool = GlobalVariableGet(p + "hedgeProfitPool");

   if(GlobalVariableCheck(p + "hedgeLossPool"))
      hedgeLossPool = GlobalVariableGet(p + "hedgeLossPool");

   if(GlobalVariableCheck(p + "hedgePeakProfit"))
      hedgePeakProfit = GlobalVariableGet(p + "hedgePeakProfit");

   if(GlobalVariableCheck(p + "PauseTradingUntil"))
      PauseTradingUntil = (datetime)GlobalVariableGet(p + "PauseTradingUntil");

   if(GlobalVariableCheck(p + "lastHedgeOpenPrice"))
      lastHedgeOpenPrice = GlobalVariableGet(p + "lastHedgeOpenPrice");

   if(GlobalVariableCheck(p + "hedgeLossMode"))
      hedgeLossMode = (GlobalVariableGet(p + "hedgeLossMode") > 0.5);
}

//+------------------------------------------------------------------+
//| RESET ENGINE                                                     |
//+------------------------------------------------------------------+
void ResetEngine()
{
   hedgeProfitPool = 0.0;
   hedgeLossPool   = 0.0;
   hedgePeakProfit = 0.0;

   hedgeLossMode = false;
   lastHedgeOpenPrice = 0.0;

   SaveState();
}

//+------------------------------------------------------------------+
//| INIT                                                             |
//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(MagicNumber);
   trade.SetDeviationInPoints(30);
   trade.SetTypeFillingBySymbol(_Symbol);

   LoadState();

   shockWindowStart = TimeCurrent();

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   shockWindowPrice = (ask + bid) * 0.5;

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| DEINIT                                                           |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   SaveState();
   Comment("");
}

//+------------------------------------------------------------------+
//| VOLUME DIGITS                                                    |
//+------------------------------------------------------------------+
int VolumeDigits()
{
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   int digits = 0;

   while(step < 1.0 && digits < 8)
   {
      step *= 10.0;
      digits++;
   }

   return digits;
}

//+------------------------------------------------------------------+
//| NORMALIZE LOT                                                    |
//+------------------------------------------------------------------+
double NormalizeLot(double lot)
{
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(lot < minLot)
      lot = minLot;

   if(lot > maxLot)
      lot = maxLot;

   lot = MathFloor(lot / step) * step;

   return NormalizeDouble(lot, VolumeDigits());
}

//+------------------------------------------------------------------+
//| IS OUR POSITION                                                  |
//+------------------------------------------------------------------+
bool IsOurPosition()
{
   if(PositionGetString(POSITION_SYMBOL) != _Symbol)
      return false;

   if((ulong)PositionGetInteger(POSITION_MAGIC) != MagicNumber)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| IS GRID POSITION                                                 |
//+------------------------------------------------------------------+
bool IsGridPosition()
{
   if(!IsOurPosition())
      return false;

   string c = PositionGetString(POSITION_COMMENT);

   if(c == "GridBuy" || c == "GridSell")
      return true;

   return false;
}

//+------------------------------------------------------------------+
//| IS HEDGE POSITION                                                |
//+------------------------------------------------------------------+
bool IsHedgePosition()
{
   if(!IsOurPosition())
      return false;

   if(PositionGetString(POSITION_COMMENT) == "HEDGE")
      return true;

   return false;
}

//+------------------------------------------------------------------+
//| TOTAL OUR POSITIONS                                              |
//+------------------------------------------------------------------+
int TotalOurPositions()
{
   int count = 0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(IsOurPosition())
         count++;
   }

   return count;
}

//+------------------------------------------------------------------+
//| TOTAL GRID POSITIONS                                             |
//+------------------------------------------------------------------+
int TotalGridPositions()
{
   int count = 0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(IsGridPosition())
         count++;
   }

   return count;
}

//+------------------------------------------------------------------+
//| TOTAL PROFIT - ALL OUR POSITIONS                                 |
//+------------------------------------------------------------------+
double GetTotalProfit()
{
   double profit = 0.0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(IsOurPosition())
      {
         profit += PositionGetDouble(POSITION_PROFIT);
         profit += PositionGetDouble(POSITION_SWAP);
      }
   }

   return profit;
}

//+------------------------------------------------------------------+
//| GRID PROFIT ONLY                                                 |
//+------------------------------------------------------------------+
double GetGridProfit()
{
   double profit = 0.0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(IsGridPosition())
      {
         profit += PositionGetDouble(POSITION_PROFIT);
         profit += PositionGetDouble(POSITION_SWAP);
      }
   }

   return profit;
}

//+------------------------------------------------------------------+
//| COUNT GRID POSITIONS BY TYPE                                     |
//+------------------------------------------------------------------+
int CountGridPositions(int type)
{
   int count = 0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      if((int)PositionGetInteger(POSITION_TYPE) == type)
         count++;
   }

   return count;
}

//+------------------------------------------------------------------+
//| GRID LOTS BY TYPE                                                |
//+------------------------------------------------------------------+
double GridLotsByType(int type)
{
   double lots = 0.0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      if((int)PositionGetInteger(POSITION_TYPE) == type)
         lots += PositionGetDouble(POSITION_VOLUME);
   }

   return lots;
}

//+------------------------------------------------------------------+
//| TOTAL GRID LOTS                                                  |
//+------------------------------------------------------------------+
double TotalGridLots()
{
   return GridLotsByType(POSITION_TYPE_BUY) +
          GridLotsByType(POSITION_TYPE_SELL);
}

//+------------------------------------------------------------------+
//| HEDGE OPEN CHECK                                                 |
//+------------------------------------------------------------------+
bool IsHedgeOpen()
{
   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(IsHedgePosition())
         return true;
   }

   return false;
}

//+------------------------------------------------------------------+
//| GET OUTERMOST GRID PRICE                                         |
//| BUY grid  -> lowest buy price                                    |
//| SELL grid -> highest sell price                                  |
//+------------------------------------------------------------------+
double GetOuterGridPrice(int type)
{
   bool found = false;
   double price = 0.0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      if((int)PositionGetInteger(POSITION_TYPE) != type)
         continue;

      double p = PositionGetDouble(POSITION_PRICE_OPEN);

      if(!found)
      {
         price = p;
         found = true;
      }
      else
      {
         if(type == POSITION_TYPE_BUY && p < price)
            price = p;

         if(type == POSITION_TYPE_SELL && p > price)
            price = p;
      }
   }

   return price;
}

//+------------------------------------------------------------------+
//| SPREAD CHECK                                                     |
//+------------------------------------------------------------------+
bool SpreadOK()
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   double spread = (ask - bid) / _Point;

   if(spread > MaxSpreadPoints)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| MARGIN CHECK                                                     |
//+------------------------------------------------------------------+
bool MarginOK()
{
   double marginLevel = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);

   if(marginLevel <= 0.0)
      return true;

   if(marginLevel < MinMarginLevelPercent)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| BALANCE TARGET CHECK                                             |
//+------------------------------------------------------------------+
bool BalanceTargetReached()
{
   if(AccountInfoDouble(ACCOUNT_BALANCE) >= StopTradingBalance)
      return true;

   return false;
}

//+------------------------------------------------------------------+
//| TRADE COOLDOWN CHECK                                             |
//+------------------------------------------------------------------+
bool CooldownOK()
{
   if(TimeCurrent() - lastTradeTime < TradeCooldownSeconds)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| PAUSE CHECK                                                      |
//+------------------------------------------------------------------+
bool IsPaused()
{
   if(PauseTradingUntil > 0 && TimeCurrent() < PauseTradingUntil)
      return true;

   return false;
}

//+------------------------------------------------------------------+
//| CAN OPEN NORMAL GRID / FIRST TRADE                               |
//+------------------------------------------------------------------+
bool CanOpenNormalTrade()
{
   if(BalanceTargetReached())
      return false;

   if(IsPaused())
      return false;

   if(!SpreadOK())
      return false;

   if(!MarginOK())
      return false;

   if(!CooldownOK())
      return false;

   if(TotalGridLots() >= MaxGridLots)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| CAN OPEN HEDGE                                                   |
//+------------------------------------------------------------------+
bool CanOpenHedge()
{
   if(BalanceTargetReached())
      return false;

   if(IsPaused() && !AllowHedgeDuringPause)
      return false;

   if(!SpreadOK())
      return false;

   if(!MarginOK())
      return false;

   if(!CooldownOK())
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| PRICE SHOCK GUARD - PRICE ONLY                                   |
//+------------------------------------------------------------------+
void UpdatePriceShockGuard()
{
   if(!EnablePriceShockGuard)
      return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double mid = (ask + bid) * 0.5;

   datetime now = TimeCurrent();

   if(shockWindowStart == 0)
   {
      shockWindowStart = now;
      shockWindowPrice = mid;
      return;
   }

   int elapsed = (int)(now - shockWindowStart);

   if(elapsed >= ShockWindowSeconds)
   {
      shockWindowStart = now;
      shockWindowPrice = mid;
      return;
   }

   double movePoints = MathAbs(mid - shockWindowPrice) / _Point;

   if(movePoints >= ShockMovePoints)
   {
      PauseTradingUntil = now + PauseAfterShockMinutes * 60;

      shockWindowStart = now;
      shockWindowPrice = mid;

      Print("PRICE SHOCK PAUSE: movePoints=", movePoints,
            " PauseUntil=", TimeToString(PauseTradingUntil));

      SaveState();
   }
}

//+------------------------------------------------------------------+
//| PREPARE HEDGE DIRECTION USING NET GRID LOTS                      |
//+------------------------------------------------------------------+
void PrepareHedge()
{
   double buyLots  = GridLotsByType(POSITION_TYPE_BUY);
   double sellLots = GridLotsByType(POSITION_TYPE_SELL);

   if(buyLots > sellLots)
      hedgeSignalType = ORDER_TYPE_SELL;
   else if(sellLots > buyLots)
      hedgeSignalType = ORDER_TYPE_BUY;
   else
   {
      if(currentDirection == 0)
         hedgeSignalType = ORDER_TYPE_SELL;
      else
         hedgeSignalType = ORDER_TYPE_BUY;
   }
}

//+------------------------------------------------------------------+
//| CALCULATE DYNAMIC HEDGE LOT                                      |
//+------------------------------------------------------------------+
double GetDynamicHedgeLot()
{
   double buyLots  = GridLotsByType(POSITION_TYPE_BUY);
   double sellLots = GridLotsByType(POSITION_TYPE_SELL);

   double netLots = MathAbs(buyLots - sellLots);

   if(netLots <= 0.0)
      netLots = TotalGridLots();

   double hedgeLot = netLots * HedgeCoverageRatio;

   if(hedgeLot < MinHedgeLot)
      hedgeLot = MinHedgeLot;

   if(hedgeLot > MaxHedgeLot)
      hedgeLot = MaxHedgeLot;

   return NormalizeLot(hedgeLot);
}

//+------------------------------------------------------------------+
//| OPEN AUTO HEDGE                                                  |
//+------------------------------------------------------------------+
void OpenAutoHedge()
{
   if(IsHedgeOpen())
      return;

   if(!CanOpenHedge())
      return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(hedgeLossMode)
   {
      if(hedgeSignalType == ORDER_TYPE_BUY && ask < lastHedgeOpenPrice)
         return;

      if(hedgeSignalType == ORDER_TYPE_SELL && bid > lastHedgeOpenPrice)
         return;
   }

   double hedgeLot = GetDynamicHedgeLot();

   bool result = false;
   hedgePeakProfit = 0.0;

   if(hedgeSignalType == ORDER_TYPE_BUY)
   {
      result = trade.Buy(
         hedgeLot,
         _Symbol,
         ask,
         0,
         0,
         "HEDGE"
      );

      if(result)
      {
         lastHedgeOpenPrice = ask;
         lastTradeTime = TimeCurrent();

         Print("HEDGE BUY opened. Lot=", hedgeLot,
               " Price=", ask);
      }
      else
      {
         Print("HEDGE BUY failed. Retcode=",
               trade.ResultRetcode(),
               " ",
               trade.ResultRetcodeDescription());
      }
   }
   else
   {
      result = trade.Sell(
         hedgeLot,
         _Symbol,
         bid,
         0,
         0,
         "HEDGE"
      );

      if(result)
      {
         lastHedgeOpenPrice = bid;
         lastTradeTime = TimeCurrent();

         Print("HEDGE SELL opened. Lot=", hedgeLot,
               " Price=", bid);
      }
      else
      {
         Print("HEDGE SELL failed. Retcode=",
               trade.ResultRetcode(),
               " ",
               trade.ResultRetcodeDescription());
      }
   }

   SaveState();
}

//+------------------------------------------------------------------+
//| CLOSE POSITION AND GET REALIZED P/L                              |
//+------------------------------------------------------------------+
bool ClosePositionAndGetRealized(ulong ticket, double &realizedPL)
{
   realizedPL = 0.0;

   if(!PositionSelectByTicket(ticket))
      return true;

   datetime beforeClose = TimeCurrent() - 10;

   bool result = trade.PositionClose(ticket);

   if(!result)
   {
      Print("PositionClose failed. Ticket=", ticket,
            " Retcode=", trade.ResultRetcode(),
            " ",
            trade.ResultRetcodeDescription());

      return false;
   }

   ulong deal = trade.ResultDeal();

   HistorySelect(beforeClose, TimeCurrent() + 60);

   if(deal > 0 && HistoryDealSelect(deal))
   {
      realizedPL  = HistoryDealGetDouble(deal, DEAL_PROFIT);
      realizedPL += HistoryDealGetDouble(deal, DEAL_SWAP);
      realizedPL += HistoryDealGetDouble(deal, DEAL_COMMISSION);
   }
   else
   {
      Print("Warning: Could not read realized P/L for ticket=", ticket);
   }

   return true;
}

//+------------------------------------------------------------------+
//| MANAGE SMART HEDGE                                               |
//+------------------------------------------------------------------+
void ManageSmartHedge()
{
   double gridFloatingLoss = MathMax(0.0, -GetGridProfit());

   if(!IsHedgeOpen() && gridFloatingLoss >= HedgeTriggerUSD)
   {
      PrepareHedge();
      OpenAutoHedge();
   }

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsHedgePosition())
         continue;

      double profit = PositionGetDouble(POSITION_PROFIT) +
                      PositionGetDouble(POSITION_SWAP);

      if(profit <= -HedgeFixedLossUSD)
      {
         double realized = 0.0;

         if(ClosePositionAndGetRealized(ticket, realized))
         {
            if(realized < 0.0)
            {
               hedgeLossPool += MathAbs(realized);
               hedgeLossMode = true;
            }
            else
            {
               hedgeProfitPool += realized;
               hedgeLossMode = false;
            }

            hedgePeakProfit = 0.0;

            Print("HEDGE closed by fixed loss. Realized=",
                  DoubleToString(realized, 2),
                  " ProfitPool=",
                  DoubleToString(hedgeProfitPool, 2),
                  " LossPool=",
                  DoubleToString(hedgeLossPool, 2));

            SaveState();
         }

         return;
      }

      if(profit > hedgePeakProfit)
      {
         hedgePeakProfit = profit;
         SaveState();
      }

      if(hedgePeakProfit >= HedgeTrailStart)
      {
         double trailLevel = hedgePeakProfit - HedgeTrailStep;

         if(profit <= trailLevel)
         {
            double realized = 0.0;

            if(ClosePositionAndGetRealized(ticket, realized))
            {
               if(realized >= 0.0)
               {
                  hedgeProfitPool += realized;
                  hedgeLossMode = false;
               }
               else
               {
                  hedgeLossPool += MathAbs(realized);
                  hedgeLossMode = true;
               }

               hedgePeakProfit = 0.0;

               Print("HEDGE closed by trailing. Realized=",
                     DoubleToString(realized, 2),
                     " ProfitPool=",
                     DoubleToString(hedgeProfitPool, 2),
                     " LossPool=",
                     DoubleToString(hedgeLossPool, 2));

               SaveState();
            }

            return;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| MANAGE GRID                                                      |
//+------------------------------------------------------------------+
void ManageGrid()
{
   if(IsHedgeOpen())
      return;

   if(!CanOpenNormalTrade())
      return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   double trigger = GridDistancePoints * GridTriggerRatio;

   if(currentDirection == 0)
   {
      int count = CountGridPositions(POSITION_TYPE_BUY);

      if(count >= MaxTrades)
         return;

      double outerPrice = GetOuterGridPrice(POSITION_TYPE_BUY);

      if(outerPrice <= 0.0)
         return;

      double distance = (outerPrice - bid) / _Point;

      if(distance >= trigger)
      {
         double lot = NormalizeLot(LotSize);

         bool result = trade.Buy(
            lot,
            _Symbol,
            ask,
            0,
            0,
            "GridBuy"
         );

         if(result)
         {
            lastTradeTime = TimeCurrent();

            Print("GRID BUY opened. Lot=", lot,
                  " Price=", ask,
                  " Distance=", distance);
         }
         else
         {
            Print("GRID BUY failed. Retcode=",
                  trade.ResultRetcode(),
                  " ",
                  trade.ResultRetcodeDescription());
         }
      }
   }
   else
   {
      int count = CountGridPositions(POSITION_TYPE_SELL);

      if(count >= MaxTrades)
         return;

      double outerPrice = GetOuterGridPrice(POSITION_TYPE_SELL);

      if(outerPrice <= 0.0)
         return;

      double distance = (ask - outerPrice) / _Point;

      if(distance >= trigger)
      {
         double lot = NormalizeLot(LotSize);

         bool result = trade.Sell(
            lot,
            _Symbol,
            bid,
            0,
            0,
            "GridSell"
         );

         if(result)
         {
            lastTradeTime = TimeCurrent();

            Print("GRID SELL opened. Lot=", lot,
                  " Price=", bid,
                  " Distance=", distance);
         }
         else
         {
            Print("GRID SELL failed. Retcode=",
                  trade.ResultRetcode(),
                  " ",
                  trade.ResultRetcodeDescription());
         }
      }
   }
}

//+------------------------------------------------------------------+
//| OPEN FIRST TRADE                                                 |
//+------------------------------------------------------------------+
void OpenFirstTrade()
{
   if(!CanOpenNormalTrade())
      return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(currentDirection == -1)
      currentDirection = 0;

   double lot = NormalizeLot(LotSize);

   bool result = false;

   if(currentDirection == 0)
   {
      result = trade.Buy(
         lot,
         _Symbol,
         ask,
         0,
         0,
         "GridBuy"
      );

      if(result)
         Print("FIRST GRID BUY opened. Lot=", lot, " Price=", ask);
   }
   else
   {
      result = trade.Sell(
         lot,
         _Symbol,
         bid,
         0,
         0,
         "GridSell"
      );

      if(result)
         Print("FIRST GRID SELL opened. Lot=", lot, " Price=", bid);
   }

   if(result)
   {
      lastTradeTime = TimeCurrent();
      SaveState();
   }
   else
   {
      Print("FIRST TRADE failed. Retcode=",
            trade.ResultRetcode(),
            " ",
            trade.ResultRetcodeDescription());
   }
}

//+------------------------------------------------------------------+
//| REQUEST CLOSE ALL                                                |
//+------------------------------------------------------------------+
void RequestCloseAll(bool lossClose)
{
   closeAllPending = true;
   closeAfterLoss  = lossClose;
}

//+------------------------------------------------------------------+
//| PROCESS CLOSE ALL SAFELY                                         |
//+------------------------------------------------------------------+
bool ProcessCloseAll()
{
   bool allCloseRequestsOK = true;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsOurPosition())
         continue;

      bool result = trade.PositionClose(ticket);

      if(!result)
      {
         allCloseRequestsOK = false;

         Print("CloseAll failed. Ticket=", ticket,
               " Retcode=", trade.ResultRetcode(),
               " ",
               trade.ResultRetcodeDescription());
      }
   }

   if(TotalOurPositions() == 0)
   {
      if(currentDirection == 0)
         currentDirection = 1;
      else
         currentDirection = 0;

      ResetEngine();

      if(closeAfterLoss)
      {
         PauseTradingUntil = TimeCurrent() + RestartAfterHours * 3600;
         SaveState();

         Print("Basket loss close completed. Trading paused until ",
               TimeToString(PauseTradingUntil));
      }
      else
      {
         Print("Basket close completed. New direction=",
               currentDirection == 0 ? "BUY" : "SELL");
      }

      closeAllPending = false;
      closeAfterLoss  = false;

      return true;
   }

   if(!allCloseRequestsOK)
      Print("CloseAll still pending. Remaining positions=", TotalOurPositions());

   return false;
}

//+------------------------------------------------------------------+
//| DASHBOARD                                                        |
//+------------------------------------------------------------------+
void ShowDashboard()
{
   double totalFloating = GetTotalProfit();

   double netRecovery = totalFloating +
                        hedgeProfitPool -
                        hedgeLossPool;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = (ask - bid) / _Point;

   Comment(
      "AUTO GRID + HEDGE RECOVERY - PRICE ONLY\n",
      "Symbol: ", _Symbol,
      "\nDirection: ", currentDirection == 0 ? "BUY GRID" : "SELL GRID",
      "\nPositions: ", TotalOurPositions(),
      "\nGrid Positions: ", TotalGridPositions(),
      "\nGrid Lots: ", DoubleToString(TotalGridLots(), 2),
      "\nHedge Open: ", IsHedgeOpen() ? "YES" : "NO",
      "\nFloating P/L: ", DoubleToString(totalFloating, 2),
      "\nGrid Floating P/L: ", DoubleToString(GetGridProfit(), 2),
      "\nHedge Profit Pool: ", DoubleToString(hedgeProfitPool, 2),
      "\nHedge Loss Pool: ", DoubleToString(hedgeLossPool, 2),
      "\nNet Recovery: ", DoubleToString(netRecovery, 2),
      "\nBasket Target: ", DoubleToString(BasketProfit, 2),
      "\nBasket Loss Limit: ", DoubleToString(BasketLossLimit, 2),
      "\nSpread Points: ", DoubleToString(spread, 1),
      "\nPaused: ", IsPaused() ? "YES" : "NO",
      "\nPause Until: ", TimeToString(PauseTradingUntil),
      "\nCloseAll Pending: ", closeAllPending ? "YES" : "NO"
   );
}

//+------------------------------------------------------------------+
//| ON TICK                                                          |
//+------------------------------------------------------------------+
void OnTick()
{
   UpdatePriceShockGuard();

   if(closeAllPending)
   {
      ProcessCloseAll();
      ShowDashboard();
      return;
   }

   if(BalanceTargetReached())
   {
      if(TotalOurPositions() > 0)
      {
         RequestCloseAll(false);
         ProcessCloseAll();
      }

      Comment(
         "TRADING STOPPED\n",
         "Balance target reached: ",
         DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2)
      );

      return;
   }

   if(TotalOurPositions() == 0)
   {
      if(IsPaused())
      {
         Comment(
            "TRADING PAUSED\n",
            "Restart At: ",
            TimeToString(PauseTradingUntil)
         );

         return;
      }

      OpenFirstTrade();
      ShowDashboard();
      return;
   }

   ManageSmartHedge();

   ManageGrid();

   double totalFloating = GetTotalProfit();

   double netRecovery = totalFloating +
                        hedgeProfitPool -
                        hedgeLossPool;

   if(hedgeProfitPool == 0.0 && hedgeLossPool == 0.0)
   {
      if(totalFloating >= BasketProfit + CloseBufferUSD)
      {
         RequestCloseAll(false);
         ProcessCloseAll();
         ShowDashboard();
         return;
      }
   }
   else
   {
      if(netRecovery >= BasketProfit + CloseBufferUSD)
      {
         RequestCloseAll(false);
         ProcessCloseAll();
         ShowDashboard();
         return;
      }
   }

   if(netRecovery <= BasketLossLimit)
   {
      RequestCloseAll(true);
      ProcessCloseAll();
      ShowDashboard();
      return;
   }

   ShowDashboard();
}
//+------------------------------------------------------------------+
