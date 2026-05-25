//+------------------------------------------------------------------+
//| AUTO GRID + AUTO HEDGE RECOVERY ENGINE                          |
//+------------------------------------------------------------------+
#property strict

#include <Trade/Trade.mqh>
CTrade trade;

//================ INPUTS =================//
input double LotSize              = 0.01;
input int    GridDistancePoints   = 100;
input int    MaxTrades            = 50;

input double BasketProfit         = 10.0;
input double BasketLossLimit      = -100.0;

input int    RestartAfterHours    = 2;

input double HedgeTriggerUSD      = 100.0;
input double HedgeLotSize         = 0.05;

input double HedgeFixedLossUSD    = 100.0;

input double HedgeTrailStart      = 40.0;
input double HedgeTrailStep       = 25.0;

input double StopTradingBalance   = 100000.0;

//================ GLOBALS =================//
int currentDirection = -1;

double hedgeProfitPool = 0;
double hedgeLossPool   = 0;

double hedgePeakProfit = 0;

ENUM_ORDER_TYPE hedgeSignalType;

datetime PauseTradingUntil = 0;

double lastHedgeOpenPrice = 0;
bool hedgeLossMode = false;

//+------------------------------------------------------------------+
//| INIT                                                             |
//+------------------------------------------------------------------+
int OnInit()
{
   PauseTradingUntil = 0;
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| RESET ENGINE                                                     |
//+------------------------------------------------------------------+
void ResetEngine()
{
   hedgeProfitPool = 0;
   hedgeLossPool   = 0;

   hedgePeakProfit = 0;

   hedgeLossMode = false;

   lastHedgeOpenPrice = 0;
}

//+------------------------------------------------------------------+
//| ALLOW TRADING                                                    |
//+------------------------------------------------------------------+
bool AllowTrading()
{
   return(
      AccountInfoDouble(ACCOUNT_BALANCE)
      < StopTradingBalance
   );
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

   lot = MathFloor(lot/step)*step;

   return NormalizeDouble(lot,2);
}

//+------------------------------------------------------------------+
//| TOTAL POSITIONS                                                  |
//+------------------------------------------------------------------+
int TotalSymbolPositions()
{
   int count = 0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetString(POSITION_SYMBOL)==_Symbol)
            count++;
      }
   }

   return count;
}

//+------------------------------------------------------------------+
//| TOTAL FLOATING                                                   |
//+------------------------------------------------------------------+
double GetTotalProfit()
{
   double profit = 0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket = PositionGetTicket(i);

      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetString(POSITION_SYMBOL)==_Symbol)
         {
            profit +=
            PositionGetDouble(POSITION_PROFIT);
         }
      }
   }

   return profit;
}

//+------------------------------------------------------------------+
//| COUNT POSITIONS                                                  |
//+------------------------------------------------------------------+
int CountPositions(int type)
{
   int count=0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket=PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(PositionGetString(POSITION_SYMBOL)!=_Symbol)
         continue;

      if(PositionGetInteger(POSITION_TYPE)==type)
         count++;
   }

   return count;
}

//+------------------------------------------------------------------+
//| LAST GRID PRICE                                                  |
//+------------------------------------------------------------------+
double GetLastGridPrice(int type)
{
   datetime lastTime=0;
   double price=0;

   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket=PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(PositionGetString(POSITION_SYMBOL)!=_Symbol)
         continue;

      if(PositionGetString(POSITION_COMMENT)=="HEDGE")
         continue;

      if(PositionGetInteger(POSITION_TYPE)!=type)
         continue;

      datetime t=
      (datetime)PositionGetInteger(POSITION_TIME);

      if(t > lastTime)
      {
         lastTime=t;

         price=
         PositionGetDouble(POSITION_PRICE_OPEN);
      }
   }

   return price;
}

//+------------------------------------------------------------------+
//| HEDGE OPEN CHECK                                                 |
//+------------------------------------------------------------------+
bool IsHedgeOpen()
{
   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket=PositionGetTicket(i);

      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetString(POSITION_COMMENT)
            =="HEDGE")
            return true;
      }
   }

   return false;
}

