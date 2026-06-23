# XAUUSD Grid Trading Strategies - Complete Guide

## Overview

This folder contains **18 Expert Advisor (EA) variations** for MetaTrader 5, designed for XAUUSD (Gold) trading using grid strategies and EMA-based strategies.

---

## File Naming Convention

Each file follows the pattern: `{Series}{Number}_{strategy-type}_{features}.mq5`

| Component | Meaning |
|-----------|---------|
| **A** | Fixed Grid Distance (200 points always) |
| **B** | Incremental Grid Distance (200 × N pattern) |
| **C** | EMA-based Single Trade strategies |
| **1-2** | No Hedge strategies |
| **3-7** | With Hedge strategies |
| **8-9** | Time-filtered versions (trades only during optimal hours) |
| **10** | Dynamic stop loss + daily limits |
| **nohedge/hedge** | Hedge protection enabled or not |
| **nopool/pool** | Profit pooling (tracks hedge profits) |
| **notrail/trail** | Grid trailing stop enabled or not |
| **dual_trail** | Both hedge profit and hedge loss trailing enabled |
| **time** | Time filter enabled (MT5 broker time, auto DST handling) |
| **ema** | EMA-based entry signal |

---

## Complete File Matrix

| File | Grid Type | Hedge | Profit Pooling | Grid Trailing | Hedge Profit Trail | Hedge Loss Trail |
|------|-----------|-------|----------------|---------------|-------------------|------------------|
| A1_fixed_nohedge_notrail | Fixed | No | N/A | No | N/A | N/A |
| A2_fixed_nohedge_trail | Fixed | No | N/A | Yes | N/A | N/A |
| A3_fixed_hedge_nopool_notrail | Fixed | Yes | No | No | No | No |
| A4_fixed_hedge_nopool_trail | Fixed | Yes | No | Yes | Yes | No |
| A5_fixed_hedge_pool_notrail | Fixed | Yes | Yes | No | No | No |
| A6_fixed_hedge_pool_trail | Fixed | Yes | Yes | Yes | Yes | No |
| A7_fixed_hedge_pool_dual_trail | Fixed | Yes | Yes | Yes | Yes | Yes |
| B1_incr_nohedge_notrail | Incremental | No | N/A | No | N/A | N/A |
| B2_incr_nohedge_trail | Incremental | No | N/A | Yes | N/A | N/A |
| B3_incr_hedge_nopool_notrail | Incremental | Yes | No | No | No | No |
| B4_incr_hedge_nopool_trail | Incremental | Yes | No | Yes | Yes | No |
| B5_incr_hedge_pool_notrail | Incremental | Yes | Yes | No | No | No |
| B6_incr_hedge_pool_trail | Incremental | Yes | Yes | Yes | Yes | No |
| B7_incr_hedge_pool_dual_trail | Incremental | Yes | Yes | Yes | Yes | Yes |
| **B8_incr_nohedge_trail_time** | **Incremental** | **No** | **N/A** | **Yes** | **N/A** | **N/A** |
| **B9_incr_hedge_pool_trail_time** | **Incremental** | **Yes** | **Yes** | **Yes** | **Yes** | **No** |
| **B10_incr_nohedge_dynamic_trail** | **Incremental** | **No** | **N/A** | **Yes** | **N/A** | **N/A** |

### C-Series: EMA-Based Strategies

| File | Strategy | Entry Signal | Hedge | Trailing | Stop Loss |
|------|----------|--------------|-------|----------|-----------|
| **C1_ema_single_trade** | Single Trade | 1H Open vs N-day EMA (D1, completed bar) | No | Yes | 60% of investment |

**NEW (V8):** B10 includes **dynamic stop loss**, **daily limits**, and **24/7 trading** - see section below.

**NEW (V8):** C1 is an **EMA-based single trade strategy** - see section below.

**B8 and B9:** Include **consistent dual trading windows** with comprehensive filters:

**Trading Schedule (MODE_DUAL_WINDOW - Default):**
| Day | Window 1 | Gap (Skipped) | Window 2 | Total Hours |
|-----|----------|---------------|----------|-------------|
| **Sunday** | - | - | - | 0 hrs (Market closed) |
| **Monday** | 11:00-15:30 | 15:30-17:30 | 17:30-19:30 | **6.5 hrs** |
| **Tuesday** | 11:00-15:30 | 15:30-17:30 | 17:30-19:30 | **6.5 hrs** |
| **Wednesday** | 11:00-15:30 | 15:30-17:30 | 17:30-19:30 | **6.5 hrs** |
| **Thursday** | 11:00-15:30 | 15:30-17:30 | 17:30-19:30 | **6.5 hrs** |
| **Friday** | 11:00-15:30 | 15:30-17:30 | 17:30-19:30 | **6.5 hrs** |
| **Saturday** | - | - | - | 0 hrs (Market closes at 01:00) |
| **Weekly Total** | | | | **~32.5 hrs** |

**Other Trading Modes:**
- **MODE_OVERLAP_ONLY**: 17:30-19:30 UTC+3 (highest volatility period only)
- **MODE_FULL_LONDON**: 11:00-19:30 UTC+3 (continuous window, includes gap)
- **MODE_PEAK_HOUR**: 17:30-18:30 UTC+3 (ultra-conservative)
- **MODE_CUSTOM**: User-defined hours

**V7 Features:**
- **Consistent Schedule**: Same trading hours Monday through Friday (no special day handling)
- **Market Hours Aligned**: Saturday/Sunday blocked (market closes Saturday 01:00 UTC+3)
- All features work year-round with automatic DST handling

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

**V7 Trailing-Only Exit Strategy:**

For **no-hedge strategies with trailing** (A2, B2, B8) and **hedge strategies when hedge is NOT triggered** (B6, B7, B9):
- **NO fixed profit target** - wait for trailing to activate
- Exit ONLY via: **Trailing stop** OR **Stop loss**
- Wait for profit to reach $20 (GridTrailStart), then trail by $10 (GridTrailStep)

```
Example - Trailing-Only Exit:

Scenario: Profit rises and trails
- Profit: 0 → 5 → 10 → 15 → 20 → 25 (peak) → 20 → 15 → CLOSE at $15
- Trail activates at $20, trail level = peak - $10
- At peak $25: trail level = $15
- Closes when profit drops to trail level
- Result: $15 profit (not $10!)

Scenario: Profit never reaches trailing threshold
- Profit: 0 → 5 → 10 → 15 → stays flat → eventually hits STOP LOSS
- Trailing never activates (peak < $20)
- No fixed target closes at $10 - must wait for trailing or stop loss
```

**For hedge strategies when hedge IS triggered:**
- Fixed profit target (BasketProfit) is used for recovery
- Trailing is disabled - need fixed target to ensure full recovery

---

### 5. Hedge Loss Trailing (A7/B7 Only)

#### What is Hedge Loss Trailing?
- A7 and B7 are the **most advanced strategies** with dual trailing capability
- In addition to hedge profit trailing, they also trail the hedge when in LOSS
- This helps minimize hedge losses if the market moves against the hedge

#### How Hedge Loss Trailing Works
```
Hedge Loss Trailing Example:
- Hedge opened at price 2000.00
- Price moves against hedge, loss reaches -$40
- Loss peak = -$40 (trail starts at -$40)
- Trail level = -$40 + $30 = -$10
- If loss improves to -$10 or better, close hedge
- Saves $30 compared to waiting for fixed stop loss at -$75
```

**Trail Parameters:**
- **HedgeLossTrailStart**: Activates when loss reaches this amount (default: $40)
- **HedgeLossTrailStep**: Closes hedge if loss improves by this amount (default: $30)

