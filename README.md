# XAUUSD Grid Trading Strategies - Complete Guide

## Overview

This folder contains **12 Expert Advisor (EA) variations** for MetaTrader 5, designed for XAUUSD (Gold) trading using grid strategies with optional hedging features.

---

## File Naming Convention

Each file follows the pattern: `{Series}{Number}_{grid-type}_{hedge}_{pooling}_{trailing}.mq5`

| Component | Meaning |
|-----------|---------|
| **A** | Fixed Grid Distance (200 points always) |
| **B** | Incremental Grid Distance (200 × N pattern) |
| **1-2** | No Hedge strategies |
| **3-6** | With Hedge strategies |
| **nohedge/hedge** | Hedge protection enabled or not |
| **nopool/pool** | Profit pooling (tracks hedge profits) |
| **notrail/trail** | Grid trailing stop enabled or not |

---

## Complete File Matrix

| File | Grid Type | Hedge | Profit Pooling | Grid Trailing |
|------|-----------|-------|----------------|---------------|
| A1_fixed_nohedge_notrail | Fixed | No | N/A | No |
| A2_fixed_nohedge_trail | Fixed | No | N/A | Yes |
| A3_fixed_hedge_nopool_notrail | Fixed | Yes | No | No |
| A4_fixed_hedge_nopool_trail | Fixed | Yes | No | Yes |
| A5_fixed_hedge_pool_notrail | Fixed | Yes | Yes | No |
| A6_fixed_hedge_pool_trail | Fixed | Yes | Yes | Yes |
| B1_incr_nohedge_notrail | Incremental | No | N/A | No |
| B2_incr_nohedge_trail | Incremental | No | N/A | Yes |
| B3_incr_hedge_nopool_notrail | Incremental | Yes | No | No |
| B4_incr_hedge_nopool_trail | Incremental | Yes | No | Yes |
| B5_incr_hedge_pool_notrail | Incremental | Yes | Yes | No |
| B6_incr_hedge_pool_trail | Incremental | Yes | Yes | Yes |

---

## Feature Explanations

### 1. Grid Types

#### Fixed Grid (A Series)
- Opens new positions at **fixed intervals** (default: 200 points)
- Example: If first BUY at 2000.00, next at 1998.00, then 1996.00, etc.
- Positions accumulate quickly during strong trends

```
Price Movement (Fixed Grid - 200 pts each):
2000.00 -----> Position 1 (BUY)
1998.00 -----> Position 2 (BUY)  [200 pts drop]
1996.00 -----> Position 3 (BUY)  [200 pts drop]
1994.00 -----> Position 4 (BUY)  [200 pts drop]
```

#### Incremental Grid (B Series)
- Opens new positions at **increasing intervals** (200 × Grid Count)
- Example: 1st gap = 200 pts, 2nd gap = 400 pts, 3rd gap = 600 pts
- Slows down position accumulation as drawdown increases

```
Price Movement (Incremental Grid):
2000.00 -----> Position 1 (BUY)
1998.00 -----> Position 2 (BUY)  [200 pts = 200×1]
1994.00 -----> Position 3 (BUY)  [400 pts = 200×2]
1988.00 -----> Position 4 (BUY)  [600 pts = 200×3]
1980.00 -----> Position 5 (BUY)  [800 pts = 200×4]
```

**Why Incremental is Safer:**
- Fewer positions opened during the same price drop
- More margin available for recovery
- Reduces risk of margin call

---

### 2. Hedging

#### No Hedge (Files 1-2)
- Pure grid trading
- If price moves against you, only options are:
  - Wait for reversal (profit target)
  - Hit stop loss and close all

#### With Hedge (Files 3-6)
- When grid loss reaches trigger (default: $150), opens opposite position
- Hedge protects against continued adverse movement
- Hedge has its own trailing stop and fixed stop loss

