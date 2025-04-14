from datetime import datetime
from pydantic import BaseModel, ValidationError, Field
from src.lib.external.openai_api import chat_completion
from typing import *
import json

class ToolResult(BaseModel):
    result: Any
    context_for_assistant: Any = None

class ToolConfig(BaseModel):
    name: str = Field(..., description="The name of the tool.")
    parameters: List[Dict] = Field(..., description="The parameters (name, type, description) that the tool needs to be used.")
    expected_response_format: str = Field(..., description="The expected response format of the tool.")
    description: str = Field(..., description="The description of the tool's functionalty.")
    function: Callable

    def get_tool_info(self):
        return {
            "name": self.name,
            "parameters": self.parameters,
            "expected_response_format": self.expected_response_format,
            "description": self.description
        }
    
    def run_tool(self, parameters: List[Dict], status_callback: Callable[[str], None] = None) -> ToolResult:
        try:
            if status_callback:
                # Call the status callback function with the tool name with only alphanumeric characters
                # to avoid any issues with special characters or spaces
                status_callback(f"Running tool: { "".join([char for char in self.name if char.isalnum()])}")

            #Ensure the parameters are in the correct format
            if isinstance(parameters, str):
                parameters = json.loads(parameters)

            result = self.function(parameters)

            return result
        except Exception as e:
            print(f"Error running tool {self.name}: {e}")
            return ToolResult(result=f"Error running tool: {str(e)}")