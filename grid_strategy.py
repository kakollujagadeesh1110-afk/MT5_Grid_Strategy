"""
Grid Trading Strategy
A simple grid-based trading strategy that places buy and sell orders at regular intervals.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

class GridStrategy:
    def __init__(self, symbol, grid_levels=5, grid_size=2.0, initial_investment=1000):
        """
        Initialize the grid strategy.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            grid_levels: Number of grid levels (default: 5)
            grid_size: Percentage distance between grid levels (default: 2%)
            initial_investment: Initial capital for trading
        """
        self.symbol = symbol
        self.grid_levels = grid_levels
        self.grid_size = grid_size
        self.initial_investment = initial_investment
        self.buy_orders = []
        self.sell_orders = []
        
    def connect_mt5(self):
        """Connect to MetaTrader 5"""
        if not mt5.initialize():
            print("Failed to initialize MT5")
            return False
        return True
    
    def get_current_price(self):
        """Get the current price of the symbol"""
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None
        return tick.last
    
    def calculate_grid_levels(self, current_price):
        """Calculate buy and sell grid levels"""
        price_step = current_price * (self.grid_size / 100)
        
        buy_levels = []
        sell_levels = []
        
        # Generate grid levels below and above current price
        for i in range(1, self.grid_levels + 1):
            buy_levels.append(current_price - (price_step * i))
            sell_levels.append(current_price + (price_step * i))
        
        return buy_levels, sell_levels
    
    def place_buy_order(self, price, volume=0.1):
        """Place a pending buy order at specified price"""
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "Grid Buy Order",
            "type_time": mt5.ORDER_TIME_GTC,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.buy_orders.append({
                'price': price,
                'volume': volume,
                'timestamp': datetime.now()
            })
            print(f"Buy order placed at {price}")
            return True
        else:
            print(f"Buy order failed: {result.comment}")
            return False
    
    def place_sell_order(self, price, volume=0.1):
        """Place a pending sell order at specified price"""
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "Grid Sell Order",
            "type_time": mt5.ORDER_TIME_GTC,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.sell_orders.append({
                'price': price,
                'volume': volume,
                'timestamp': datetime.now()
            })
            print(f"Sell order placed at {price}")
            return True
        else:
            print(f"Sell order failed: {result.comment}")
            return False
    
    def setup_grid(self):
        """Set up the initial grid orders"""
        current_price = self.get_current_price()
        if current_price is None:
            print("Could not get current price")
            return False
        
        print(f"Current price: {current_price}")
        
        buy_levels, sell_levels = self.calculate_grid_levels(current_price)
        volume = self.initial_investment / (current_price * self.grid_levels * 2)
        
        # Place buy orders
        for buy_price in buy_levels:
            self.place_buy_order(buy_price, volume)
        
        # Place sell orders
        for sell_price in sell_levels:
            self.place_sell_order(sell_price, volume)
        
        print(f"Grid setup complete with {len(buy_levels)} buy and {len(sell_levels)} sell orders")
        return True
    
    def get_strategy_summary(self):
        """Get summary of the strategy"""
        summary = {
            'symbol': self.symbol,
            'grid_levels': self.grid_levels,
            'grid_size': f"{self.grid_size}%",
            'initial_investment': self.initial_investment,
            'buy_orders_placed': len(self.buy_orders),
            'sell_orders_placed': len(self.sell_orders),
        }
        return summary


def main():
    """Example usage of the grid strategy"""
    strategy = GridStrategy(
        symbol="AAPL",           # Stock symbol
        grid_levels=5,           # 5 levels above and below current price
        grid_size=2.0,           # 2% distance between levels
        initial_investment=1000  # $1000 investment
    )
    
    # Connect to MT5
    if strategy.connect_mt5():
        # Setup the grid
        strategy.setup_grid()
        
        # Print strategy summary
        summary = strategy.get_strategy_summary()
        print("\n=== Grid Strategy Summary ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
    
    # Shutdown MT5
    mt5.shutdown()


if __name__ == "__main__":
    main()
