from src.lib.external.openai_api import chat_completion
from src.agents.finance_assistant import finance_assistant_agent

message_history = []

system_message = f"""
    You are an AI Assistant for Stephen Lee, a student interested in software engineering, computer science, and biotechnology/bioinformatics.
    You are expected to provide helpful and informative responses to questions related to these fields.
    You should also be able to assist with general knowledge questions and provide guidance on various topics.
    You are chatting with Stephen, you should speak to him in an informal and friendly manner.
"""

message_history.append({"role": "system", "content": system_message})

def handle_input(input, status_callback=None):

    message_history.append({"role": "user", "content": input})

    agentic_response = agentic_action(message_history, status_callback)

    if agentic_response['context_for_assistant']:
        message_history.append({
            "role": "assistant", 
            "content": f"""
                Here is some additional context for me as an assistant.

                <context>
                {agentic_response['context_for_assistant']}
                </context>
            """
        })

    # Generate chat response
    chat_response = chat_completion([
        {
            "role": "system",
            "content": f"""
                You are an chatbot for Stephen Lee, a student interested in software engineering, computer science, and biotechnology/bioinformatics.
                You need to provide a response based on the current conversation.
                We have recieved his previous message and have taken the following actions: {agentic_response}
                Based on the message history provided and the actions that have been taken, how should we respond to Stephen?
                You are chatting with Stephen, you should speak to him in an informal and friendly manner.
            """
        },
        {
            "role": "user",
            "content": format_messages_to_string(message_history)
        },
    ])

    # Add the message to the message history
    message_history.append({
        "role": "system",
        "content": chat_response['response']
    })

    return chat_response

def agentic_action(messanges, status_callback=None):

    messanges_string = format_messages_to_string(messanges)

    agents = [finance_assistant_agent]

    agents_info = [agent.get_agent_info() for agent in agents]

    system_message = f"""
        You are an AI Agent working for Stephen Lee's Assistant. (No need to address this directly to the user)
        You need to determine the intent of the user based on teh current conversation, and determine if any actions need to be passed to the rest of the agents.
        Here is a JSON list of the agents that you can pass to {agents_info}
        Do not try to delegate an action to an agent that doesnt exist.

        You can also choose to handle the action yourself if you are able to do so.
        You should format your response as follows:
         - If you are delegating an action to an agent, use the following format (FOLLOW THE JSON FORMAT FOR PARAMETERS): "DELEGATE_ACTION:::AGENT_NAME:::ACTION_NAME:::ACTION_PARAMETERS"
         - If you need more information from the user, provide a responese that asks for the information: "REQIEST_INFO:::QUESTION"
         - If no action is needed, provide a "NO_ACTION" response.
         - If you know what the answer to the question is, provide an answere to the question: "ANSWER:::answer"

        Do not respond to the user directly, you must respond to the assistant who will then respond to the user. Do not address the user directly

    """

    res = chat_completion([
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": messanges_string
        },
    ])

    if res['response'] == "NO_ACTION":
        return {
            "context_for_assistant": None,
            "response": "NO_ACTION"
        }
    
    elif res['response'].startswith("REQUEST_INFO"):
        question = res['response'].split(":::")[1]
        return {
            "context_for_assistant": None,
            "response": f"REQUEST_INFO::: {question}"
        }
    elif res['response'].startswith('DELEGATE_ACTION'):
        action = res['response']

        action_parts = action.split(':::')

        agent_name = action_parts[1]
        agent_prompt = action_parts[2]
        action_parameters = action_parts[3]

        # Find the agent
        agent = [agent for agent in agents if agent.name == agent_name][0]

        # Find the action
        action = [action for action in agent.tools if action.name == agent_prompt][0]

        # Run the action
        result = action.run_tool(action_parameters, status_callback=status_callback)

        if result:
            print('Agent response: ', result)
            return {
                "context_for_assistant": result.context_for_assistant,
                "response": result.result,
            }
        else:
            return {
                "context_for_assistant": None,
                "response": "NO_ACTION"
            }
    elif res['response'].startswith('ANSWER'):
        answer = res['response'].split(':::')[1]
        return {
            "context_for_assistant": None,
            "response": f"ANSWER::: {answer}"
        }

def format_messages_to_string(messages):
    """
    Format the messages to a string for the chat completion API.
    """
    formatted_messages = []
    for message in messages:
        if message['role'] == 'user':
            formatted_messages.append(f"User: {message['content']}")
        elif message['role'] == 'assistant':
            formatted_messages.append(f"Assistant: {message['content']}")
        elif message['role'] == 'system':
            formatted_messages.append(f"System: {message['content']}")

    return "\n".join(formatted_messages)