**Why This Matters:**
- Without loss trailing: Hedge could hit -$75 fixed stop loss
- With loss trailing: If loss reaches -$40 but improves to -$10, close with only -$10 loss
- Reduces overall hedge costs when market briefly moves against hedge

#### Dual Trailing Strategy (A7/B7)
These strategies monitor BOTH directions:
1. **Profit side**: Trail when profit exceeds $20, close if drops $10 from peak
2. **Loss side**: Trail when loss exceeds -$40, close if improves $30 from worst

This provides maximum flexibility to capture profits and minimize losses on hedge positions.

---

### 6. Time Filter (B8/B9 Only) ⏰

#### What is Time Filtering?
- B8 and B9 are **time-aware strategies** that trade only during optimal market hours
- Automatically restricts trading to high-liquidity, trending sessions
- **Critical Advantage**: MT5 broker time shows UTC+3 with automatic DST adjustment

#### How It Works

**MT5 Broker Time = UTC+3**
- MT5 display: UTC+3 (automatically adjusts for DST)
- All trading times configured in UTC+3 timezone
- **You don't need to manually adjust for DST changes!**

#### Flexible Trading Modes (V6 Update)

B8 and B9 now support **5 different trading modes** via dropdown selection:

**1. MODE_DUAL_WINDOW (Default) ⭐ V7 UPDATE**
```cpp
TradingMode = MODE_DUAL_WINDOW
// CONSISTENT WINDOWS (V7) - Same hours Mon-Fri:
// MON-FRI:   Window 1: 11:00-15:30 (Early London)
//            Window 2: 17:30-19:30 (London-NY Overlap)
//            Total: 6.5 hours each day
// SATURDAY:  NO TRADING (Market closes at 01:00 UTC+3)
// SUNDAY:    NO TRADING (Market closed)
// GAP SKIPPED: 15:30-17:30 (All days)
```
- **When to use**: Best for data-driven optimal performance (DEFAULT for both B8 and B9)
- **Benefits**:
  - **Consistent Schedule**: Same trading hours every weekday
  - **Quality Sessions**: Focuses on London and London-NY overlap (best liquidity)
  - Skips the 15:30-17:30 gap period (lower quality trades)
  - ~32.5 hours of targeted trading per week (6.5 hrs × 5 days)
  - Works year-round with automatic DST handling
- **Recommendation**: **DEFAULT - Best balance of trading time and quality**

**2. MODE_OVERLAP_ONLY**
```cpp
TradingMode = MODE_OVERLAP_ONLY
// Trades 17:30 - 19:30 UTC+3
// Only London-NY Overlap (highest volatility window)
```
- **When to use**: Ultra-conservative, highest win rate approach
- **Benefits**:
  - Highest liquidity and volatility
  - Clear directional trends
  - Best win rate per data analysis (85-90%)
  - 2 hours of peak quality trading only
- **Recommendation**: **For maximum quality, minimum exposure**

**3. MODE_FULL_LONDON**
```cpp
TradingMode = MODE_FULL_LONDON
// Trades 11:00 - 19:30 UTC+3 (continuous)
// Includes the gap period (may have lower quality trades)
```
- **When to use**: When you want maximum trading opportunities
- **Benefits**:
  - Continuous trading window (no gaps)
  - 8.5 hours of trading per day
  - Good for hedge strategies that need more time
- **Recommendation**: **For experienced traders who monitor constantly**

**4. MODE_PEAK_HOUR**
```cpp
TradingMode = MODE_PEAK_HOUR
// Trades 17:30 - 18:30 UTC+3
// Only the first hour of overlap (most consistent)
```
- **When to use**: Ultra-conservative approach
- **Benefits**:
  - Lowest risk exposure
  - Highest quality setups only
  - 1 hour of peak trading
- **Recommendation**: **For high-volatility days or conservative capital**

**5. MODE_CUSTOM**
```cpp
TradingMode = MODE_CUSTOM
CustomStartHour = 9      // Set your own hours
CustomStartMinute = 30
CustomEndHour = 11
CustomEndMinute = 30
```
- **When to use**: Advanced users with specific requirements
- **Benefits**:
  - Full control over trading window
  - Test different time ranges
- **Recommendation**: **For experienced traders only**

#### Quick Mode Selection Guide

| Strategy | Market Type | Recommended Mode | Trading Window (UTC+3) | Weekly Hours |
|----------|-------------|------------------|------------------------|--------------|
| **B8/B9** (General) | All Markets | MODE_DUAL_WINDOW ⭐ | Mon-Fri: 11:00-15:30 + 17:30-19:30 | ~32.5 hours |
| **B8** (Conservative) | Trending | MODE_OVERLAP_ONLY | Mon-Fri: 17:30-19:30 | ~10 hours |
| **B9** (Maximum) | Ranging | MODE_FULL_LONDON | Mon-Fri: 11:00-19:30 | ~42.5 hours |
| Any (Ultra-safe) | High Volatility | MODE_PEAK_HOUR | Mon-Fri: 17:30-18:30 | ~5 hours |
| Any (Advanced) | Custom Analysis | MODE_CUSTOM | User-defined | Variable |

#### Automatic DST Handling

Since MT5 broker time shows UTC+3, DST is handled automatically:

```
All Year Round:
- MT5 displays UTC+3
- MODE_DUAL_WINDOW: 11:00-15:30 + 17:30-19:30 UTC+3
- MODE_OVERLAP_ONLY: 17:30-19:30 UTC+3
- MODE_FULL_LONDON: 11:00-19:30 UTC+3

NO MANUAL ADJUSTMENT NEEDED - ALL MODES WORK YEAR-ROUND!
```

**Why This Works:**
- MT5 automatically adjusts for DST transitions
- All times remain in UTC+3 regardless of season
- Your MODE selection works identically across all seasons

#### Time Filter Behavior

**V7 Behavior - Active Position Management:**
- **Active positions are ALWAYS managed** regardless of trading hours
- Stop loss and trailing stop are checked every tick, even outside trading windows
- Time filter only blocks **opening NEW positions**, not managing existing ones
- This ensures you never get stuck with an unmanaged grid when trading hours end

```
Example - Grid Open When Trading Hours End:

Before V7 (BUG):
- Grid active at 19:30 (end of Window 2)
- Trading hours end → EA stops checking stop loss/trailing
- Grid continues losing without any exit management!

After V7 (FIXED):
- Grid active at 19:30 (end of Window 2)
- Trading hours end → EA still checks stop loss and trailing stop every tick
- Grid closes properly when stop loss or trailing stop is triggered
- Only NEW grid opening is blocked outside hours
```

**Default Behavior:**
- Open positions continue running even outside trading hours
- Stop loss and trailing stop remain active at all times
- Existing baskets close based on exit conditions (profit target, trail stop, loss limit)
- `ClosePositionsOutsideHours = false` (default): Keep grid open, manage exits
- `ClosePositionsOutsideHours = true`: Force close all when hours end

#### Day-of-Week Filter (V7 Feature) 📅

B8 and B9 use a simplified, consistent day filter:

**V7 Consistent Schedule:**
```cpp
// All weekdays use the same trading windows:
// Monday-Friday: Window 1: 11:00-15:30, Window 2: 17:30-19:30
// Saturday: NO TRADING (market closes at 01:00 UTC+3, before our windows)
// Sunday: NO TRADING (market closed)
```

**Why No Special Monday/Saturday Windows:**
- **Consistency**: Same strategy behavior every weekday
- **Quality Focus**: Asian session (05:00-11:00) has lower quality trades
- **Market Alignment**: Saturday market closes at 01:00 UTC+3, before our 11:00 window starts

