import streamlit as st
# Use 4o-mini 3 requests perr minute
from utils.config import MAX_TOKENS_ALLOWED, MAX_MESSAGES_TO_OPENAI, TOKEN_BUFFER, db_credentials
from utils.chat_funs import run_chat, count_tokens, prep_menuebar_data, clear_chat_history
from utils.system_prompts import get_final_prompt
from utils.fun_calling import funs
from utils.helper_funs import save_conv_history
from utils.db_funs import db_schema_dict


if __name__ == '__main__':
    # TODO: Connect to db
    
    # Menu bar
    # TODO: Make fun for preping menue bar data
    menu_bar = prep_menuebar_data(db_schema_dict)
    

    ## Postgress database viewer

    st.sidebar.title("Database Viewer")
    # Dropdown menue
    selected_schema = st.sidebar.selectbox("Select Schema", list(menu_bar.keys()))
    selected_table = st.sidebar.selectbox("Select Table", list(menu_bar[selected_schema].keys()))
    # Show columns of table
    st.sidebar.subheader(f"Columns of {selected_table}")
    for col in menu_bar[selected_schema][selected_table]:
        # TODO: Check other ofrmats than checkboxes
        checked_box = st.sidebar.checkbox(f" {col}")
    

    ## Button for saving convo
    if st.sidebar.button("Save Conversation"):
        # Save conversation: st.session_state["full_chat_history"]
        saved_file_path = save_conv_history(st.session_state["full_chat_history"])
        st.sidebar.success(f"Conversation saved in {saved_file_path}")
        st.sidebar.markdown(f"Download here: [Open Conversation]({saved_file_path})")

    ## clear chat button
    if st.sidebar.button("Clear Chat"): 
        # save conversation 
        save_conv_history(st.session_state["full_chat_history"])
        # clear chat 
        clear_chat_history()


    ### Chat interface
    st.title("Database Chatbot")

    # System state: added so I can use general prompt
    if "full_chat_history" not in st.session_state:
        st.session_state["full_chat_history"] = [{"role": "system", "content": get_final_prompt(db_credentials)}]

    # For API history
    if "api_chat_history" not in st.session_state:
        # TODO: Add general prompt, make into function?
        st.session_state["full_chat_history"] = [{"role": "system", "content": get_final_prompt(db_credentials)}]

    ### Chat 
    # Start
    if (prompt := st.chat_input("What would you like to know?")) is not None:
        st.session_state.full_chat_history.append({"role": "user", "content": prompt})

        # Limit the number of messages sent to OpenAI by token count
        total_tokens = sum(count_tokens(message["content"]) for message in st.session_state["api_chat_history"])
        while total_tokens + count_tokens(prompt) + TOKEN_BUFFER > MAX_TOKENS_ALLOWED:
            removed_message = st.session_state["api_chat_history"].pop(0)
            total_tokens -= count_tokens(removed_message["content"])
        
        st.session_state.api_chat_history.append({"role": "user", "content": prompt})
    
    # Display previous chat
    for message in st.session_state["full_chat_history"][1:]:
        if message["role"] == "user":
            st.chat_message(f"You: ").write(message['content'])
        elif message["role"] == "system":
            st.chat_message(f"System: ").write(message['content'])

    # TODO: Come up with better name than assistant
    if st.session_state["api_chat_history"][-1]["role"] != "system":
        with st.spinner("Connecting to model..."):
            # Send onlt most recent messages to reduce tokens
            recent_messages = st.session_state["api_chat_history"][-MAX_MESSAGES_TO_OPENAI:]
            # get latest message
            new_message = run_chat(recent_messages, funs)

            # Add to latest message
            st.session_state["api_chat_history"].append(new_message)
            st.session_state["full_chat_history"].append(new_message)

            #display latest
            st.chat_message("System: ").write(new_message["context"])
        
        ## Show how much left
        max_tokens = MAX_TOKENS_ALLOWED
        current_tokens = sum(count_tokens(message["content"] for message in st.session_state["full_chat_history"]))
        progress = min(1, max(0, current_tokens/max_tokens))
        st.progress(progress)
        st.write(f"Tokens Used: {current_tokens} / {max_tokens}")
        if current_tokens > max_tokens:
            st.warning("Warning: Due to character limits, older messages may not be remembered in conversations.")

