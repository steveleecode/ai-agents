from pydantic import BaseModel, Field
import json
from datetime import datetime
from src.lib.external.openai_api import chat_completion
from typing import *

class AgentConfig(BaseModel):
    name: str = Field(..., description="The name of the agent.")
    background: str = Field(..., description="The background information for the agent.")
    tools: List = Field(..., description="The tools that the agent can use.")
    expected_output: str = Field(..., description="The expected output of the agent.")

    instruction_message: str = ""
    agent_message_history: List[Dict[str, str]] = []

    def get_agent_info(self):
        return {
            "agent_name": self.name,
            "actions": self.tools,
        }

    def run_agent(self, instruction_message: str, status_callback: Callable[[str], None] = None) -> Dict[str, Union[str, bool]]:
        system_message = f"""
            You are {self.name}, an AI agent working with the following background {self.background}.
            The current timestamp is {datetime.now().isoformat()}
            Tou can work with dates even if they are n the past
            Do not throw an error if the user specifies a date in the past as part of the instruction.
            You have the following tools available (JSON format): {self.tools}
            Using the provided user message, you should do what is required to provide the following expected output: {self.expected_output}.
            Definet ool parameters in JSON format as shown in the tools list
            If you are unsure how to proceed, return an "ERROR_RESULT" response.
            If you need to ask the end user a question, return a "FINAL_RESULT:::(question)" responnse.
            Here is how you should respond:
                if the response is the final result:FINAL_RESULT:::result_content
                if the response is an error: ERROR_RESULT:::error_content
                if the response is a tool_action: TOOL_ACTION:::tool_name:::tool_parameters
            Always adhere to this strict format. Responses outside these guidelines will not be processed
        """
        self.agent_message_history.append({
            "role": "system", 
            "content": system_message
        })

        self.agent_message_history.append({
            "role": "user", 
            "content": self.instruction_message
        })

        #Run the chat completion
        chat_res = chat_completion(self.agent_message_history)

        if chat_res['response'].startswith('TOOL_ACTION'):
            tool_name, tool_parameters = chat_res['response'].split(':::')[1:3]

            print("Calling tool: ", tool_name, ' with parameters: ', tool_parameters)

            #Find the tool

            tool = [tool for tool in self.tools if tool['name'] == tool_name][0]
            print('Found tool: ', tool)

            parameters_dict = json.loads(tool_parameters)

            tool_res = tool.run_tool(parameters_dict, status_callback=status_callback)

            step_res = {
                "should_continue": True,
                "step_result": tool_res['result'],
                "context_for_assistant": tool_res['context_for_assistant']
            }

            return step_res
        elif chat_res['response'].startswith('FINAL_RESULT'):
            final_result = chat_res['response'].split(':::')[1]

            step_res = {
                "should_continue": False,
                "step_result": final_result,
                "context_for_assistant": None
            }
            return step_res
        elif chat_res['response'].startswith('ERROR_RESULT'):
            error_result = chat_res['response'].split(':::')[1]

            step_res = {
                "should_continue": False,
                "step_result": error_result,
                "context_for_assistant": None
            }

            return step_res