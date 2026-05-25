//+------------------------------------------------------------------+
//|        XAUUSD GRID + SMART DYNAMIC HEDGE ENGINE                  |
//|                PRICE ACTION ONLY - NO INDICATORS                 |
//|                      Hardened Production EA                      |
//+------------------------------------------------------------------+
#property strict

#include <Trade/Trade.mqh>
CTrade trade;

//========================= INPUTS ==================================//

input ulong  MagicNumber              = 26052501;

//---------------- GRID ----------------//

input double LotSize                  = 0.02;
input int    GridDistancePoints       = 200;
input int    MaxTrades                = 50;

//---------------- BASKET --------------//

input double BasketProfit             = 10.0;
input double BasketLossLimit          = -320.0;

input int    RestartAfterHours        = 2;

//---------------- HEDGE ---------------//

input double HedgeTriggerUSD          = 150.0;

input double HedgeCoverageRatio       = 0.45;
input double HedgeLossBoostFactor     = 0.12;

input double MinHedgeLot              = 0.02;
input double MaxHedgeLot              = 1.00;

input double HedgeFixedLossUSD        = 75.0;

input double HedgeTrailStart          = 25.0;
input double HedgeTrailStep           = 10.0;

input int    HedgeMinimumLifeSeconds  = 45;

//---------------- SAFETY --------------//

input double StopTradingBalance       = 1100.0;

input int    MaxSpreadPoints          = 80;

input double MinMarginLevel           = 250.0;

input int    TradeCooldownSeconds     = 3;

//---------------- SHOCK FILTER --------//

input bool   EnableShockProtection    = true;

input int    ShockMovePoints          = 600;

input int    ShockTimeWindowSeconds   = 60;

input int    ShockPauseMinutes        = 30;

//========================= GLOBALS =================================//

// -1 = not initialized
//  0 = BUY GRID
//  1 = SELL GRID

int currentDirection = -1;

double hedgeProfitPool = 0.0;
double hedgeLossPool   = 0.0;

double hedgePeakProfit = 0.0;

bool hedgeLossMode = false;

ENUM_ORDER_TYPE hedgeSignalType;

datetime PauseTradingUntil = 0;

double lastHedgeOpenPrice = 0.0;

datetime lastTradeTime = 0;

bool closeAllPending = false;
bool closeAfterLoss  = false;

datetime hedgeOpenTime = 0;

datetime shockStartTime = 0;
double   shockStartPrice = 0.0;

//+------------------------------------------------------------------+
//| INIT                                                             |
//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(MagicNumber);

   trade.SetDeviationInPoints(20);

   trade.SetTypeFillingBySymbol(_Symbol);

   double ask =
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid =
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   shockStartPrice =
   (ask + bid) * 0.5;

   shockStartTime =
   TimeCurrent();

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| NORMALIZE LOT                                                    |
//+------------------------------------------------------------------+
double NormalizeLot(double lot)
{
   double minLot =
   SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);

   double maxLot =
   SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);

   double step =
   SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);

   if(lot < minLot)
      lot = minLot;

   if(lot > maxLot)
      lot = maxLot;

   lot =
   MathFloor(lot / step) * step;

   return NormalizeDouble(lot,2);
}

//+------------------------------------------------------------------+
//| IS OUR POSITION                                                  |
//+------------------------------------------------------------------+
bool IsOurPosition()
{
   if(PositionGetString(POSITION_SYMBOL)
      != _Symbol)
      return false;

   if((ulong)PositionGetInteger(POSITION_MAGIC)
      != MagicNumber)
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

   string c =
   PositionGetString(POSITION_COMMENT);

   if(c == "GridBuy"
      || c == "GridSell")
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

   if(PositionGetString(POSITION_COMMENT)
      == "HEDGE")
      return true;

   return false;
}