//+------------------------------------------------------------------+
//| PREPARE HEDGE                                                    |
//+------------------------------------------------------------------+
void PrepareHedge()
{
   int buyCount=
   CountPositions(POSITION_TYPE_BUY);

   int sellCount=
   CountPositions(POSITION_TYPE_SELL);

   if(sellCount > buyCount)
      hedgeSignalType = ORDER_TYPE_BUY;
   else
      hedgeSignalType = ORDER_TYPE_SELL;
}

//+------------------------------------------------------------------+
//| OPEN AUTO HEDGE                                                  |
//+------------------------------------------------------------------+
void OpenAutoHedge()
{
   if(IsHedgeOpen())
      return;

   double ask=
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid=
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   //=====================================
   // LOSS MODE FILTER
   //=====================================

   if(hedgeLossMode)
   {
      // BUY retry
      if(hedgeSignalType==ORDER_TYPE_BUY
         && ask < lastHedgeOpenPrice)
         return;

      // SELL retry
      if(hedgeSignalType==ORDER_TYPE_SELL
         && bid > lastHedgeOpenPrice)
         return;
   }

   bool result=false;

   hedgePeakProfit=0;

   // BUY HEDGE
   if(hedgeSignalType==ORDER_TYPE_BUY)
   {
      result=
      trade.Buy(
         NormalizeLot(HedgeLotSize),
         _Symbol,
         ask,
         0,
         0,
         "HEDGE"
      );

      if(result)
         lastHedgeOpenPrice=ask;
   }

   // SELL HEDGE
   else
   {
      result=
      trade.Sell(
         NormalizeLot(HedgeLotSize),
         _Symbol,
         bid,
         0,
         0,
         "HEDGE"
      );

      if(result)
         lastHedgeOpenPrice=bid;
   }
}

//+------------------------------------------------------------------+
//| CLOSE ALL                                                        |
//+------------------------------------------------------------------+
void CloseAll()
{
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);

      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetString(POSITION_SYMBOL)
            ==_Symbol)
         {
            trade.PositionClose(ticket);
         }
      }
   }

   // SWITCH DIRECTION
   if(currentDirection==0)
      currentDirection=1;
   else
      currentDirection=0;

   ResetEngine();
}

