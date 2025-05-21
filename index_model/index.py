import datetime as dt
import pandas as pd

        
class IndexModel:
        
    def __init__(self):
          
        self.price_data = pd.read_csv("./data_sources/stock_prices.csv", parse_dates=["Date"], index_col=["Date"], dayfirst=True)
        self.index_values: pd.DataFrame
        
        """
        Determines the index constituents and assigns weights based on market cap.
        
        Logic:
        - Assumes market cap = stock price (i.e., each company has 1 share outstanding)
        - Selects top 3 stocks by market cap from previous business day
        - Assigns 50% of index to top stock, 25% to next two
        - Calculates number of shares to hold in each based on current prices
        
        Returns:
            pd.DataFrame: Stock-wise number of shares to hold
        """

    def sort_index(self, date: dt.date, current_index_value: float) -> pd.DataFrame:
        relevant_price_data = self.price_data.loc[str(prev_business_day(date))]
        # assume all companies have 1 share outstanding: price = marketCap
        largest_market_caps = sorted(list(relevant_price_data.values), reverse=True)[:3]
        current_price_data = self.price_data.loc[str(date)]
        number_shares = [float(0.5 / y * current_index_value if x == largest_market_caps[0]
                               else 0.25 / y * current_index_value if x in largest_market_caps[1:]
                               else 0
                               )
                         for x, y in zip(relevant_price_data.values, current_price_data.values)]
        return pd.DataFrame(data=number_shares, index=self.price_data.columns)
    
    
        """
        Calculates the daily index value from start_date to end_date.
        The index is:
        - Initialized at 100 on start_date
        - Updated daily based on portfolio market value
        - Rebalanced at the start of each new month using top 3 stocks

        Stores the result in self.index_values
        """

    def calc_index_level(self, start_date: dt.date, end_date: dt.date):
        dates = [start_date]
        index_values = [100.0]
        number_shares = self.sort_index(start_date, index_values[0])
        while start_date < end_date:
            previous_day_market_value = float(self.price_data.loc[str(start_date)].dot(number_shares).values[0])
            actual_day_market_value = float(self.price_data.loc[str(next_business_day(start_date))].dot(number_shares).values[0])
            return_rate = actual_day_market_value / previous_day_market_value
            index_value = index_values[-1] * return_rate
            start_date = next_business_day(start_date)
            index_values.append(index_value)
            dates.append(start_date)
            # get new index constituents at the beginning of month
            if start_date.month != prev_business_day(start_date).month:
                number_shares = self.sort_index(start_date, index_value)

        self.index_values = pd.DataFrame({"Date": dates, "index_level": index_values})
        return
        """
        Exports the index time series to a CSV file.

        Args:
            file_name (str): Destination file path
        """
    def export_values(self, file_name: str):
        self.index_values.to_csv(file_name, index=False)
        return

    """
    Advances the given date to the next business day.
    Skips weekends (Saturday/Sunday). Assumes no holidays.

    Returns:
        dt.date: Next valid trading day
    """

def next_business_day(date: dt.date) -> dt.date:
    date += dt.timedelta(days=1)
    return date + dt.timedelta(days=(7 - date.weekday()) % 7) if date.weekday() >= 5 else date
    
    """
    Moves the given date back to the previous business day.
    Skips weekends (Saturday/Sunday). Assumes no holidays.

    Returns:
        dt.date: Most recent valid trading day
    """
    
def prev_business_day(date: dt.date) -> dt.date:
    date -= dt.timedelta(days=1)
    while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        date -= dt.timedelta(days=1)
    return date