//+------------------------------------------------------------------+
//| SPREAD CHECK                                                     |
//+------------------------------------------------------------------+
bool SpreadOK()
{
   double ask =
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid =
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   double spread =
   (ask - bid) / _Point;

   if(spread > MaxSpreadPoints)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| MARGIN CHECK                                                     |
//+------------------------------------------------------------------+
bool MarginOK()
{
   double ml =
   AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);

   if(ml <= 0)
      return true;

   if(ml < MinMarginLevel)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| ALLOW TRADING                                                    |
//+------------------------------------------------------------------+
bool AllowTrading()
{
   if(AccountInfoDouble(ACCOUNT_BALANCE)
      >= StopTradingBalance)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| COOLDOWN CHECK                                                   |
//+------------------------------------------------------------------+
bool CooldownOK()
{
   if(TimeCurrent() - lastTradeTime
      < TradeCooldownSeconds)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| TOTAL OUR POSITIONS                                              |
//+------------------------------------------------------------------+
int TotalOurPositions()
{
   int count = 0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(IsOurPosition())
         count++;
   }

   return count;
}

//+------------------------------------------------------------------+
//| TOTAL GRID LOTS                                                  |
//+------------------------------------------------------------------+
double TotalGridLots()
{
   double lots = 0.0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      lots +=
      PositionGetDouble(POSITION_VOLUME);
   }

   return lots;
}

//+------------------------------------------------------------------+
//| COUNT GRID POSITIONS                                             |
//+------------------------------------------------------------------+
int CountGridPositions(int type)
{
   int count = 0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      if(PositionGetInteger(POSITION_TYPE)
         == type)
         count++;
   }

   return count;
}

//+------------------------------------------------------------------+
//| TOTAL GRID PROFIT                                                |
//+------------------------------------------------------------------+
double GetGridProfit()
{
   double profit = 0.0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      profit +=
      PositionGetDouble(POSITION_PROFIT);

      profit +=
      PositionGetDouble(POSITION_SWAP);
   }

   return profit;
}

//+------------------------------------------------------------------+
//| TOTAL PROFIT                                                     |
//+------------------------------------------------------------------+
double GetTotalProfit()
{
   double profit = 0.0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsOurPosition())
         continue;

      profit +=
      PositionGetDouble(POSITION_PROFIT);

      profit +=
      PositionGetDouble(POSITION_SWAP);
   }

   return profit;
}

//+------------------------------------------------------------------+
//| HEDGE OPEN CHECK                                                 |
//+------------------------------------------------------------------+
bool IsHedgeOpen()
{
   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(IsHedgePosition())
         return true;
   }

   return false;
}

//+------------------------------------------------------------------+
//| OUTERMOST GRID PRICE                                             |
//+------------------------------------------------------------------+
double GetOuterGridPrice(int type)
{
   bool found = false;

   double price = 0.0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      if(PositionGetInteger(POSITION_TYPE)
         != type)
         continue;

      double p =
      PositionGetDouble(POSITION_PRICE_OPEN);

      if(!found)
      {
         found = true;
         price = p;
      }
      else
      {
         if(type == POSITION_TYPE_BUY
            && p < price)
            price = p;

         if(type == POSITION_TYPE_SELL
            && p > price)
            price = p;
      }
   }

   return price;
}

//+------------------------------------------------------------------+
//| RESET ENGINE                                                     |
//+------------------------------------------------------------------+
void ResetEngine()
{
   hedgeProfitPool = 0.0;

   hedgeLossPool = 0.0;

   hedgePeakProfit = 0.0;

   hedgeLossMode = false;

   lastHedgeOpenPrice = 0.0;

   hedgeOpenTime = 0;
}

//+------------------------------------------------------------------+
//| PRICE SHOCK PROTECTION                                           |
//+------------------------------------------------------------------+
void CheckPriceShock()
{
   if(!EnableShockProtection)
      return;

   double ask =
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid =
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   double mid =
   (ask + bid) * 0.5;

   datetime now =
   TimeCurrent();

   int elapsed =
   (int)(now - shockStartTime);

   if(elapsed >= ShockTimeWindowSeconds)
   {
      shockStartTime = now;
      shockStartPrice = mid;
      return;
   }

   double move =
   MathAbs(mid - shockStartPrice)
   / _Point;

   if(move >= ShockMovePoints)
   {
      PauseTradingUntil =
      now + ShockPauseMinutes * 60;

      Print(
         "PRICE SHOCK DETECTED. ",
         "Trading paused."
      );

      shockStartTime = now;
      shockStartPrice = mid;
   }
}

