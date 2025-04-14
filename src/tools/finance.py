from src.lib.tool_runner import ToolConfig
from src.lib.tool_functions.finance import get_stock_price

get_stock_price_tool = ToolConfig(
    name="get_stock_price",
    parameters=[
        {
            "name": "stock_symbol",
            "type": "string",
            "description": "The stock ticker symbol for the company for which to retrieve the current price.",
            "required": True,
        },
    ],
    expected_response_format="A string containing the current stock price for a given symbol.",
    description="This tool retrieves the current stock price for a given stock symbol",
    function=get_stock_price
)