**XAUUSD Market Hours (UTC+3):**
- Opens: Monday 01:00 UTC+3
- Closes: Saturday 01:00 UTC+3
- Our windows: 11:00-15:30 and 17:30-19:30 (within market hours Mon-Fri)

**Best Trading Days:**
- **Tuesday-Thursday**: Most consistent price action
- These are highlighted as "BEST DAY" in the dashboard

**How to Disable:**
```cpp
EnableDayFilter = false        // Disable all day restrictions (not recommended)
```

#### Benefits

1. **Eliminates low-quality trades** during Asian session
2. **Higher win rate** - trades only during trending sessions
3. **Better risk/reward** - avoids choppy, low-liquidity periods
4. **Automatic DST** - no manual intervention needed twice per year
5. **Transparent** - Dashboard shows current time and window status

#### Dashboard Display (V7 Update)

The dashboard shows comprehensive real-time information about all filters:

```
GRID V7 (Incremental + NO HEDGE + DUAL WINDOW + DAY FILTER)

--- TIME FILTER ---
Time Filter: ENABLED
Trading Mode: Dual Window
MON-FRI: Window 1: 11:00-15:30 UTC+3
Window 2: 17:30-19:30 UTC+3
GAP SKIPPED: 15:30-17:30 UTC+3
Current Time (MT5): 14:15:30 (UTC+3)
Current Window: Window 1 (Early London)
Time Status: INSIDE WINDOW

--- DAY FILTER ---
Day Filter: ENABLED
Today: Wednesday (BEST DAY)
Day Status: ALLOWED

--- TRADING STATUS ---
Overall Status: TRADING ALLOWED
```

**V7 Dashboard Shows:**
- **Trading Mode**: Which MODE is selected (Dual Window, Overlap Only, etc.)
- **Consistent Windows**: Same windows displayed for all weekdays (Mon-Fri)
- **Current Window**: Which window you're currently in (Window 1 or Window 2)
- **Time Status**: Whether current time is inside or outside trading windows
- **Day Filter Status**: Current day and whether trading is allowed
- **Overall Status**: Clear indication if trading is allowed or blocked (and why)

#### Comparison: B2 vs B8, B6 vs B9 (V7 Features)

| Feature | B2/B6 (No Filter) | B8/B9 (V7 With Filters) |
|---------|-------------------|-------------------------|
| Trading hours | 24/7 | ~32.5 hours/week (MODE_DUAL_WINDOW) |
| Trading modes | None | 5 modes (Dual Window, Overlap, Full London, Peak, Custom) |
| Schedule | N/A | Consistent Mon-Fri (same windows each day) |
| Monday trading | ✅ Full day | ✅ 11:00-15:30 + 17:30-19:30 (6.5 hrs) |
| Saturday trading | ✅ Until market close | ❌ No trading (market closes before windows) |
| Asian session | ✅ Trades (choppy) | ❌ Skips (prevents losses) |
| Gap period (15:30-17:30) | ✅ Trades | ❌ Skips (MODE_DUAL_WINDOW) |
| London-NY overlap | ✅ Trades | ✅ Trades (all modes) |
| DST adjustment | Manual | Automatic (year-round) |
| Win rate | Lower (all sessions) | Higher (V7: targeted sessions) |
| Drawdown frequency | Higher | Lower (V7: better entry timing) |
| Weekly coverage | 120+ hours | ~32.5 hours (optimized) |
| Best for | 24/7 monitoring | Strategic time-based trading with full control |

**Recommendation:** Use B8/B9 (V7) for **optimal data-driven performance** with maximum control.

**V7 Mode Recommendations:**
- **B8/B9 (Default)**: Use MODE_DUAL_WINDOW for best balance (~32.5 hours/week)
- **B8 (Conservative)**: Use MODE_OVERLAP_ONLY for highest win rate (~10 hours/week)
- **B9 (Maximum)**: Use MODE_FULL_LONDON for full session coverage (~42.5 hours/week)

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
| HedgeTrailStart | 20.0 | Start trailing hedge profit at this level |
| HedgeTrailStep | 10.0 | Trail step for hedge profit |
| HedgeLossTrailStart | 40.0 | Start trailing hedge loss at this level (A7/B7 only) |
| HedgeLossTrailStep | 30.0 | Trail step for hedge loss (A7/B7 only) |

### Grid Trailing Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| GridTrailStart | 20.0 | Start trailing grid basket at this profit |
| GridTrailStep | 10.0 | Close if profit drops this much from peak |

### Safety Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| StopTradingBalance | 1100.0 | Stop if balance exceeds (for demo) |
| MaxSpreadPoints | 80 | Skip trading if spread too high (A/B1-B9) |
| MinMarginLevel | 250.0 | Skip trading if margin too low |
| TradeCooldownSeconds | 3 | Minimum seconds between trades |

**Note:** B10 does NOT use MaxSpreadPoints - it relies on market pause buffers instead.

---

## File Comparison

### Simplicity vs Features

