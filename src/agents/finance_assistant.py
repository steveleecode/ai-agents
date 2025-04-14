from src.lib.agent_runner import AgentConfig
from src.tools.finance import get_stock_price_tool

finance_assistant_agent = AgentConfig(
    name="finance_assistant",
    background="""
        You are a finance assistant.
        You are responsible for summarizing and answering questions about financial matters around the world
    """,
    tools=[get_stock_price_tool],
    expected_output="A text summary or answer to the question asked about financial matters",
)