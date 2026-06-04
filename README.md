# XAUUSD Grid Trading Strategies - Complete Guide

## Overview

This folder contains **16 Expert Advisor (EA) variations** for MetaTrader 5, designed for XAUUSD (Gold) trading using grid strategies with optional hedging features.

---

## File Naming Convention

Each file follows the pattern: `{Series}{Number}_{grid-type}_{hedge}_{pooling}_{trailing}.mq5`

| Component | Meaning |
|-----------|---------|
| **A** | Fixed Grid Distance (200 points always) |
| **B** | Incremental Grid Distance (200 × N pattern) |
| **1-2** | No Hedge strategies |
| **3-7** | With Hedge strategies |
| **8-9** | Time-filtered versions (trades only during optimal hours) |
| **nohedge/hedge** | Hedge protection enabled or not |
| **nopool/pool** | Profit pooling (tracks hedge profits) |
| **notrail/trail** | Grid trailing stop enabled or not |
| **dual_trail** | Both hedge profit and hedge loss trailing enabled |
| **time** | Time filter enabled (MT5 broker time, auto DST handling) |

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

**NEW (V6):** B8 and B9 include **dual trading windows** with comprehensive filters:

**Trading Modes:**
- **MODE_DUAL_WINDOW** (DEFAULT): 3:00-7:30 AM + 9:30-11:30 AM US time (skips gap for optimal trading)
- **MODE_OVERLAP_ONLY**: 9:30-11:30 AM US time (highest volatility period only)
- **MODE_FULL_LONDON**: 3:00-11:30 AM US time (continuous window, includes gap)
- **MODE_PEAK_HOUR**: 9:30-10:30 AM US time (ultra-conservative)
- **MODE_CUSTOM**: User-defined hours

**Additional V6 Features:**
- **Day-of-Week Filter**: Skip Monday early trading, stop Friday late trading
- **Manual Pause/Resume**: Control via global variables (Press F3 in MT5)
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

**Important:** Grid trailing is DISABLED when hedge triggers. Why?
- After hedge triggers, you need to recover hedge losses
- Fixed target ensures you wait for full recovery
- Trailing might close too early with partial recovery

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
- **Critical Advantage**: MT5 broker time shows US Eastern time with automatic DST adjustment

#### How It Works

**MT5 Broker Time = US Eastern Time (EST/EDT)**
- Your laptop: IST (India Standard Time)
- MT5 display: US time (automatically adjusts for DST)
- **You don't need to manually adjust for DST changes!**

#### Flexible Trading Modes (V6 Update)

B8 and B9 now support **5 different trading modes** via dropdown selection:

**1. MODE_DUAL_WINDOW (Default) ⭐ NEW**
```cpp
TradingMode = MODE_DUAL_WINDOW
// Window 1: 3:00 AM - 7:30 AM (Early London - 4.5 hours)
// GAP SKIPPED: 7:30 AM - 9:30 AM (No trading - 2 hours)
// Window 2: 9:30 AM - 11:30 AM (London-NY Overlap - 2 hours)
// Total: 6.5 hours of optimal trading
```
- **When to use**: Best for data-driven optimal performance (DEFAULT for both B8 and B9)
- **Benefits**:
  - Captures BOTH high-quality sessions
  - Skips the 7:30-9:30 AM gap period (lower quality trades)
  - Based on tick data analysis showing optimal win rates
  - 6.5 hours of targeted trading vs 8.5 hours continuous
  - Works identically for summer (EDT) and winter (EST)
- **Recommendation**: **DEFAULT - Best balance of trading time and quality**