```
SIMPLEST                                                            MOST FEATURES
   │                                                                      │
   ▼                                                                      ▼
   A1 ──► A2 ──► B1 ──► B2 ──► A3 ──► B3 ──► A4 ──► B4 ──► A5 ──► B5 ──► A6 ──► B6 ──► A7 ──► B7
   │      │      │      │      │      │      │      │      │      │      │      │      │      │
   │      │      │      │      │      │      │      │      │      │      │      │      │      └─ Ultimate: Incr + Dual Trail
   │      │      │      │      │      │      │      │      │      │      │      │      └─ Ultimate: Fixed + Dual Trail
   │      │      │      │      │      │      │      │      │      │      │      └─ Incr + Pool + Trail
   │      │      │      │      │      │      │      │      │      │      └─ Fixed + Pool + Trail
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
LEAST SAFE                                                      SAFEST
   │                                                              │
   ▼                                                              ▼
   A1 ◄── A2 ◄── B1 ◄── B2 ◄── A3 ◄── A4 ◄── B3 ◄── B4 ◄── A5 ◄── A6 ◄── B5 ◄── B6 ◄── A7 ◄── B7
   │                                                                                            │
   └────────────────────────────────────────────────────────────────────────────────────────────┘

   Why B7 is safest:
   ✓ Incremental grid = fewer positions
   ✓ Hedge protection = covers adverse moves
   ✓ Profit pooling = accurate recovery
   ✓ Grid trailing = locks in profits
   ✓ Hedge dual trailing = minimizes hedge losses, maximizes hedge profits
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
Use **B9** (NEW), **B6**, or **B7**:
- **B9** (⭐ RECOMMENDED): B6 + Time Filter for optimal performance
  - Trades only during optimal sessions (default: 11:00-15:30 + 17:30-19:30 UTC+3)
  - Automatic DST handling
  - Expected 40-60% better performance vs 24/7 trading
- **B6**: Full protection without hedge loss trailing (+30.12% in backtests)
- **B7**: Ultimate protection with dual trailing on hedge (+20.74% in backtests)
- **B5**: Solid alternative without trailing complexity (+25.60% in backtests)

**Note**: Recent backtests (May 28-29, 2026) showed B6 outperforming B7. B9 adds time filtering to B6's proven logic for even better results.

### For Production (Trending Market)
Use **B8** (⭐ NEW) or **B2**:
- **B8** (RECOMMENDED): B2 + Time Filter
  - Trades only during high-trend sessions (default: 11:00-15:30 + 17:30-19:30 UTC+3)
  - No hedge (hedging loses in trends)
  - Trailing locks profits
  - Automatic DST handling
- **B2**: 24/7 version without time filter
  - Cut losses quickly
  - More frequent trading opportunities

### For Maximum Control
Use **B9** (⭐ NEW) or **B7**:
- **B9** (RECOMMENDED): Most sophisticated + time-aware
  - All features of B7 plus time filtering
  - Automatic DST handling
  - Trades only during proven high-win-rate hours
  - Best for experienced traders seeking optimal performance
- **B7**: 24/7 version with dual trailing
  - Maximum complexity without time restrictions
  - Best for those who can monitor markets constantly

### Important Warning: A-Series (Fixed Grid) Strategies
**Use with caution!** Recent backtests showed:
- **A6**: -105.09% (account blown)
- **A7**: -107.77% (account blown)
- Fixed grid accumulates positions too quickly in trending markets
- Consider using smaller lot sizes or tighter loss limits with A-series
- **B-series (Incremental)** is strongly recommended over A-series for most scenarios

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

## Recommended Trading Hours (IST)

Based on tick data analysis of 331,023 ticks over XAUUSD market sessions, the following trading hours are recommended for optimal grid strategy performance.

**⚠️ IMPORTANT: Daylight Saving Time (DST) Impact**

Since **IST does not observe DST** but London and New York do, the optimal trading hours in IST **shift by 1 hour** depending on the season.

**Note:** The tick data analyzed (May 28-29, 2026) was collected during the summer DST period when both London and New York were observing daylight saving time.

See [DST Adjustments](#daylight-saving-time-dst-adjustments) section below for detailed schedules.

### BEST TRADING HOURS (IST)

#### Primary Window: London-NY Overlap ⭐
- **Summer Period (March-October)**: **7:00 PM - 9:00 PM IST**
- **Winter Period (November-February)**: **8:00 PM - 10:00 PM IST**
- **Market Session**: London-NY Overlap
- **Volatility**: Highest (0.0293-0.0297% std dev)
- **Characteristics**:
  - Maximum liquidity
  - Clear directional trends
  - Best for grid trailing stops
  - Optimal price action for grid strategies
- **Recommendation**: **PRIMARY trading window - deploy all strategies**

#### Secondary Window: London Session ✓
- **Summer Period (March-October)**: **12:30 PM - 5:00 PM IST**
- **Winter Period (November-February)**: **1:30 PM - 6:00 PM IST**
- **Market Session**: London Session
- **Volatility**: Good (0.0243-0.0277% std dev)
- **Characteristics**:
  - Decent liquidity
  - Moderate trends
  - European market activity
  - Good for conservative strategies
- **Recommendation**: **Secondary window - suitable for most strategies**

### AVOID TRADING HOURS (IST)

#### Asian Session: 6:30 AM - 11:30 AM IST ⚠️
- **Market Session**: Asian Markets (Tokyo, Singapore, Hong Kong)
- **Volatility**: Low (0.0080-0.0240% std dev)
- **Characteristics**:
  - Choppy, range-bound movement
  - Low liquidity causes whipsaw
  - Stop losses frequently hit without recovery
  - High false signal rate
- **Recommendation**: **AVOID - High risk of losses**

#### Late Night: 9:00 PM - 6:00 AM IST ❌
- **Market Session**: After-hours / Early Asian
- **Volatility**: Very Low (0.0101-0.0152% std dev)
- **Characteristics**:
  - Minimal liquidity
  - Erratic price movements
  - Wide spreads
  - Gap risk
- **Recommendation**: **AVOID - No favorable conditions**

### Trading Schedule Summary

**Summer Schedule (March - October)** - When UK & US observe DST:

| Time (IST) | Session | Status | Grid Strategy Suitability |
|------------|---------|--------|---------------------------|
| 06:30 - 11:30 | Asian | AVOID | Poor - Choppy movement |
| 11:30 - 12:30 | Pre-London | CAUTION | Fair - Transitional |
| 12:30 - 17:00 | London | GOOD | Good - Moderate trends |
| 17:00 - 19:00 | Pre-Overlap / NY Open | CAUTION | Fair - Building volatility |
| 19:00 - 21:00 | London-NY Overlap | BEST | Excellent - Peak conditions |
| 21:00 - 00:30 | NY Session | GOOD | Good - Still active |
| 00:30 - 06:30 | After Hours | AVOID | Poor - Low activity |

**Winter Schedule (November - February)** - When UK & US on Standard Time:

| Time (IST) | Session | Status | Grid Strategy Suitability |
|------------|---------|--------|---------------------------|
| 06:30 - 11:30 | Asian | AVOID | Poor - Choppy movement |
| 11:30 - 13:30 | Pre-London | CAUTION | Fair - Transitional |
| 13:30 - 18:00 | London | GOOD | Good - Moderate trends |
| 18:00 - 20:00 | Pre-Overlap / NY Open | CAUTION | Fair - Building volatility |
| 20:00 - 22:00 | London-NY Overlap | BEST | Excellent - Peak conditions |
| 22:00 - 01:30 | NY Session | GOOD | Good - Still active |
| 01:30 - 06:30 | After Hours | AVOID | Poor - Low activity |

### Important Notes

1. **News Events**: Pause EA 30 minutes before and after major news:
   - US Non-Farm Payrolls (NFP) - First Friday, 6:00 PM IST
   - US CPI (Inflation Data) - Mid-month, 6:00 PM IST
   - FOMC Rate Decisions - 11:30 PM IST
   - ECB Rate Decisions - 5:45 PM IST
   - Major GDP releases

2. **Best Trading Days**:
   - **Tuesday - Thursday**: Most consistent price action
   - **Monday**: Wait until after 3:00 PM IST (post-weekend gap settlement)
   - **Friday**: Exercise caution after 9:00 PM IST (weekend risk)

3. **Price Behavior Analysis** (from tick data):
   - Median 1-hour swing: 1,215 points (typically 2-3 grid positions)
   - Median drawdown recovery time: 3.5 minutes
   - 85% of drawdowns occur below $54 with proper timing
   - Mean reversion is strongest during London-NY overlap

4. **Strategy-Specific Timing**:
   - **No-hedge strategies (B1, B2)**:
     - Summer: 7:00-9:00 PM IST only (London-NY overlap)
     - Winter: 8:00-10:00 PM IST only (London-NY overlap)
   - **Hedge strategies (B6, B7)**:
     - Summer: 12:30 PM - 9:00 PM IST (full London + overlap)
     - Winter: 1:30 PM - 10:00 PM IST (full London + overlap)
   - **Fixed grid (A-series)**: Extra caution - trending sessions only
   - **Incremental grid (B-series)**: More flexible across all good hours

5. **Time-Based EA Control**:
   - Consider implementing time filters in EA settings
   - Automatically pause outside recommended hours
   - Resume automatically during prime windows

### Performance Impact of Trading Hours

Based on data analysis (May 2026 - Summer DST period):

```
Trading during BEST hours (London-NY Overlap):
- Summer: 7:00-9:00 PM IST | Winter: 8:00-10:00 PM IST
- Win rate: ~85-90%
- Average drawdown: -$54
- Recovery time: 3-5 minutes
- Expected cycles per session: 24-30