```
Example Hedge Scenario:
- Grid BUY positions losing $150
- EA opens SELL hedge (0.4 lot)
- If price drops more: hedge profits, offsets grid loss
- If price rises: hedge closes with small loss, grid recovers
```

**Hedge Management:**
- **Fixed Stop Loss**: Closes hedge if loss exceeds $75
- **Trailing Stop**: Locks in hedge profit (starts at $20, trails by $10)
- **Conditional Re-opening**: If hedge closed with loss, waits for price to return before opening new hedge

---

### 3. Profit Pooling

#### No Pooling (nopool)
- Only tracks hedge LOSSES
- Recovery formula: `Floating P/L - Realized Hedge Losses`
- Hedge profits are "lost" when hedge closes

#### With Pooling (pool)
- Tracks both hedge PROFITS and LOSSES
- Recovery formula: `Floating P/L + Hedge Profits - Hedge Losses`
- More accurate recovery calculation

```
Example Without Pooling:
- Grid floating: -$80
- Hedge 1 closed: +$30 profit (NOT counted)
- Hedge 2 closed: -$50 loss
- Recovery Value: -$80 - $50 = -$130

Example With Pooling:
- Grid floating: -$80
- Hedge 1 closed: +$30 profit (COUNTED)
- Hedge 2 closed: -$50 loss
- Recovery Value: -$80 + $30 - $50 = -$100
```

---

### 4. Grid Trailing Stop

#### No Trailing (notrail)
- Closes basket only when fixed profit target is reached (default: $10)
- May give back profits if price reverses before target

#### With Trailing (trail)
- Tracks peak profit of the basket
- Once peak reaches threshold (default: $20), starts trailing
- Closes if profit drops by step amount (default: $10) from peak

```
Example Trailing Scenario:
- Profit reaches $25 (peak)
- Trail level = $25 - $10 = $15
- If profit drops to $15, close all with $15 profit
- Without trailing, might have waited for $10 and price reversed to -$50
```

**Important:** Grid trailing is DISABLED when hedge triggers. Why?
- After hedge triggers, you need to recover hedge losses
- Fixed target ensures you wait for full recovery
- Trailing might close too early with partial recovery

---

## Flowcharts

### Basic Grid Flow (A1/B1 - Simplest)

```
                    START
                      │
                      ▼
              ┌───────────────┐
              │  Any Positions │
              │    Open?       │
              └───────┬───────┘
                      │
           ┌─────────┴─────────┐
           │ NO                │ YES
           ▼                   ▼
    ┌─────────────┐    ┌─────────────┐
    │ Open First  │    │ Check Profit│
    │   Trade     │    │   Target    │
    └─────────────┘    └──────┬──────┘
                              │
                    ┌─────────┴─────────┐
                    │ >= $10?           │
                    │                   │
              ┌─────┴─────┐       ┌─────┴─────┐
              │ YES       │       │ NO        │
              ▼           │       ▼           │
       ┌──────────┐       │  ┌──────────┐    │
       │Close All │       │  │Check Stop│    │
       │ (Profit) │       │  │  Loss    │    │
       └──────────┘       │  └────┬─────┘    │
                          │       │          │
                          │  ┌────┴────┐     │
                          │  │<= -$150?│     │
                          │  └────┬────┘     │
                          │       │          │
                    ┌─────┴───────┴─────┐    │
                    │ YES               │ NO │
                    ▼                   ▼    │
             ┌──────────┐        ┌──────────┐
             │Close All │        │ Manage   │
             │ (Loss)   │        │  Grid    │
             │ + Pause  │        │          │
             └──────────┘        └──────────┘
```

### Grid with Trailing Flow (A2/B2)