//+------------------------------------------------------------------+
//| PREPARE HEDGE                                                    |
//+------------------------------------------------------------------+
void PrepareHedge()
{
   double buyLots = 0.0;
   double sellLots = 0.0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      double lot =
      PositionGetDouble(POSITION_VOLUME);

      if(PositionGetInteger(POSITION_TYPE)
         == POSITION_TYPE_BUY)
      {
         buyLots += lot;
      }
      else
      {
         sellLots += lot;
      }
   }

   if(buyLots > sellLots)
      hedgeSignalType = ORDER_TYPE_SELL;
   else
      hedgeSignalType = ORDER_TYPE_BUY;
}

//+------------------------------------------------------------------+
//| DYNAMIC HEDGE LOT                                                |
//+------------------------------------------------------------------+
double GetDynamicHedgeLot()
{
   double buyLots = 0.0;
   double sellLots = 0.0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsGridPosition())
         continue;

      double lot =
      PositionGetDouble(POSITION_VOLUME);

      if(PositionGetInteger(POSITION_TYPE)
         == POSITION_TYPE_BUY)
      {
         buyLots += lot;
      }
      else
      {
         sellLots += lot;
      }
   }

   double netLots =
   MathAbs(buyLots - sellLots);

   if(netLots <= 0.0)
      netLots = buyLots + sellLots;

   double hedgeLot =
   netLots * HedgeCoverageRatio;

   double gridLoss =
   MathMax(0,-GetGridProfit());

   if(gridLoss > HedgeTriggerUSD)
   {
      double multiplier =
      gridLoss / HedgeTriggerUSD;

      double boost =
      multiplier * HedgeLossBoostFactor;

      hedgeLot =
      hedgeLot * (1.0 + boost);
   }

   if(hedgeLot < MinHedgeLot)
      hedgeLot = MinHedgeLot;

   if(hedgeLot > MaxHedgeLot)
      hedgeLot = MaxHedgeLot;

   hedgeLot =
   NormalizeLot(hedgeLot);

   return hedgeLot;
}

//+------------------------------------------------------------------+
//| OPEN AUTO HEDGE                                                  |
//+------------------------------------------------------------------+
void OpenAutoHedge()
{
   if(IsHedgeOpen())
      return;

   if(!SpreadOK())
      return;

   if(!MarginOK())
      return;

   if(!CooldownOK())
      return;

   double ask =
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid =
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   if(hedgeLossMode)
   {
      if(hedgeSignalType
         == ORDER_TYPE_BUY
         && ask < lastHedgeOpenPrice)
         return;

      if(hedgeSignalType
         == ORDER_TYPE_SELL
         && bid > lastHedgeOpenPrice)
         return;
   }

   bool result = false;

   hedgePeakProfit = 0.0;

   double hedgeLot =
   GetDynamicHedgeLot();

   //================ BUY HEDGE =================//

   if(hedgeSignalType == ORDER_TYPE_BUY)
   {
      result =
      trade.Buy(
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

         hedgeOpenTime =
         TimeCurrent();

         Print(
            "BUY HEDGE OPENED | Lot=",
            hedgeLot,
            " | Price=",
            ask
         );
      }
   }

   //================ SELL HEDGE ================//

   else
   {
      result =
      trade.Sell(
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

         hedgeOpenTime =
         TimeCurrent();

         Print(
            "SELL HEDGE OPENED | Lot=",
            hedgeLot,
            " | Price=",
            bid
         );
      }
   }

   if(result)
      lastTradeTime = TimeCurrent();
}

//+------------------------------------------------------------------+
//| CLOSE POSITION + REALIZED PL                                     |
//+------------------------------------------------------------------+
bool ClosePositionGetPL(
   ulong ticket,
   double &realizedPL
)
{
   realizedPL = 0.0;

   bool result =
   trade.PositionClose(ticket);

   if(!result)
      return false;

   ulong deal =
   trade.ResultDeal();

   if(deal > 0
      && HistoryDealSelect(deal))
   {
      realizedPL =
      HistoryDealGetDouble(
         deal,
         DEAL_PROFIT
      );

      realizedPL +=
      HistoryDealGetDouble(
         deal,
         DEAL_SWAP
      );

      realizedPL +=
      HistoryDealGetDouble(
         deal,
         DEAL_COMMISSION
      );
   }

   return true;
}

