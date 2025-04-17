import streamlit as st
# Use 4o-mini 3 requests perr minute
from utils.config import MAX_TOKENS_ALLOWED, MAX_MESSAGES_TO_OPENAI, TOKEN_BUFFER, db_credentials
from utils.chat_funs import run_chat, count_tokens, prep_menuebar_data, clear_chat_history
from utils.system_prompts import get_final_prompt
from utils.fun_calling import funs
from utils.helper_funs import save_conv_history
from utils.db_funs import db_schema_dict, get_db_connection, create_db, drop_database, import_csv_to_table, get_db_info
import pandas as pd

# Initialize chat history at the very beginning
if "full_chat_history" not in st.session_state:
    st.session_state["full_chat_history"] = [{"role": "system", "content": get_final_prompt(db_credentials)}]
if "api_chat_history" not in st.session_state:
    st.session_state["api_chat_history"] = [{"role": "system", "content": get_final_prompt(db_credentials)}]

#TODO: Fix for no existing database case

if __name__ == '__main__':
    # Check database connection
    db_connection = get_db_connection()
    
    # Database setup section
    st.sidebar.title("Database Setup")
    
    if db_connection is None:
        st.sidebar.warning("No database connection available")
        
        # Database creation form
        with st.sidebar.form("create_db_form"):
            st.subheader("Create New Database")
            db_name = st.text_input("Database Name", "my_database")
            submitted = st.form_submit_button("Create Database")
            if submitted:
                result = create_db(db_name)
                st.sidebar.info(result)
                # Refresh connection
                db_connection = get_db_connection()
    
    # Database import section
    if db_connection:
        with st.sidebar.expander("Import Data"):
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.write("Preview of your data:")
                    st.write(df.head())
                    
                    table_name = st.text_input("Table Name", "imported_data")
                    schema_name = st.text_input("Schema Name", "public")
                    
                    if st.button("Import to Database"):
                        result = import_csv_to_table(db_connection, table_name, df, schema_name)
                        st.info(result)
                        # Refresh the database view
                        db_schema_dict = get_db_info(db_connection, [schema_name])
                except Exception as e:
                    st.error(f"Error reading file: {e}")
    
    # Database viewer section
    st.sidebar.title("Database Viewer")
    
    if db_connection:
        # Menu bar
        menu_bar = prep_menuebar_data(db_schema_dict)
        
        if menu_bar:
            # Dropdown menu
            selected_schema = st.sidebar.selectbox("Select Schema", list(menu_bar.keys()))
            selected_table = st.sidebar.selectbox("Select Table", list(menu_bar[selected_schema].keys()))
            
            # Show columns of table
            st.sidebar.subheader(f"Columns of {selected_table}")
            for col in menu_bar[selected_schema][selected_table]:
                st.sidebar.checkbox(f" {col}")
        else:
            st.sidebar.info("No tables found in the database")
    else:
        st.sidebar.info("Connect to a database to view its contents")
    
    # Conversation management
    if st.sidebar.button("Save Conversation"):
        if "full_chat_history" in st.session_state:
            saved_file_path = save_conv_history(st.session_state["full_chat_history"])
            st.sidebar.success(f"Conversation saved in {saved_file_path}")
            st.sidebar.markdown(f"Download here: [Open Conversation]({saved_file_path})")
        else:
            st.sidebar.warning("No conversation to save")

    if st.sidebar.button("Clear Chat"):
        if "full_chat_history" in st.session_state:
            save_conv_history(st.session_state["full_chat_history"])
        clear_chat_history()
        # Reinitialize chat history after clearing
        st.session_state["full_chat_history"] = [{"role": "system", "content": get_final_prompt(db_credentials)}]
        st.session_state["api_chat_history"] = [{"role": "system", "content": get_final_prompt(db_credentials)}]

    # Chat interface
    st.title("Database Chatbot")


    # Chat input
    if (prompt := st.chat_input("What would you like to know?")) is not None:
        st.session_state.full_chat_history.append({"role": "user", "content": prompt})

        # Token management
        total_tokens = sum(count_tokens(message["content"]) for message in st.session_state["api_chat_history"])
        while total_tokens + count_tokens(prompt) + TOKEN_BUFFER > MAX_TOKENS_ALLOWED:
            removed_message = st.session_state["api_chat_history"].pop(0)
            total_tokens -= count_tokens(removed_message["content"])
        
        st.session_state.api_chat_history.append({"role": "user", "content": prompt})

    # Display chat history
    for message in st.session_state["full_chat_history"][1:]:
        if message["role"] == "user":
            st.chat_message("You").write(message['content'])
        elif message["role"] == "system":
            st.chat_message("System").write(message['content'])

    # Process latest message
    if st.session_state["api_chat_history"][-1]["role"] != "system":
        with st.spinner("Connecting to model..."):
            recent_messages = st.session_state["api_chat_history"][-MAX_MESSAGES_TO_OPENAI:]
            new_message = run_chat(recent_messages, funs)
            st.session_state["api_chat_history"].append(new_message)
            st.session_state["full_chat_history"].append(new_message)
            st.chat_message("System").write(new_message["content"])

    # Token usage display
    if db_connection:
        current_tokens = sum(count_tokens(message["content"]) for message in st.session_state["full_chat_history"])
        progress = min(1, max(0, current_tokens/MAX_TOKENS_ALLOWED))
        st.progress(progress)
        st.write(f"Tokens Used: {current_tokens} / {MAX_TOKENS_ALLOWED}")
        if current_tokens > MAX_TOKENS_ALLOWED:
            st.warning("Warning: Due to character limits, older messages may not be remembered in conversations.")

