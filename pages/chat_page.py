import streamlit as st
from helpers import *
from view.navbar import *
from controllers.chat_controller import ChatController
from controllers.user_controller import UserController
from models.vectorstore_model import load_vectorstore_from_gcs
import re

MAX_CHAR_LIMIT = 400
MAX_TOKEN_LIMIT = 150000


def get_llm(chat_controller):
    if st.session_state.llm == None:
        st.session_state.llm = chat_controller.initialize_llm()
    return st.session_state.llm


def display_chat_history(user_id, course_id, chats):
    """Displays previous chat history."""
    chat_history_response = chats.get_chat_history(user_id, course_id)
    if chat_history_response["code"] in [200, 404]:
        chat_history = chat_history_response["data"]
        for chat in chat_history:
            with st.chat_message("user"):
                st.markdown(chat["query"])
            with st.chat_message("assistant"):
                st.markdown(chat["response"])


def is_explain_query(query):
    explain_pattern = r"^(please\s+)?(can you\s+|could you\s+)?(explain|clarify)(\s+more|\s+this|\s+further|)?(\s+please)?[?.!]*$"
    return re.match(explain_pattern, query.strip().lower()) is not None


def main():
    hide_streamlit_bar()
    chat_css()

    # mandatory check
    session_state_init()
    if check_logged_in() == False:
        redirect_to_main()
        return None

    user_email = st.session_state["user_email"]
    custom_sidebar(user_email, chat=True)

    # load user_id and controllers
    user_id = st.session_state["user_id"]
    course_id = st.session_state["course_id"]
    course_name = st.session_state["course_name"]

    chat_controller = ChatController()
    user_controller = UserController()

    st.markdown(
        '<div class = "chattitle" >Ask me anything!</div>', unsafe_allow_html=True
    )
    st.info(f"ⓘ This chat is for course: {course_id}")

    # 1. Initialise components
    llm = get_llm(chat_controller)
    if course_id:
        vector_store_response = load_vectorstore_from_gcs(course_id)
        print(vector_store_response)
        if vector_store_response["code"] == 200:
            loaded_faiss_vs = vector_store_response["data"]
        else:
            loaded_faiss_vs = None
            st.error(
                "The chatbot is currently unavailable for use as no course files have been added."
            )
            return None
    else:
        redirect_to_courses()  # handle lack of course id, redirect to courses page.

    # 2. Display chat history
    display_chat_history(user_id, course_id, chat_controller)

    # 3. Handle User input
    query = st.chat_input("Enter query")

    tokens_used_response = user_controller.get_user_tokens_used(user_id)
    if tokens_used_response["code"] == 200:
        total_tokens_used = tokens_used_response["data"]
    else:
        st.error("Failed to retrieve token usage.")
        return

    # 3a. validate query first
    if query:
        if len(query) > MAX_CHAR_LIMIT:
            st.error(
                f"Your query exceeds the maximum limit of characters. Please shorten your query."
            )
            query = None
        if total_tokens_used >= MAX_TOKEN_LIMIT:
            st.error(
                f"You have reached the maximum usage limit for this chatbot. Please contact support."
            )
            query = None

    # 3b. process query
    if query:
        chat_controller.process_query(
            query, user_id, course_id, course_name, loaded_faiss_vs, llm
        )


def chat_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
        .chattitle{ 
        font-family: 'Source Sans Pro';
        margin-bottom: 15px;
        font-size:30px}
        .block-container {
            padding-top: 5rem !important;
        }
        </style>

            """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