Trading during AVOID hours (Asian Session):
- 6:30-11:30 AM IST (same year-round)
- Win rate: ~50-60%
- Average drawdown: -$150+
- Recovery time: 15-30 minutes
- Expected cycles per session: 8-12
- High stop loss hit rate
```

**Key Takeaway**: Trading only during recommended hours can improve profitability by 40-60% compared to 24/7 operation.

---

### Daylight Saving Time (DST) Adjustments

**Understanding the Time Shift:**

IST (Indian Standard Time) = **UTC+5:30** year-round (NO DST)

However, London and New York observe DST:
- **London**: GMT (UTC+0) → BST (UTC+1) during summer
- **New York**: EST (UTC-5) → EDT (UTC-4) during summer

**Result:** Trading hours in IST shift by **1 hour earlier** during summer months.

#### DST Transition Dates (Approximate)

**UK (Last Sunday of March to Last Sunday of October):**
- **Starts**: Last Sunday in March (clocks forward)
- **Ends**: Last Sunday in October (clocks backward)
- Examples:
  - 2024: March 31 - October 27
  - 2025: March 30 - October 26
  - 2026: March 29 - October 25

**US (Second Sunday of March to First Sunday of November):**
- **Starts**: Second Sunday in March (clocks forward)
- **Ends**: First Sunday in November (clocks backward)
- Examples:
  - 2024: March 10 - November 3
  - 2025: March 9 - November 2
  - 2026: March 8 - November 1

#### Quick Reference: Best Trading Hours by Season

| Period | Months | London-NY Overlap (IST) | London Session (IST) | Status |
|--------|--------|------------------------|---------------------|---------|
| **Summer** | March - October | **7:00 PM - 9:00 PM** | 12:30 PM - 5:00 PM | Both markets in DST |
| **Winter** | November - February | **8:00 PM - 10:00 PM** | 1:30 PM - 6:00 PM | Both markets standard time |

#### Transition Periods (3-4 weeks with mismatched DST)

During March and November, there are brief periods when one market has switched to DST but the other hasn't:

**Early March (US in DST, UK still GMT):** ~2-3 weeks
- NY opens earlier: 7:00 PM IST (EDT)
- London still on: 1:30 PM - 10:00 PM IST (GMT)
- Overlap: **7:00 PM - 10:00 PM IST** (3 hours)

**Late October to Early November (UK back to GMT, US still DST):** ~1-2 weeks
- London back to: 1:30 PM - 10:00 PM IST (GMT)
- NY still on: 7:00 PM - 12:30 AM IST (EDT)
- Overlap: **7:00 PM - 10:00 PM IST** (3 hours)

**Extended overlap during transitions can be advantageous!**

#### How to Check Current DST Status

**Manual Check:**
1. **London**: If UK clocks are GMT (winter), add 5.5 hours to get IST
2. **London**: If UK clocks are BST (summer), add 4.5 hours to get IST
3. **New York**: If US clocks are EST (winter), add 10.5 hours to get IST
4. **New York**: If US clocks are EDT (summer), add 9.5 hours to get IST

**Quick Test:**
- If London opens at 8:00 AM local time:
  - Winter (GMT): 8:00 AM GMT = **1:30 PM IST**
  - Summer (BST): 8:00 AM BST = **12:30 PM IST**

- If NY opens at 9:30 AM local time:
  - Winter (EST): 9:30 AM EST = **8:00 PM IST**
  - Summer (EDT): 9:30 AM EDT = **7:00 PM IST**

#### Important DST Notes

1. **Mark Your Calendar**: Set reminders for DST transition dates to adjust EA trading hours
2. **Weekend Transitions**: DST changes happen on weekends (Sunday morning), so adjust before Monday trading
3. **Automatic Adjustment**: If using time-based EA filters, update parameters twice per year
4. **Gap Risk**: Be cautious the first trading day after DST changes - markets can gap
5. **Broker Server Time**: Check your broker's server time zone and how they handle DST

#### Recommended Approach

**Simple Solution:** Use the **Conservative Schedule** that works year-round:
- Trade **8:00 PM - 9:00 PM IST** (works for both summer and winter)
- This captures the peak hour of overlap in all seasons
- Sacrifice 1 hour of potential trading for simplicity

**Optimal Solution:** Adjust EA parameters twice per year:
- **Set Summer hours on last Sunday of March**
- **Set Winter hours on first Sunday of November**

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
| Ultimate protection (dual trail) | A7 or B7 |
| **Time-filtered (best hours only)** | **B8 or B9** |
| **Auto DST handling** | **B8 or B9** |
| Trending market | B2 or **B8** (no hedge) |
| Ranging market | B7, B6, or **B9** (full featured) |
| Most sophisticated | **B9** (incr + hedge + pool + trail + time) |
| Simplest with time filter | **B8** (incr + trail + time) |
| **24/7 with dynamic features** | **B10** (incr + dynamic SL + daily limits) |
| **EMA-based single trade** | **C1** (single lot + EMA signal + trailing) |

---

## B10: Advanced Dynamic Strategy (NEW in V8, Updated V9)

### Overview

B10 is a specialized strategy designed for **24/7 automated trading** with intelligent risk management:

| Feature | Description |
|---------|-------------|
| Grid Type | Incremental (200 × N points) |
| Hedging | NO |
| Profit Exit | Dynamic Trailing Stop (position-based step + min floor) |
| Stop Loss | LOT-SCALED ($75-$300 base, scales with lot size) |
| Time Filters | NONE (runs 24/7, year-round) |
| Direction | ALWAYS switches after every trade |

### Key Features

#### 1. Lot-Scaled Dynamic Stop Loss (V9 NEW)

All stop loss parameters **automatically scale** based on lot size using a multiplier:

```
Multiplier = LotSize / 0.1
```

**Base Values (for 0.1 lot):**
| Parameter | Base Value |
|-----------|------------|
| Min Stop Loss | $75 |
| Max Stop Loss | $300 |
| SL Threshold | $85 |
| SL Cushion | $10 |

**Scaled Examples:**
| Lot Size | Multiplier | Min SL | Max SL | SL Threshold | SL Cushion |
|----------|------------|--------|--------|--------------|------------|
| 0.1 | 1× | $75 | $300 | $85 | $10 |
| 0.2 | 2× | $150 | $600 | $170 | $20 |
| 0.3 | 3× | $225 | $900 | $255 | $30 |
| 0.5 | 5× | $375 | $1500 | $425 | $50 |

**Dynamic SL Logic:**
```
IF dayProfit <= scaledSLThreshold:
   stopLoss = scaledMinSL
ELSE:
   stopLoss = dayProfit - scaledCushion (capped at scaledMaxSL)