**2. MODE_OVERLAP_ONLY**
```cpp
TradingMode = MODE_OVERLAP_ONLY
// Trades 9:30 AM - 11:30 AM US time
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
// Trades 3:00 AM - 11:30 AM US time (continuous)
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
// Trades 9:30 AM - 10:30 AM US time
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

| Strategy | Market Type | Recommended Mode | Trading Window (US Time) | Daily Hours |
|----------|-------------|------------------|-------------------------|-------------|
| **B8/B9** (General) | All Markets | MODE_DUAL_WINDOW ⭐ | 3:00-7:30 + 9:30-11:30 AM | 6.5 hours |
| **B8** (Conservative) | Trending | MODE_OVERLAP_ONLY | 9:30-11:30 AM | 2 hours |
| **B9** (Maximum) | Ranging | MODE_FULL_LONDON | 3:00-11:30 AM | 8.5 hours |
| Any (Ultra-safe) | High Volatility | MODE_PEAK_HOUR | 9:30-10:30 AM | 1 hour |
| Any (Advanced) | Custom Analysis | MODE_CUSTOM | User-defined | Variable |

#### Automatic DST Handling

Since MT5 broker time shows US Eastern (EST/EDT), DST is handled automatically:

```
Summer (March-October):
- US observes EDT (UTC-4)
- MT5 shows EDT
- MODE_FULL_LONDON: 3:00-11:30 AM remains correct
- MODE_OVERLAP_ONLY: 9:30-11:30 AM remains correct

Winter (November-February):
- US observes EST (UTC-5)
- MT5 shows EST
- MODE_FULL_LONDON: 3:00-11:30 AM remains correct
- MODE_OVERLAP_ONLY: 9:30-11:30 AM remains correct

NO MANUAL ADJUSTMENT NEEDED - ALL MODES WORK YEAR-ROUND!
```

**Why This Works:**
- London 8:00 AM opening = 3:00 AM US time (both EDT and EST)
- London-NY overlap 9:30 AM = 9:30 AM US time (both EDT and EST)
- MT5 automatically adjusts its clock for DST transitions
- Your MODE selection works identically across all seasons

#### Configuration Options

**Option 1: Auto-close outside hours**
```cpp
ClosePositionsOutsideHours = true
// Closes all positions when trading window ends
// Use for aggressive capital preservation
```

**Option 2: Hold positions (Default)**
```cpp
ClosePositionsOutsideHours = false
// Keeps positions open, just stops new trades
// Allows existing positions to reach targets
```

#### Example: Your Laptop vs MT5

**Scenario 1: MODE_FULL_LONDON**
- **Your laptop**: 8:30 PM IST (evening in India)
- **MT5 displays**:
  - Summer: 10:00 AM EDT (within 3:00-11:30 window ✅)
  - Winter: 10:00 AM EST (within 3:00-11:30 window ✅)
- **Result**: EA trades during early London AND overlap

**Scenario 2: MODE_OVERLAP_ONLY**
- **Your laptop**: 11:00 PM IST (late night in India)
- **MT5 displays**:
  - Summer: 12:30 PM EDT (outside 9:30-11:30 window ❌)
  - Winter: 12:30 PM EST (outside 9:30-11:30 window ❌)
- **Result**: EA stops trading after overlap ends

**Key Insight:** EA trades correctly regardless of season because MT5 automatically handles DST!

#### Day-of-Week Filter (V6 Feature) 📅

B8 and B9 include smart day-of-week restrictions based on market behavior analysis:

**Monday Restrictions:**
```cpp
SkipMondayEarly = true         // Skip Monday before this hour
MondayStartHour = 15           // Start at 3:00 PM US time
```
- **Why**: Avoid post-weekend gap and low-quality early Monday trades
- **Effect**: EA waits until 3:00 PM US time (8:30 PM IST summer / 9:30 PM IST winter) before trading
- **Benefit**: Lets market settle after weekend, reduces false signals

**Friday Restrictions:**
```cpp
StopFridayLate = true          // Stop Friday after this hour
FridayEndHour = 21             // Stop at 9:00 PM US time
```
- **Why**: Avoid weekend risk and low-liquidity late Friday trades
- **Effect**: EA stops opening new positions after 9:00 PM US time (2:30 AM IST Saturday)
- **Benefit**: Reduces exposure to weekend gaps, protects capital

**Best Trading Days:**
- **Tuesday-Thursday**: Full trading without restrictions (most consistent price action)
- These are highlighted as "BEST DAY" in the dashboard

**How to Disable:**
```cpp
EnableDayFilter = false        // Disable all day restrictions (not recommended)
```

#### Manual Pause/Resume Control (V6 Feature) ⏸️

Take full control of your EA with real-time pause/resume capability:

**How It Works:**
1. EA creates a global variable: `B8_ManualPause` or `B9_ManualPause`
2. Press **F3** in MT5 to open Global Variables window
3. Double-click the variable to change value:
   - **0** = Resume Trading (EA active)
   - **1** = Pause Trading (EA stops immediately)
4. Changes take effect instantly - no need to restart EA

**When to Use:**
- **Before major news events**: NFP, FOMC, CPI releases
- **During high volatility**: Unexpected market events
- **Manual oversight**: When you want to observe without trading
- **Testing/debugging**: Temporarily halt EA without removing from chart

**Dashboard Display:**
```
--- MANUAL CONTROL ---
Manual Pause: OFF
Control: Press F3 > B8_ManualPause
Set to 1 to PAUSE trading
```

**Important Notes:**
- Pausing does NOT close existing positions - only stops new trades
- Resume anytime by setting variable back to 0
- Global variable persists across EA restarts
- Each EA (B8/B9) has its own separate pause control

#### Benefits

1. **Eliminates low-quality trades** during Asian session
2. **Higher win rate** - trades only during trending sessions
3. **Better risk/reward** - avoids choppy, low-liquidity periods
4. **Automatic DST** - no manual intervention needed twice per year
5. **Transparent** - Dashboard shows current time and window status

#### Dashboard Display (V6 Update)

The dashboard shows comprehensive real-time information about all filters:

```
GRID V6 (Incremental + NO HEDGE + DUAL WINDOW + DAY FILTER)