```
                    START
                      │
                      ▼
              ┌───────────────┐
              │  Check Profit │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Update Peak   │
              │ if profit >   │
              │ current peak  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Peak >= $20?  │
              │ (Trail Start) │
              └───────┬───────┘
                      │
           ┌─────────┴─────────┐
           │ NO                │ YES
           ▼                   ▼
    ┌─────────────┐    ┌─────────────┐
    │ Check Fixed │    │Trail Level =│
    │ Target $10  │    │Peak - $10   │
    └─────────────┘    └──────┬──────┘
                              │
                              ▼
                       ┌─────────────┐
                       │Profit <= ?  │
                       │Trail Level  │
                       └──────┬──────┘
                              │
                    ┌─────────┴─────────┐
                    │ YES               │ NO
                    ▼                   ▼
             ┌──────────┐        ┌──────────┐
             │Close All │        │ Continue │
             │ (Profit) │        │ Trading  │
             └──────────┘        └──────────┘
```

### Full Featured Flow (A6/B6)

```
                         START
                           │
                           ▼
                   ┌───────────────┐
                   │  Close All    │──YES──► Process Close
                   │  Pending?     │
                   └───────┬───────┘
                           │ NO
                           ▼
                   ┌───────────────┐
                   │   Paused?     │──YES──► Wait
                   └───────┬───────┘
                           │ NO
                           ▼
                   ┌───────────────┐
                   │  Loss Limit   │──YES──► Manage Hedge Only
                   │  + Hedge Open │
                   └───────┬───────┘
                           │ NO
                           ▼
                   ┌───────────────┐
                   │ No Positions? │──YES──► Open First Trade
                   └───────┬───────┘
                           │ NO
                           ▼
            ┌──────────────────────────────┐
            │  PROFIT POOLING CHECK        │
            │  TrueRecovery = Floating     │
            │  + HedgeProfit - HedgeLoss   │
            └──────────────┬───────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │TrueRecovery   │──YES──► Close All (Profit)
                   │  >= $10?      │
                   └───────┬───────┘
                           │ NO
                           ▼
            ┌──────────────────────────────┐
            │      MANAGE HEDGE            │
            │  - Check if hedge needed     │
            │  - Open if grid loss >= $150 │
            │  - Manage trailing/stop      │
            └──────────────┬───────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ Hedge Open?   │──YES──► Skip Grid, Dashboard
                   └───────┬───────┘
                           │ NO
                           ▼
            ┌──────────────────────────────┐
            │      MANAGE GRID             │
            │  - Check if new position     │
            │    needed (distance check)   │
            │  - Open BUY or SELL grid     │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   GRID TRAILING CHECK        │
            │  (Only if hedge NOT triggered)│
            │  - Update peak profit        │
            │  - Check trail level         │
            └──────────────┬───────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ Grid Loss     │──YES──► Close Grid, Wait Hedge
                   │ <= -$320?     │
                   └───────┬───────┘
                           │ NO
                           ▼
                       Dashboard
```

---

## Hedge Management Flow

```
                    MANAGE HEDGE
                         │
                         ▼
                ┌────────────────┐
                │ Hedge Enabled? │──NO──► Return
                └────────┬───────┘
                         │ YES
                         ▼
                ┌────────────────┐
                │ Hedge Already  │──YES──► Manage Existing
                │    Open?       │
                └────────┬───────┘
                         │ NO
                         ▼
                ┌────────────────┐
                │ Grid Loss >=   │──NO──► Return
                │    $150?       │
                └────────┬───────┘
                         │ YES
                         ▼
                ┌────────────────┐
                │ Last Hedge     │──NO──► Open Hedge
                │ Was Loss?      │
                └────────┬───────┘
                         │ YES
                         ▼
                ┌────────────────┐
                │ Price Returned │──NO──► Wait (Don't Open)
                │ to Last Open?  │
                └────────┬───────┘
                         │ YES
                         ▼
                    Open Hedge
                         │
                         ▼
                ┌────────────────┐
                │ Set Flags:     │
                │ - hedgeTriggered│
                │ - gridFrozen   │
                └────────────────┘


              MANAGE EXISTING HEDGE
                         │
                         ▼
                ┌────────────────┐
                │ Hedge Profit   │──YES──► Close (Record Loss)
                │  <= -$75?      │         lastHedgeWasLoss = true
                └────────┬───────┘
                         │ NO
                         ▼
                ┌────────────────┐
                │ Update Peak    │
                │ Profit         │
                └────────┬───────┘
                         │
                         ▼
                ┌────────────────┐
                │ Peak >= $20?   │──NO──► Continue
                └────────┬───────┘
                         │ YES
                         ▼
                ┌────────────────┐
                │ Profit <= Peak │──YES──► Close (Trailing)
                │    - $10?      │         Record P/L
                └────────┬───────┘
                         │ NO
                         ▼
                      Continue
```