//+------------------------------------------------------------------+
//| MANAGE SMART HEDGE                                               |
//+------------------------------------------------------------------+
void ManageSmartHedge()
{
   double gridLoss =
   MathMax(0,-GetGridProfit());

   //================ OPEN HEDGE =================//

   if(!IsHedgeOpen()
      && gridLoss >= HedgeTriggerUSD)
   {
      PrepareHedge();

      OpenAutoHedge();
   }

   //================ MANAGE ACTIVE HEDGE =======//

   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsHedgePosition())
         continue;

      double profit =
      PositionGetDouble(POSITION_PROFIT);

      //============ FIXED LOSS =================//

      if(profit <= -HedgeFixedLossUSD)
      {
         double realized = 0.0;

         if(ClosePositionGetPL(ticket,realized))
         {
            hedgeLossPool +=
            MathAbs(realized);

            hedgeLossMode = true;

            hedgePeakProfit = 0.0;
         }

         return;
      }

      //============ TRACK PEAK ================//

      if(profit > hedgePeakProfit)
         hedgePeakProfit = profit;

      //============ MIN LIFE ==================//

      if(TimeCurrent() - hedgeOpenTime
         < HedgeMinimumLifeSeconds)
         return;

      //============ TRAILING ==================//

      if(hedgePeakProfit >= HedgeTrailStart)
      {
         double trailLevel =
         hedgePeakProfit
         - HedgeTrailStep;

         if(profit <= trailLevel)
         {
            double realized = 0.0;

            if(ClosePositionGetPL(ticket,realized))
            {
               hedgeProfitPool += realized;

               hedgeLossMode = false;

               hedgePeakProfit = 0.0;
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

   if(!SpreadOK())
      return;

   if(!MarginOK())
      return;

   if(!CooldownOK())
      return;

   double ask =
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid =
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   //================ BUY GRID =================//

   if(currentDirection == 0)
   {
      int count =
      CountGridPositions(
         POSITION_TYPE_BUY
      );

      if(count >= MaxTrades)
         return;

      double outer =
      GetOuterGridPrice(
         POSITION_TYPE_BUY
      );

      double distance =
      (outer - bid) / _Point;

      if(distance >= GridDistancePoints)
      {
         bool result =
         trade.Buy(
            NormalizeLot(LotSize),
            _Symbol,
            ask,
            0,
            0,
            "GridBuy"
         );

         if(result)
            lastTradeTime =
            TimeCurrent();
      }
   }

   //================ SELL GRID ================//

   else
   {
      int count =
      CountGridPositions(
         POSITION_TYPE_SELL
      );

      if(count >= MaxTrades)
         return;

      double outer =
      GetOuterGridPrice(
         POSITION_TYPE_SELL
      );

      double distance =
      (ask - outer) / _Point;

      if(distance >= GridDistancePoints)
      {
         bool result =
         trade.Sell(
            NormalizeLot(LotSize),
            _Symbol,
            bid,
            0,
            0,
            "GridSell"
         );

         if(result)
            lastTradeTime =
            TimeCurrent();
      }
   }
}

//+------------------------------------------------------------------+
//| OPEN FIRST TRADE                                                 |
//+------------------------------------------------------------------+
void OpenFirstTrade()
{
   if(!AllowTrading())
      return;

   if(!SpreadOK())
      return;

   if(!MarginOK())
      return;

   double ask =
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid =
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   if(currentDirection == -1)
      currentDirection = 0;

   bool result = false;

   if(currentDirection == 0)
   {
      result =
      trade.Buy(
         NormalizeLot(LotSize),
         _Symbol,
         ask,
         0,
         0,
         "GridBuy"
      );
   }
   else
   {
      result =
      trade.Sell(
         NormalizeLot(LotSize),
         _Symbol,
         bid,
         0,
         0,
         "GridSell"
      );
   }

   if(result)
      lastTradeTime = TimeCurrent();
}

//+------------------------------------------------------------------+
//| REQUEST CLOSE ALL                                                |
//+------------------------------------------------------------------+
void RequestCloseAll(bool lossMode)
{
   closeAllPending = true;

   closeAfterLoss = lossMode;
}

//+------------------------------------------------------------------+
//| PROCESS CLOSE ALL                                                |
//+------------------------------------------------------------------+
void ProcessCloseAll()
{
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket =
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(!IsOurPosition())
         continue;

      trade.PositionClose(ticket);
   }

   //============ RESET ONLY IF TRULY FLAT ======//

   if(TotalOurPositions() == 0)
   {
      if(currentDirection == 0)
         currentDirection = 1;
      else
         currentDirection = 0;

      ResetEngine();

      if(closeAfterLoss)
      {
         PauseTradingUntil =
         TimeCurrent()
         + (RestartAfterHours * 3600);
      }

      closeAllPending = false;

      closeAfterLoss = false;
   }
}

//+------------------------------------------------------------------+
//| DASHBOARD                                                        |
//+------------------------------------------------------------------+
void Dashboard()
{
   double totalFloating =
   GetTotalProfit();

   double netRecovery =
   totalFloating
   + hedgeProfitPool
   - hedgeLossPool;

   double ask =
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid =
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   double spread =
   (ask - bid) / _Point;

   Comment(
      "XAUUSD GRID + DYNAMIC HEDGE\n",

      "\nDirection: ",
      currentDirection == 0
      ? "BUY GRID"
      : "SELL GRID",

      "\nPositions: ",
      TotalOurPositions(),

      "\nGrid Lots: ",
      DoubleToString(
         TotalGridLots(),2
      ),

      "\nFloating: ",
      DoubleToString(
         totalFloating,2
      ),

      "\nNet Recovery: ",
      DoubleToString(
         netRecovery,2
      ),

      "\nHedge Profit Pool: ",
      DoubleToString(
         hedgeProfitPool,2
      ),

      "\nHedge Loss Pool: ",
      DoubleToString(
         hedgeLossPool,2
      ),

      "\nDynamic Hedge Lot: ",
      DoubleToString(
         GetDynamicHedgeLot(),2
      ),

      "\nSpread: ",
      DoubleToString(
         spread,1
      ),

      "\nHedge Open: ",
      IsHedgeOpen()
      ? "YES"
      : "NO",

      "\nPaused: ",
      TimeCurrent()
      < PauseTradingUntil
      ? "YES"
      : "NO"
   );
}

//+------------------------------------------------------------------+
//| ON TICK                                                          |
//+------------------------------------------------------------------+
void OnTick()
{
   CheckPriceShock();

   //================ CLOSE PROCESS =================//

   if(closeAllPending)
   {
      ProcessCloseAll();

      Dashboard();

      return;
   }

   //================ PAUSE =========================//

   if(PauseTradingUntil > 0
      && TimeCurrent() < PauseTradingUntil)
   {
      Dashboard();

      return;
   }

   //================ STOP TRADING =================//

   if(!AllowTrading())
   {
      Dashboard();

      return;
   }

   //================ FIRST TRADE ==================//

   if(TotalOurPositions() == 0)
   {
      OpenFirstTrade();

      Dashboard();

      return;
   }

   //================ MANAGE HEDGE =================//

   ManageSmartHedge();

   //================ MANAGE GRID ==================//

   ManageGrid();

   //================ BASKET =======================//

   double totalFloating =
   GetTotalProfit();

   double netRecovery =
   totalFloating
   + hedgeProfitPool
   - hedgeLossPool;

   //============ NORMAL CLOSE ====================//

   if(hedgeProfitPool == 0
      && hedgeLossPool == 0)
   {
      if(totalFloating >= BasketProfit)
      {
         RequestCloseAll(false);
      }
   }

   //============ RECOVERY CLOSE ==================//

   else
   {
      if(netRecovery >= BasketProfit)
      {
         RequestCloseAll(false);
      }
   }

   //============ MAX LOSS ========================//

   if(netRecovery <= BasketLossLimit)
   {
      RequestCloseAll(true);
   }

   Dashboard();
}
//+------------------------------------------------------------------+
