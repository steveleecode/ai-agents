from src.lib.tool_runner import ToolResult
import yfinance as yf

def get_stock_price(params: dict) -> ToolResult:

    stock_symbol = params.get("stock_symbol")

    stock_data = yf.Ticker(stock_symbol)
    stock_price = stock_data.history(period="1d")["Close"].values[0]
    
    return ToolResult(
        result= f"The current stock price for {stock_symbol} is ${stock_price}", 
        context_for_assistant= f"{stock_symbol} Stock Price: {stock_price}",
    )