---

## Key Parameters

### Grid Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| LotSize | 0.02 | Lot size for each grid position |
| GridDistancePoints | 200 | Fixed grid distance (A series) |
| GridIncrementStep | 200 | Base increment for incremental grid (B series) |
| MaxTrades | 50 | Maximum grid positions |

### Basket Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| BasketProfit | 10.0 | Close all when profit reaches this |
| BasketLossLimit | -320.0 | Close grid if loss exceeds this |
| BasketStopLoss | -150.0 | For no-hedge strategies |
| RestartAfterHours | 2 | Pause hours after loss close |

### Hedge Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| EnableHedge | true | Enable/disable hedging |
| HedgeTriggerUSD | 150.0 | Open hedge when grid loss reaches this |
| HedgeLot | 0.05 | Hedge position size |
| HedgeFixedLossUSD | 75.0 | Close hedge if loss exceeds this |
| HedgeTrailStart | 20.0 | Start trailing hedge at this profit |
| HedgeTrailStep | 10.0 | Trail step for hedge |

### Grid Trailing Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| GridTrailStart | 20.0 | Start trailing grid basket at this profit |
| GridTrailStep | 10.0 | Close if profit drops this much from peak |

### Safety Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| StopTradingBalance | 1100.0 | Stop if balance exceeds (for demo) |
| MaxSpreadPoints | 80 | Skip trading if spread too high |
| MinMarginLevel | 250.0 | Skip trading if margin too low |
| TradeCooldownSeconds | 3 | Minimum seconds between trades |

---

## File Comparison

### Simplicity vs Features

```
SIMPLEST                                              MOST FEATURES
   │                                                        │
   ▼                                                        ▼
   A1 ──► A2 ──► B1 ──► B2 ──► A3 ──► B3 ──► A4 ──► B4 ──► A5 ──► B5 ──► A6 ──► B6
   │      │      │      │      │      │      │      │      │      │      │      │
   │      │      │      │      │      │      │      │      │      │      │      └─ Full featured incremental
   │      │      │      │      │      │      │      │      │      │      └─ Full featured fixed
   │      │      │      │      │      │      │      │      │      └─ Incr + Hedge + Pool
   │      │      │      │      │      │      │      │      └─ Fixed + Hedge + Pool
   │      │      │      │      │      │      │      └─ Incr + Hedge + Trail
   │      │      │      │      │      │      └─ Fixed + Hedge + Trail
   │      │      │      │      │      └─ Incr + Hedge basic
   │      │      │      │      └─ Fixed + Hedge basic
   │      │      │      └─ Incr + Trail only
   │      │      └─ Incr basic
   │      └─ Fixed + Trail only
   └─ Fixed basic
```

### Safety Rating

```
LEAST SAFE                                            SAFEST
   │                                                    │
   ▼                                                    ▼
   A1 ◄── A2 ◄── B1 ◄── B2 ◄── A3 ◄── A4 ◄── B3 ◄── B4 ◄── A5 ◄── A6 ◄── B5 ◄── B6
   │                                                                              │
   └──────────────────────────────────────────────────────────────────────────────┘

   Why B6 is safest:
   ✓ Incremental grid = fewer positions
   ✓ Hedge protection = covers adverse moves
   ✓ Profit pooling = accurate recovery
   ✓ Grid trailing = locks in profits
```

