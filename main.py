import streamlit as st


if __name__ == '__main__':
    # Menu bar
    menu_bar = # get data for menue bar
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