```

**Why Lot-Scaling?** Larger positions have proportionally larger profit/loss swings. A 0.2 lot position moves twice as much in dollar terms as a 0.1 lot, so stop loss and thresholds should scale accordingly.

#### 2. Lot-Scaled Dynamic Pause Time After Stop Loss (V9 Updated)

Pause durations based on stop loss amount hit. **Thresholds scale with lot size:**

**Base Thresholds (for 0.1 lot):**
| Stop Loss Hit | Pause Duration |
|---------------|----------------|
| < $75 | 0 minutes |
| $75 - $149 | 15 minutes |
| $150 - $199 | 30 minutes |
| $200 - $249 | 45 minutes |
| $250 - $300 | 60 minutes |

**Scaled Thresholds (for 0.2 lot = 2× multiplier):**
| Stop Loss Hit | Pause Duration |
|---------------|----------------|
| < $150 | 0 minutes |
| $150 - $299 | 15 minutes |
| $300 - $399 | 30 minutes |
| $400 - $499 | 45 minutes |
| $500 - $600 | 60 minutes |

**Direction always switches** regardless of pause duration.

#### 3. Dynamic Trailing Stop Based on Position Count (V9 NEW)

The trailing stop step **dynamically adjusts** based on how many positions are open:

**Formula:**
```
Trail Step = TrailStepBase + (positions - 1) × TrailStepMultiplier
Close Level = max(PeakProfit - TrailStep, MinTrailProfit)
```

**Default Values (configurable inputs):**
| Parameter | Default |
|-----------|---------|
| GridTrailStart | $20 |
| TrailStepBase | $10 |
| TrailStepMultiplier | $9 |
| MinTrailProfit | $10 |

**Resulting Trail Steps:**
| Positions | Trail Step | Calculation |
|-----------|------------|-------------|
| 1 | $10 | 10 + 0×9 |
| 2 | $19 | 10 + 1×9 |
| 3 | $28 | 10 + 2×9 |
| 4 | $37 | 10 + 3×9 |

**Example with 2 positions, peak profit = $25:**
```
Trail Step = $19
Raw Close Level = $25 - $19 = $6
Min Floor = $10
Actual Close Level = max($6, $10) = $10 ✓
```

**Why Position-Based Trailing?**
- With 1 position, a $10 swing is significant and likely indicates direction change
- With multiple positions, the same $10 swing is relatively smaller (more noise)
- Larger step for more positions prevents premature exits from small fluctuations
- The $10 minimum floor ensures you always book at least $10 profit once trailing activates

#### 4. Daily Target

- Input: `DailyTarget = 200.0` (default)
- When day's net profit reaches target, stop opening new trades
- Active grid continues until closed (trailing/stop loss)
- Resets at midnight (00:00 UTC+3)

#### 5. Daily Loss Limit

- Input: `DailyLossLimit = 500.0` (default)
- When day's net loss reaches limit, stop opening new trades
- Protects against catastrophic daily losses
- Resets at midnight (00:00 UTC+3)

#### 6. Market Pause Buffers

Optional pauses around market open/close times:

- `PauseMinutesAfterMarketOpen = 0` (default)
- `PauseMinutesBeforeMarketClose = 0` (default)

**XAUUSD Market Hours (UTC+3):**
| Day | Open | Close | Duration |
|-----|------|-------|----------|
| Mon-Fri | 01:00 | 00:00 (next day) | 23 hours |
| Daily Maintenance | 00:00 - 01:00 | | 1 hour |
| Weekend | Sat 01:00 - Mon 01:00 | | Closed |

**Active trade handling:** If a grid is open when pause starts, it continues to be managed (can close via trailing/stop loss).

#### 7. Direction Always Switches

After **every** completed trade (profit OR loss), direction switches:
- BUY grid closes → Next grid is SELL
- SELL grid closes → Next grid is BUY
- No exceptions, regardless of close reason

### B10 Input Parameters (V10 Updated)

```cpp
//--- GRID SETTINGS ---
input double LotSize                      = 0.01;   // Also used for lot multiplier
input int    MaxTrades                    = 10;
input int    BaseGridDistance             = 200;    // Points
input int    GridIncrementStep            = 200;    // Points

//--- TRAILING STOP (V10 - 0 = AUTO-scale, >0 = use as-is) ---
input double GridTrailStart               = 0;      // 0=auto(20×mult) | else as-is
input double TrailStepBase                = 0;      // 0=auto(10×mult) | else as-is
input double TrailStepMultiplier          = 0;      // 0=auto(9×mult)  | else as-is
input double MinTrailProfit               = 0;      // 0=auto(10×mult) | else as-is

//--- DYNAMIC STOP LOSS (Auto-scaled by lot size) ---
// Base values (for 0.1 lot): MinSL=$75, MaxSL=$300, Threshold=$85, Cushion=$10
// Actual values = Base × (LotSize / 0.1)

//--- DAILY LIMITS (V10 - 0 = AUTO-scale, >0 = use as-is) ---
input double DailyTarget                  = 0;      // 0=auto(200×mult) | else as-is
input double DailyLossLimit               = 0;      // 0=auto(500×mult) | else as-is

//--- DYNAMIC DAILY TARGET (Auto-scaled by lot size) ---
// Base values (for 0.1 lot):
// LossThreshold1=$200 -> ReducedTarget1=$50
// LossThreshold2=$300 -> ReducedTarget2=$10
// Actual values scale with lot size

//--- MARKET PAUSE BUFFERS ---
input int    PauseMinutesAfterMarketOpen  = 0;      // Minutes after 01:00
input int    PauseMinutesBeforeMarketClose = 0;     // Minutes before 00:00

//--- SAFETY ---
input ulong  MagicNumber                  = 101010;
input ulong  Slippage                     = 30;     // Max price deviation in points
```

**Notes:**
- B10 uses `SetTypeFillingBySymbol()` for automatic broker compatibility
- **V10: Sentinel-zero auto-scaling** — for the trailing params and daily limits,
  an input of **`0` means AUTO** (base value × `LotSize/0.1` multiplier); any value
  **`> 0` is used exactly as entered**, with no further multiplication.
- This means **`LotSize` is normally the only value you set** — leave the 6 scalable
  params at `0` and they auto-scale. Two accounts (e.g. 0.1 and 0.3 lot) then trade
  in perfect lockstep: same entries, same exits, same price points — just N× dollars.
- Stop loss params and loss thresholds / reduced targets are **always** auto-scaled
  (no override input — they have no `input` declaration).
- The lot multiplier is rounded to 2 decimals so `0.3/0.1` = exactly `3.00`
  (avoids the `2.9999996` floating-point error at trigger boundaries).

#### 8. Lot-Scaled Dynamic Daily Target (V9 Updated)

When the day's cumulative loss reaches certain thresholds, the daily target is automatically reduced. **Thresholds and reduced targets scale with lot size:**

**Base Values (for 0.1 lot):**
| Day Net Profit | Daily Target Applied |
|----------------|---------------------|
| >= -$199 | Original (input DailyTarget) |
| <= -$200 | Reduced to $50 (Level 1) |
| <= -$300 | Reduced to $10 (Level 2) |

**Scaled Values (for 0.2 lot = 2× multiplier):**
| Day Net Profit | Daily Target Applied |
|----------------|---------------------|
| >= -$399 | Original (input DailyTarget) |
| <= -$400 | Reduced to $100 (Level 1) |
| <= -$600 | Reduced to $20 (Level 2) |

**Important Rules:**
- Once a threshold is hit, the reduced target stays for the rest of the day
- Even if profit recovers (e.g., from -$500 to -$200), the target remains reduced
- Level 2 takes precedence over Level 1
- Flags reset at midnight (00:00 UTC+3)

**Example Scenario (0.2 lot):**
```
Day starts: DailyTarget = $400 (user input)
Lot Size = 0.2 → Multiplier = 2×
Loss Threshold 1 = $400, Reduced Target 1 = $100
Loss Threshold 2 = $600, Reduced Target 2 = $20

Trade 1: -$150 stop loss → dayNetProfit = -$150 → Target still $400
Trade 2: +$80 profit → dayNetProfit = -$70 → Target still $400
Trade 3: -$150 stop loss → dayNetProfit = -$220 → Target still $400
Trade 4: -$300 stop loss → dayNetProfit = -$520 → LEVEL 1 HIT → Target now $100

(If profit recovers to -$200, target REMAINS $100)

Trade 5: -$150 stop loss → dayNetProfit = -$670 → LEVEL 2 HIT → Target now $20

(Even if profit recovers to +$100, target REMAINS $20 for rest of day)
```

**Why This Matters:**
- After significant losses, it's harder to recover to original target
- Reduced target allows earlier exit to preserve remaining capital
- Lot-scaling ensures thresholds are proportional to position size
- Prevents "revenge trading" by setting achievable goals after losses

### B10 Example Trading Day

```
Day starts: Monday 01:00 UTC+3
dayNetProfit = $0
Dynamic Stop Loss = $75 (minimum)