//+------------------------------------------------------------------+
//| MANAGE HEDGE                                                     |
//+------------------------------------------------------------------+
void ManageSmartHedge()
{
   double floatingLoss=
   MathMax(0,-GetTotalProfit());

   //=====================================
   // OPEN HEDGE
   //=====================================

   if(!IsHedgeOpen()
      && floatingLoss >= HedgeTriggerUSD)
   {
      PrepareHedge();

      OpenAutoHedge();
   }

   //=====================================
   // MANAGE ACTIVE HEDGE
   //=====================================

   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=
      PositionGetTicket(i);

      if(!PositionSelectByTicket(ticket))
         continue;

      if(PositionGetString(POSITION_COMMENT)
         != "HEDGE")
         continue;

      double profit=
      PositionGetDouble(POSITION_PROFIT);

      //=====================================
      // FIXED HEDGE LOSS
      //=====================================

      if(profit <= -HedgeFixedLossUSD)
      {
         hedgeLossPool +=
         MathAbs(profit);

         hedgeLossMode = true;

         trade.PositionClose(ticket);

         hedgePeakProfit=0;

         return;
      }

      //=====================================
      // TRACK PEAK
      //=====================================

      if(profit > hedgePeakProfit)
         hedgePeakProfit=profit;

      //=====================================
      // TRAILING CLOSE
      //=====================================

      if(hedgePeakProfit >= HedgeTrailStart)
      {
         double trailLevel=
         hedgePeakProfit
         - HedgeTrailStep;

         if(profit <= trailLevel)
         {
            hedgeProfitPool += profit;

            hedgeLossMode = false;

            trade.PositionClose(ticket);

            hedgePeakProfit=0;

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
   // STOP GRID DURING HEDGE
   if(IsHedgeOpen())
      return;

   double ask=
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid=
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   double trigger=
   GridDistancePoints * 0.9;

   // BUY GRID
   if(currentDirection==0)
   {
      int count=
      CountPositions(POSITION_TYPE_BUY);

      if(count < MaxTrades)
      {
         double last=
         GetLastGridPrice(
            POSITION_TYPE_BUY
         );

         double distance=
         (last-bid)/_Point;

         if(distance >= trigger)
         {
            trade.Buy(
               LotSize,
               _Symbol,
               ask,
               0,
               0,
               "GridBuy"
            );
         }
      }
   }

   // SELL GRID
   else
   {
      int count=
      CountPositions(POSITION_TYPE_SELL);

      if(count < MaxTrades)
      {
         double last=
         GetLastGridPrice(
            POSITION_TYPE_SELL
         );

         double distance=
         (ask-last)/_Point;

         if(distance >= trigger)
         {
            trade.Sell(
               LotSize,
               _Symbol,
               bid,
               0,
               0,
               "GridSell"
            );
         }
      }
   }
}

//+------------------------------------------------------------------+
//| OPEN FIRST TRADE                                                 |
//+------------------------------------------------------------------+
void OpenFirstTrade()
{
   double ask=
   SymbolInfoDouble(_Symbol,SYMBOL_ASK);

   double bid=
   SymbolInfoDouble(_Symbol,SYMBOL_BID);

   if(currentDirection==-1)
      currentDirection=0;

   if(currentDirection==0)
   {
      trade.Buy(
         LotSize,
         _Symbol,
         ask,
         0,
         0,
         "GridBuy"
      );
   }
   else
   {
      trade.Sell(
         LotSize,
         _Symbol,
         bid,
         0,
         0,
         "GridSell"
      );
   }
}

//+------------------------------------------------------------------+
//| ON TICK                                                          |
//+------------------------------------------------------------------+
void OnTick()
{
   //=====================================
   // PAUSE MODE
   //=====================================

   if(PauseTradingUntil > 0 &&
      TimeCurrent() < PauseTradingUntil)
   {
      Comment(
         "TRADING PAUSED\n",
         "Restart At: ",
         TimeToString(PauseTradingUntil)
      );

      return;
   }

   //=====================================
   // STOP TRADING
   //=====================================

   if(!AllowTrading())
   {
      Comment(
         "TRADING STOPPED\n",
         "Balance Target Reached"
      );

      return;
   }

   //=====================================
   // START FIRST TRADE
   //=====================================

   if(TotalSymbolPositions()==0)
   {
      ResetEngine();

      OpenFirstTrade();

      return;
   }

   //=====================================
   // MANAGE HEDGE
   //=====================================

   ManageSmartHedge();

   //=====================================
   // MANAGE GRID
   //=====================================

   ManageGrid();

   //=====================================
   // FINAL RECOVERY
   //=====================================

   double totalFloating=
   GetTotalProfit();

   double netRecovery=
   totalFloating
   + hedgeProfitPool
   - hedgeLossPool;

   //=====================================
   // NORMAL BASKET CLOSE
   //=====================================

   if(
      hedgeProfitPool == 0
      &&
      hedgeLossPool == 0
   )
   {
      if(totalFloating >= BasketProfit)
      {
         CloseAll();
         return;
      }
   }

   //=====================================
   // RECOVERY CLOSE
   //=====================================

   else
   {
      if(netRecovery >= BasketProfit)
      {
         CloseAll();
         return;
      }
   }

   //=====================================
   // MAX LOSS STOP
   //=====================================

   if(netRecovery <= BasketLossLimit)
   {
      CloseAll();

      PauseTradingUntil=
      TimeCurrent()
      + (RestartAfterHours * 3600);

      return;
   }

   //=====================================
   // DASHBOARD
   //=====================================

   Comment(
      "Floating P/L: ",
      DoubleToString(totalFloating,2),

      "\nHedge Profit Pool: ",
      DoubleToString(hedgeProfitPool,2),

      "\nHedge Loss Pool: ",
      DoubleToString(hedgeLossPool,2),

      "\nNet Recovery: ",
      DoubleToString(netRecovery,2),

      "\nBasket Profit Target: ",
      DoubleToString(BasketProfit,2),

      "\nBasket Loss Limit: ",
      DoubleToString(BasketLossLimit,2),

      "\nPause Until: ",
      TimeToString(PauseTradingUntil)
   );
}
//+------------------------------------------------------------------+