---

## Recommendations

### For Beginners
Start with **B1** or **B2**:
- Simple to understand
- Incremental grid is safer
- No hedge complexity

### For Testing Hedge Logic
Use **B3**:
- Incremental grid
- Basic hedge without pooling
- Easier to verify hedge behavior

### For Production (Ranging Market)
Use **B6**:
- Full protection
- Best recovery capability
- Adapts to various conditions

### For Production (Trending Market)
Use **B2** or **A2**:
- No hedge (hedging loses in trends)
- Trailing locks profits
- Cut losses quickly

---

## Understanding Recovery Calculation

### Without Profit Pooling
```
Recovery = Current Floating P/L - All Realized Hedge Losses

Example:
- Grid positions: -$80 floating
- Hedge 1: closed +$25 (NOT counted)
- Hedge 2: closed -$40 (counted as loss)

Recovery = -$80 - $40 = -$120
Need $130 more profit to reach $10 target
```

### With Profit Pooling
```
Recovery = Current Floating P/L + Realized Hedge Profits - Realized Hedge Losses

Example:
- Grid positions: -$80 floating
- Hedge 1: closed +$25 (counted)
- Hedge 2: closed -$40 (counted)

Recovery = -$80 + $25 - $40 = -$95
Need $105 more profit to reach $10 target (saves $25!)
```

---

## Common Scenarios

### Scenario 1: Quick Profit (Best Case)
```
1. Open first BUY at 2000.00
2. Price rises to 2001.00
3. Profit = $10
4. Close all → Profit!
5. Switch to SELL direction
6. Repeat
```

### Scenario 2: Grid Recovery
```
1. Open first BUY at 2000.00
2. Price drops to 1998.00 → Open 2nd BUY
3. Price drops to 1996.00 → Open 3rd BUY
4. Price rises to 2000.00
5. All positions profitable
6. Total profit = $10 → Close all
```

### Scenario 3: Hedge Triggered
```
1. Multiple BUY positions open
2. Price keeps dropping
3. Grid loss reaches $150
4. Open SELL hedge (0.4 lot)
5. Price drops more → Hedge profits
6. Hedge trailing triggers at +$25
7. Close hedge with +$20 profit
8. Wait for grid recovery
9. Grid + hedge profit = $10 → Close all
```

### Scenario 4: Loss Limit Hit
```
1. Grid positions losing heavily
2. Hedge opened but also losing
3. Grid loss reaches $320
4. Close all grid positions
5. Keep hedge running
6. Wait for hedge to close (trailing or stop)
7. Pause for 2 hours
8. Resume with opposite direction
```

---

## Tips for Optimization

1. **Backtest each file** separately over the same period
2. **Start with B6** as your baseline
3. **Adjust HedgeTriggerUSD** based on your risk tolerance
4. **GridIncrementStep** of 200-300 works well for XAUUSD
5. **HedgeLot** should be 2-4x your grid lot for effective hedging
6. **Monitor margin level** - grid strategies are margin-intensive

---

## File Quick Reference

| Need | Use File |
|------|----------|
| Simplest test | A1 or B1 |
| Lock profits early | A2 or B2 |
| Basic hedge protection | A3 or B3 |
| Hedge + profit locking | A4 or B4 |
| Best recovery (no trail) | A5 or B5 |
| Maximum protection | A6 or B6 |
| Trending market | B2 (no hedge) |
| Ranging market | B6 (full featured) |

---

## Changelog

- **v1**: Original grid + hedge strategy
- **v2**: Added profit pooling
- **v3**: Added grid trailing stop
- **v4**: Added incremental grid distance
- **Current**: 12 complete variations covering all feature combinations

---

## Support

For questions or issues, review the dashboard output in MetaTrader 5 which shows:
- Current floating P/L
- Recovery value
- Hedge status
- Grid trailing status
- All relevant parameters

Happy Trading!