Trade 1 (BUY grid):
├── Opens at 01:00
├── Trailing stop hits at +$30
├── dayNetProfit = $30
├── Dynamic SL still $75 (profit < $85)
└── Direction switches to SELL

Trade 2 (SELL grid):
├── Opens immediately (no pause for profit)
├── Trailing stop hits at +$60
├── dayNetProfit = $90
├── Dynamic SL now = $90 - $10 = $80
└── Direction switches to BUY

Trade 3 (BUY grid):
├── Opens immediately
├── Stop loss hits at -$80
├── dayNetProfit = $90 - $80 = $10
├── Dynamic SL resets to $75 (profit < $85)
├── Direction switches to SELL
└── NO pause (SL $80 < $150)

Trade 4 (SELL grid):
├── Opens immediately
├── Trailing stop hits at +$200
├── dayNetProfit = $210
├── Daily target ($200) REACHED!
└── No new trades for rest of day

Tuesday 01:00:
├── dayNetProfit resets to $0
├── Dynamic SL = $75
└── Trade 5 (BUY) opens - continues alternating
```

---

## C1: EMA Single Trade Strategy (NEW in V8, Updated V9)

### Overview

C1 is a simple **single lot, single trade strategy** based on EMA crossover signals:

| Feature | Description |
|---------|-------------|
| Strategy Type | Single Trade (one position at a time) |
| Entry Signal | 1H candle open vs N-day EMA (default 50) |
| EMA Timeframe | Daily (D1), using last COMPLETED bar |
| Position Size | Single lot (configurable) |
| Stop Loss | 60% of investment (configurable) |
| Profit Exit | Trailing Stop Only |
| Auto Close | Before market close |

### Entry Logic

The strategy checks the 1-hour candle open price against the N-day EMA:

```
IF 1H candle open BELOW EMA:
   → Open SELL position (bearish - price below average)

IF 1H candle open ABOVE EMA:
   → Open BUY position (bullish - price above average)
```

**One trade per day** - once a trade is opened, no new trades until the next day.

### EMA Calculation (V9 Fix)

The EMA is calculated on the **Daily (D1) timeframe** using the **last completed bar** (index 1):

```
EMA Source: PERIOD_D1 (Daily candles)
EMA Index:  1 (yesterday's completed bar, NOT today's incomplete bar)
EMA Type:   Exponential Moving Average on Close prices
```

**Why index 1 instead of index 0?**
- Index 0 = Today's bar (still forming, "close" = current price)
- Index 1 = Yesterday's bar (completed, actual close price)

Using index 0 would cause:
- EMA value changing every tick throughout the day
- Signal flipping BUY → SELL → BUY multiple times
- Inconsistent and unreliable signals

Using index 1 ensures:
- Stable EMA value throughout the trading day
- Consistent signal until next day
- True EMA based on historical closing prices

### Exit Conditions

1. **Stop Loss**: Closes if loss exceeds 60% of investment
   - Investment = Lot Size × Contract Size × Open Price
   - Example: 0.01 lot at $2000 = ~$2000 investment → SL at ~$1200 loss

2. **Trailing Stop**: Locks in profits
   - Activates when profit reaches TrailStart (default $20)
   - Closes if profit drops TrailStep (default $10) from peak

3. **Market Close**: Auto-closes position before market close
   - Default: 5 minutes before 00:00 UTC+3
   - Configurable via `CloseMinutesBeforeMarketClose`

### C1 Input Parameters

```cpp
//--- TRADE SETTINGS ---
input double LotSize                      = 0.01;
input int    EMAPeriod                    = 50;       // EMA Period (days)
input double StopLossPercent              = 60.0;     // Stop Loss % of investment

//--- TRAILING STOP ---
input double TrailStart                   = 20.0;     // Start trailing at this profit ($)
input double TrailStep                    = 10.0;     // Trail by this amount ($)

//--- CLOSE BEFORE MARKET CLOSE ---
input int    CloseMinutesBeforeMarketClose = 5;       // Minutes before market close

//--- SAFETY ---
input ulong  MagicNumber                  = 201010;
input ulong  Slippage                     = 30;
```

### C1 Example Trading Day

```
Day starts: Monday 01:00 UTC+3
50-day EMA = $2010.00

09:00 - New 1H candle opens at $2005.00
├── 1H Open ($2005) < EMA ($2010)
├── Signal: SELL
└── Opens SELL position at $2005.00

12:00 - Price drops to $2000.00
├── Position profit: +$50
├── Peak profit: $50
├── Trail activated (profit > $20)
└── Trail level: $50 - $10 = $40

14:00 - Price rises to $2002.00
├── Position profit: +$30
├── Profit ($30) < Trail level ($40)
└── TRAILING STOP triggered - Close with $30 profit

