import os
from openai import OpenAI
import streamlit as st

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
)

def chat_completion(messanges: list[dict]) -> dict:
    """Generates a chat completion using OpenAI API.

    Args:
        messanges (list[dict]): A list of dictionaries containing the messages for the chat.

    Returns:
        dict: The response from the OpenAI API.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messanges,
        temperature=0,
        max_tokens=5000,
    )
    return {
        "response": response.choices[0].message.content,
        "tokens": int(response.usage.total_tokens),
    }