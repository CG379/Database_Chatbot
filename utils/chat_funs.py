import tiktoken
import streamlit as st
from utils.api_funs import send_api_request, execute_fun
from utils.config import AI_MODEL

def run_chat(messages, funs):
    if "live_chat" not in st.session_state:
        st.session_state["live_chat"] = [{"role": "system", "content": "Hello! How can I assist you?"}]
    internal_chat_history = st.session_state["live_chat"].copy()
    chat_response = send_api_request(messages, funs)
    system_message = chat_response.json()["choices"][0]["message"]

    if system_message["role"] == "system":
        internal_chat_history.append({"role": "system", "content": system_message})


def prep_menuebar_data(db_schema_dict):
    # Prepare the data for the menubar
    menubar_data = {}
    for table in db_schema_dict:
        schema_name = table["schema_name"]
        table_name = table["table_name"]
        col_names = table["column_names"]

        if schema_name not in menubar_data:
            menubar_data[schema_name] = {}
        
        menubar_data[schema_name][table_name] = col_names
    return menubar_data

def clear_chat_history():
    """ Clear the chat history stored in the Streamlit session state """
    del st.session_state["live_chat_history"]
    del st.session_state["full_chat_history"]
    del st.session_state["api_chat_history"]

def count_tokens(text):
    """ to make sure I don't go over free limit"""
    # In case this breaks
    if not isinstance(text, str):
        return 0
    # TODO: make model a global var or env file var or something
    encoding = tiktoken.encode_for_model(AI_MODEL)
    total_tokens = len(encoding.encode(text))

    return total_tokens