Result: +$30 profit
Next day: Ready for new trade based on EMA signal
```

### When to Use C1

**Best For:**
- Traders who prefer simple, trend-following strategies
- Those who want limited exposure (one trade per day)
- Markets with clear directional trends

**Not Ideal For:**
- Ranging/choppy markets (EMA signals may whipsaw)
- Traders wanting multiple trades per day

---

## Changelog

- **v1**: Original grid + hedge strategy
- **v2**: Added profit pooling
- **v3**: Added grid trailing stop
- **v4**: Added incremental grid distance
- **v4.1**: 12 complete variations covering all feature combinations
- **v4.2**: Added A7 and B7 with dual trailing (hedge profit + loss trailing)
  - Fixed critical bug where grid trailing stop never triggered
  - Corrected logic: grid trail only applies when hedge NOT triggered
  - 14 total strategy variations
- **v5**: Added B8 and B9 with time filtering (4 modes, auto DST handling)
- **v6**: Enhanced B8 and B9 with comprehensive filters and controls
  - Added dual trading window mode
  - Added day-of-week filter
- **v7**: Bug fixes + Consistent trading windows for B8 and B9
  - **B8**: Incremental + No Hedge + Trail + Consistent Time Filter
  - **B9**: Incremental + Hedge + Pool + Trail + Consistent Time Filter
  - **CRITICAL BUG FIXES**:
    - **Trailing Stop Fix**: Fixed target ($10) now only checked when trailing is NOT active
      - Previously: Fixed target always triggered at $10, preventing trailing from ever activating
      - Now: Once peak profit reaches $20, trailing takes over and fixed target is ignored
      - Result: Profits can run beyond $10 when momentum is strong
    - **Active Position Management Fix**: Stop loss and trailing stop now checked every tick
      - Previously: When trading hours ended, active grids were not managed (no exit checks)
      - Now: Active positions are ALWAYS managed regardless of trading hours
      - Time filter only blocks opening NEW positions, not managing existing ones
    - **B8 No-Hedge Logic**: Removed basket profit pooling concepts (B8 has no hedge)
      - Clean grid-only logic with proper cycle reset between trades
    - **Direction Switch Fix (ALL hedge files: A3-A7, B3-B7, B9)**:
      - Previously: When stop loss hit WITHOUT hedge open, direction did NOT switch
      - Bug: Grid BUY hits stop loss → pause → next cycle opens BUY again (wrong!)
      - Now: Direction ALWAYS switches after stop loss (BUY → SELL or SELL → BUY)
      - Also calls ResetEngine() to ensure clean state for new cycle
      - Affects: A3, A4, A5, A6, A7, B3, B4, B5, B6, B7, B9 (11 files fixed)
    - **Trailing-Only Exit Fix (ALL trailing strategies)**:
      - Previously: Fixed profit target ($10) closed trades before trailing could activate
      - Now: NO fixed profit target for trailing strategies - wait for trailing or stop loss
      - Trailing-only files: A2, B2, B8 (no-hedge with trailing)
      - Hedge files with trailing (B6, B7, B9): Use trailing-only when hedge NOT triggered
      - Fixed target only used when hedge IS triggered (for recovery)
  - **NEW: Consistent Dual Window Schedule (MODE_DUAL_WINDOW)**:
    - **Monday-Friday**: Same windows - 11:00-15:30 + 17:30-19:30 UTC+3
    - **Saturday**: No trading (market closes at 01:00 UTC+3, before our windows)
    - **Sunday**: No trading (market closed)
    - GAP SKIPPED: 15:30-17:30 UTC+3 (all days)
    - Total: ~32.5 hours of optimized trading per week (6.5 hrs × 5 days)
  - **Design Decisions**:
    - **No extended Monday window**: Asian session (05:00-11:00) has lower quality trades
    - **No Saturday trading**: Market closes at 01:00 UTC+3, before our 11:00 window starts
    - **Consistency**: Same strategy behavior every weekday for predictable results
  - **Enhanced Dashboard** showing:
    - Consistent window information for all weekdays
    - Current window indicator (Window 1 or Window 2)
    - Overall trading status with clear day/time context
  - All features work year-round with automatic DST handling
  - 16 total strategy variations available
- **v8**: Added B10 with dynamic features for 24/7 trading
  - **B10**: Incremental + No Hedge + Dynamic Stop Loss + Trailing Only
  - **NEW FEATURES**:
    - **Dynamic Stop Loss**: Adjusts from $75-$300 based on day profit
      - If dayProfit <= $85: Use minimum $75
      - If dayProfit > $85: Use (dayProfit - $10), capped at $300
    - **Dynamic Pause After Stop Loss**: 0/15/30/45/60 minutes based on loss size
      - < $75: No pause (edge case)
      - $75-$149: 15 minutes (V10: was 5 minutes)
      - $150-$199: 30 minutes
      - $200-$249: 45 minutes
      - $250-$300: 60 minutes
    - **Daily Target**: Stop trading when day profit reaches target (default $200)
    - **Daily Loss Limit**: Stop trading when day loss reaches limit (default $500)
    - **Market Pause Buffers**: Optional pause after market open / before market close
    - **Direction Always Switches**: After every trade (profit or loss), direction alternates
  - **24/7 Trading**: No day/time filters - runs continuously year-round
  - **XAUUSD Market Hours Support**: Handles daily maintenance (00:00-01:00) and weekends
  - **BUG FIXES (B10)**:
    - **Realized P/L Tracking**: Day profit now uses actual balance difference after positions close (not floating P/L before close)
    - **Daily Flags Persistence**: Daily target/loss limit flags now persist through input changes (only reset on new day or full EA restart)
    - **Broker Compatibility**: Changed from hardcoded `ORDER_FILLING_IOC` to `SetTypeFillingBySymbol()` for auto-detection
    - **Removed MaxSpread**: Unnecessary copy-paste from other strategies (market pause buffers already handle high-spread periods)
    - **Pause Logic Fix**: Fixed bug where pause after stop loss never triggered (saved values before ResetEngine cleared them)
    - **Updated Pause Durations**: Added 5-minute pause for $75-$149 stop loss (was 0 minutes)
  - **NEW FEATURE (B10)**: Dynamic Daily Target based on loss thresholds
    - When day loss >= $200 → Daily target reduced to $50
    - When day loss >= $300 → Daily target reduced to $10
    - Once reduced, target stays reduced for rest of day (even if profit recovers)
    - Configurable thresholds via inputs: LossThreshold1/2, ReducedTarget1/2
  - **C1**: NEW EMA-based single trade strategy
    - Single lot, single trade per day
    - Entry: 1H candle open vs 50-day EMA (above=BUY, below=SELL)
    - Stop loss: 60% of investment (configurable)
    - Profit exit: Trailing stop only
    - Auto-close before market close
  - 18 total strategy variations available
- **v10 (Current)**: B10 sentinel-zero auto-scaling + pause + float fix
  - **SENTINEL-ZERO AUTO-SCALING (B10)**: 6 params now default to `0` = AUTO
    - Affected: `GridTrailStart`, `TrailStepBase`, `TrailStepMultiplier`,
      `MinTrailProfit`, `DailyTarget`, `DailyLossLimit`
    - Input `0` → base value × (`LotSize`/0.1) multiplier
    - Input `> 0` → use the entered value exactly, no further scaling
    - **Why**: Previously `DailyTarget`/`DailyLossLimit` were NOT scaled and the
      trailing params had to be scaled by hand. Two accounts on different lot sizes
      (e.g. 0.1 vs 0.3) desynced — the larger lot hit the un-scaled $200 target /
      $500 loss limit after only 1/N the price move, then stopped trading while the
      other kept going. Now, with all 6 at `0`, both accounts trade in lockstep.
  - **FLOAT-PRECISION FIX (B10)**: `GetLotMultiplier()` rounds to 2 decimals
    - `0.3 / 0.1` now returns exactly `3.00` instead of `2.9999996`
    - Prevents the two accounts flipping a trigger a tick apart at boundaries
  - **PAUSE DURATION UPDATE (B10)**: $75–$149 stop-loss tier now pauses **15 min**
    (was 5 min). Tier still scales with lot size.
- **v9**: B10 enhancements + C1 EMA fix
  - **B10 LOT-SCALED PARAMETERS**: All stop loss parameters now auto-scale based on lot size
    - Multiplier formula: `LotSize / 0.1`
    - Base values (for 0.1 lot): MinSL=$75, MaxSL=$300, SLThreshold=$85, SLCushion=$10
    - Example (0.2 lot = 2× multiplier): MinSL=$150, MaxSL=$600, etc.
    - Loss thresholds and reduced targets also scale
    - Pause time thresholds scale with lot size
  - **B10 DYNAMIC TRAILING STOP**: Trail step based on position count
    - Formula: `TrailStepBase + (positions - 1) × TrailStepMultiplier`
    - Default: 1 pos=$10, 2 pos=$19, 3 pos=$28, 4 pos=$37
    - Minimum profit floor ($10) after trailing activates
    - Prevents premature exits from noise with multiple positions
  - **NEW INPUT PARAMETERS (B10)**:
    - `TrailStepBase = 10.0` - Base trail step for 1 position
    - `TrailStepMultiplier = 9.0` - Additional step per extra position
    - `MinTrailProfit = 10.0` - Minimum profit floor after trailing starts
  - **REMOVED INPUT PARAMETERS (B10)**: Now auto-calculated based on lot size
    - MinStopLoss, MaxStopLoss, DynamicSLThreshold (now scaled from base values)
    - LossThreshold1/2, ReducedTarget1/2 (now scaled from base values)
  - **DASHBOARD UPDATES (B10)**: Shows lot multiplier and all scaled values
  - **C1 EMA FIX**: Fixed incorrect EMA calculation
    - **Bug**: EMA was using index 0 (current incomplete daily bar)
    - **Fix**: Now uses index 1 (last completed daily bar)
    - **Impact**: EMA value is now stable throughout the day, signals are consistent
    - Dashboard now shows which date the EMA is calculated from

---

## Support

For questions or issues, review the dashboard output in MetaTrader 5 which shows:
- Current floating P/L
- Recovery value
- Hedge status
- Grid trailing status
- All relevant parameters

Happy Trading!
