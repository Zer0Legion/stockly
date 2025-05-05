import yfinance as yf
from pydantic import BaseModel


class StockRequestInfo(BaseModel):
    exchange: str
    ticker: str

    @property
    def full_name(self):
        return f"{self.exchange}:{self.ticker}"

    @property
    def long_name(self) -> str:
        """Return long name of stock."""

        ticker = yf.Ticker(self.ticker)
        return ticker.info.get("longName", "Unknown Stock")
