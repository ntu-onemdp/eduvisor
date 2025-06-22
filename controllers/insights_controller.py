import streamlit as st
from models.user_model import UserModel
from models.chat_history_model import ChatHistoryModel
from models.courses_model import CoursesModel
from models.pdf_model import PDFModel


class InsightsController:
    """Handles data retrieval and processing for insights page."""

    def __init__(self):
        self.user_model = UserModel()
        self.chat_model = ChatHistoryModel()
        self.courses_model = CoursesModel()
        self.pdf_model = PDFModel()

    # for usage graph
    def get_token_and_chat_usage(self, user_id, is_admin):
        """Retrieves token usage and chat count for the user (or aggregated stats for admins)."""
        if is_admin:
            tokens_response = self.user_model.get_average_token_usage()
            chats_response = self.user_model.get_total_chat_count()
        else:
            tokens_response = self.user_model.get_user_tokens_used(user_id)
            chats_response = self.user_model.get_user_chat_count(user_id)

        if chats_response["code"] != 200 or tokens_response["code"] != 200:
            return None, None

        return tokens_response["data"], chats_response["data"]

    # for chat analytics
    def get_chat_counts_by_topic(self, user_id, course_id, is_admin):
        """Fetches the number of chats for each topic for a given course."""
        # Get list of topics (from PDFs)
        topic_list = self.get_available_topics_for_course(course_id)
        if topic_list is None:
            return None

        # Get chat history
        if is_admin:
            chat_history_response = self.chat_model.get_chat_history_by_course(
                course_id
            )
        else:
            chat_history_response = self.chat_model.get_chat_history(user_id, course_id)

        if chat_history_response["code"] != 200:
            return {topic: 0 for topic in topic_list} | {"Unknown": 0}

        chat_history = chat_history_response["data"]

        # Count chats per topic
        topic_counter = {topic: 0 for topic in topic_list}
        topic_counter["Unknown"] = 0

        for chat in chat_history:
            main_topic = chat.get("main_topic", "Unknown")
            if main_topic in topic_counter:
                topic_counter[main_topic] += 1
            else:
                topic_counter["Unknown"] += 1

        return topic_counter

    def get_available_topics_for_course(self, course_id):
        """Fetches the available topics (PDFs) for a given course."""
        list_response = self.pdf_model.list_pdfs_for_course(course_id)

        if list_response["code"] == 200:
            topic_list = sorted(list_response["data"])
            return topic_list if topic_list else None
        else:
            st.error("Failed to retrieve topic list.")
            return None

    def get_all_courses(self):
        """Fetches all courses available."""
        all_courses_response = self.courses_model.get_courses()
        if all_courses_response["code"] == 200:
            return all_courses_response["data"]
        else:
            st.error("No courses available.")
            return []
