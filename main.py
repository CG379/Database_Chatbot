import streamlit as st
# Use 4o-mini 3 requests perr minute

if __name__ == '__main__':
    # Menu bar
    menu_bar = get_data()# get data for menue bar
    # add watermark later
    

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
        path = ... # TODO: save conversation function
        st.sidebar.success(f"Conversation saved at {path}")
        st.sidebar.markdown(f"Download here: [Open Conversation]({path})")

    ## clear chat button
    if st.sidebar.button("Clear Chat"):
        # save conversation: st.session_state["full_chat_history"]
        # TODO: save conversation function
        # TODO: clear chat function
        pass


    ### Chat interface
    st.title("Database Chatbot")

    # System state: added so I can use general prompt
    if "full_chat_history" not in st.session_state:
        # TODO: Add general prompt, make into function?
        temp = "Hello, you are a chatbot to help the user look through their databases"
        st.session_state["full_chat_history"] = [{"role": "system", "content": temp}]

    # For API history
    if "api_chat_history" not in st.session_state:
        # TODO: Add general prompt, make into function?
        temp = "Hello, you are a chatbot to help the user look through their databases"
        st.session_state["api_chat_history"] = [{"role": "system", "content": temp}]

    ### Chat 
    # Start
    if (prompt := st.chat_input("What would you like to know?")) is not None:
        st.session_state.full_chat_history.append({"role": "user", "content": prompt})

        # TODO: make count tokens function
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
    if st.session_state["api_chat_history"][-1]["role"] != "assistant":
        with st.spinner("Connecting to model..."):
            # Send onlt most recent messages to reduce tokens
            # TODO: Set max messages
            recent_messages = st.session_state["api_chat_history"][-MAX_MESSAGES_TO_OPENAI:]
            # get latest message
            # TODO: Make run chat function
            new_message = run_chat_sequence(recent_messages, functions)

            # Add to latest message to api chat and full chat
            st.session_state["api_chat_history"].append(new_message)
            st.session_state["full_chat_history"].append(new_message)

            #display latest
            st.chat_message("System: ").write(new_message["context"])
        
        ## Show how much left
        # TODO: Set max tokens
        max_tokens = MAX_TOKENS_ALLOWED
        # TODO: make count tokens function
        current_tokens = sum(count_tokens(message["content"] for message in st.session_state["full_chat_history"]))
        progress = min(1, max(0, current_tokens/max_tokens))
        st.progress(progress)
        st.write(f"Tokens Used: {current_tokens} / {max_tokens}")
        if current_tokens > max_tokens:
            st.warning("Warning: Due to character limits, older messages may not be remembered in conversations.")