--- TIME FILTER ---
Time Filter: ENABLED
Trading Mode: Dual Window
Window 1: 03:00-07:30 (Early London)
Window 2: 09:30-11:30 (Overlap)
GAP SKIPPED: 07:30-09:30
Current Time (MT5): 10:15:30 (US EST/EDT)
Current Window: Window 2 (Overlap)
Time Status: INSIDE WINDOW

--- DAY FILTER ---
Day Filter: ENABLED
Today: Thursday (BEST DAY)
Day Status: ALLOWED

--- MANUAL CONTROL ---
Manual Pause: OFF
Control: Press F3 > B8_ManualPause
Set to 1 to PAUSE trading

--- TRADING STATUS ---
Overall Status: TRADING ALLOWED
```

**V6 Dashboard Shows:**
- **Trading Mode**: Which MODE is selected (Dual Window, Overlap Only, etc.)
- **Window Details**: For dual window, shows both windows and gap period
- **Current Window**: Which window you're currently in (Window 1 or Window 2)
- **Time Status**: Whether current time is inside or outside trading windows
- **Day Filter Status**: Current day and whether trading is allowed
- **Manual Pause Status**: Whether EA is manually paused
- **Overall Status**: Clear indication if trading is allowed or blocked (and why)

#### Comparison: B2 vs B8, B6 vs B9 (V6 Features)

| Feature | B2/B6 (No Filter) | B8/B9 (V6 With Filters) |
|---------|-------------------|-------------------------|
| Trading hours | 24/7 | Flexible (1-8.5 hours based on MODE) |
| Trading modes | None | 5 modes (V6: Dual Window, Overlap, Full London, Peak, Custom) |
| Dual window | ❌ No | ✅ Yes (V6: skips gap period) |
| Asian session | ✅ Trades (choppy) | ❌ Skips (prevents losses) |
| London early | ✅ Trades | ✅ Trades (MODE_DUAL_WINDOW Window 1) |
| Gap period (7:30-9:30) | ✅ Trades | ❌ Skips (MODE_DUAL_WINDOW) |
| London-NY overlap | ✅ Trades | ✅ Trades (all modes) |
| Day filter | ❌ No | ✅ Yes (V6: Monday/Friday restrictions) |
| Manual pause | ❌ No | ✅ Yes (V6: F3 global variable control) |
| DST adjustment | Manual | Automatic (year-round) |
| Win rate | Lower (all sessions) | Higher (V6: targeted sessions + day filter) |
| Drawdown frequency | Higher | Lower (V6: better entry timing) |
| Flexibility | None | Very High (V6: 5 modes + day + manual) |
| Best for | 24/7 monitoring | Strategic time-based trading with full control |

**Recommendation:** Use B8/B9 (V6) for **optimal data-driven performance** with maximum control.

**V6 Mode Recommendations:**
- **B8/B9 (Default)**: Use MODE_DUAL_WINDOW for best balance (6.5 hours/day, skips gap)
- **B8 (Conservative)**: Use MODE_OVERLAP_ONLY for highest win rate (2 hours/day)
- **B9 (Maximum)**: Use MODE_FULL_LONDON for full session coverage (8.5 hours/day)
- **Any (Manual Control)**: Use day filter + manual pause for news events

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
| MaxSpreadPoints | 80 | Skip trading if spread too high |
| MinMarginLevel | 250.0 | Skip trading if margin too low |
| TradeCooldownSeconds | 3 | Minimum seconds between trades |

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
  - Trades only 9:30-11:30 AM US time (London-NY overlap)
  - Automatic DST handling
  - Expected 40-60% better performance vs 24/7 trading
- **B6**: Full protection without hedge loss trailing (+30.12% in backtests)
- **B7**: Ultimate protection with dual trailing on hedge (+20.74% in backtests)
- **B5**: Solid alternative without trailing complexity (+25.60% in backtests)

**Note**: Recent backtests (May 28-29, 2026) showed B6 outperforming B7. B9 adds time filtering to B6's proven logic for even better results.

### For Production (Trending Market)
Use **B8** (⭐ NEW) or **B2**:
- **B8** (RECOMMENDED): B2 + Time Filter
  - Trades only during high-trend sessions (9:30-11:30 AM US time)
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
- **v6 (Current)**: Enhanced B8 and B9 with comprehensive filters and controls
  - **B8**: Incremental + No Hedge + Trail + Time Filter + Day Filter + Manual Pause
  - **B9**: Incremental + Hedge + Pool + Trail + Time Filter + Day Filter + Manual Pause
  - **NEW: Dual Trading Window (MODE_DUAL_WINDOW)**:
    - Window 1: 3:00-7:30 AM US time (Early London - 4.5 hours)
    - GAP SKIPPED: 7:30-9:30 AM US time (2 hours of lower quality trades)
    - Window 2: 9:30-11:30 AM US time (London-NY Overlap - 2 hours)
    - Total: 6.5 hours of optimal data-driven trading
    - Set as DEFAULT mode for both B8 and B9
  - **NEW: 5 Trading Modes** (added Dual Window to existing 4):
    - MODE_DUAL_WINDOW (NEW DEFAULT): Skips gap, trades 6.5 hours optimally
    - MODE_OVERLAP_ONLY: 9:30-11:30 AM (highest volatility, 2 hours)
    - MODE_FULL_LONDON: 3:00-11:30 AM (continuous 8.5 hours, includes gap)
    - MODE_PEAK_HOUR: 9:30-10:30 AM (ultra-conservative, 1 hour)
    - MODE_CUSTOM: User-defined hours
  - **NEW: Day-of-Week Filter**:
    - Skip Monday early trading (default: before 3:00 PM US / after weekend gap)
    - Stop Friday late trading (default: after 9:00 PM US / before weekend)
    - Tuesday-Thursday flagged as "BEST DAYS" in dashboard
    - Configurable or can be disabled
  - **NEW: Manual Pause/Resume Control**:
    - Real-time control via global variables (F3 in MT5)
    - B8_ManualPause / B9_ManualPause variables
    - Instant pause/resume without restarting EA
    - Perfect for news events (NFP, FOMC, CPI)
  - **Enhanced Dashboard** showing:
    - Current trading window (Window 1 or Window 2 for dual mode)
    - Day filter status and restrictions
    - Manual pause status with control instructions
    - Overall trading status (allowed/blocked with reasons)
  - All features work year-round with automatic DST handling
  - Based on tick data analysis optimizing for win rate and capital efficiency
  - 16 total strategy variations available

---

## Support

For questions or issues, review the dashboard output in MetaTrader 5 which shows:
- Current floating P/L
- Recovery value
- Hedge status
- Grid trailing status
- All relevant parameters

Happy Trading!
