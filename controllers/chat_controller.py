import streamlit as st
from models.chat_history_model import ChatHistoryModel
from models.user_model import UserModel
from models.vectorstore_model import VectorStoreModel
from services.chat_service import ChatService
import re

class ChatController:
    """Handles chat interactions between the frontend, models, and services."""
    def __init__(self):
        self.chat_service = ChatService()
        self.chat_model = ChatHistoryModel()
        self.user_model = UserModel()
        self.vectorstore_model = VectorStoreModel()
    
    def load_vectorstore_from_gcs(self,course_id):
        return VectorStoreModel.load_vectorstore_from_gcs(course_id)

    def initialize_llm(self):
        """Initializes the LLM."""
        return self.chat_service.initialize_llm()

    def get_chat_history(self, user_id, course_id):
        """Retrieves chat history from the database."""
        return self.chat_model.get_chat_history(user_id, course_id)
    
    # def is_explain_query(self,query):
    #     explain_pattern = r"^(please\s+)?(can you\s+|could you\s+)?(explain|clarify)(\s+more|\s+this|\s+further|)?(\s+please)?[?.!]*$"
    #     return re.match(explain_pattern, query.strip().lower()) is not None

    def process_query(self,query,user_id,course_id,course_name,loaded_faiss_vs,llm): 
        st.chat_message("user").markdown(query) 
        modified_query = ""
        response =""
        main_topic = 'Unknown'
        token_used = 0

        if query.lower().strip() in ['hi', 'hello']: 
            response =f"Hello! I am a virtual teaching assistant for {course_name}. What questions do you have? :)"
            token_used = 0

        # elif self.is_explain_query( query.lower().strip() ):
        elif "explain more" in query.lower().strip():
            last_response_response = self.chat_model.get_last_response(user_id, course_id)
            if last_response_response["code"] == 200:
                last_response = last_response_response["data"]
                # modified_query = f"This was your previous response: '{last_response}', Go more in-depth for the explanation."
                modified_query = f"The user asks this query: {query}\n Which is based  on your previous answer: {last_response}\n Please go more in depth."
            
            else:
                response = "There was no previous input to explain more on."
                token_used = 0
            
        # invoke response
        ERROR = False
        if not response:
            persona = "You are a Teaching assistant at NTU."
            task =  f"Answer queries on {course_name}." 
            conditions = f"If user asks any query beyond {course_name}, do not craft an answer but tell the user you are not an expert on the topic. "
            output_style = "Use at most 15 sentences for your response. Respond like you are explaining it to a student."

            try:
                query_to_process = modified_query if modified_query else query
                print(query)
                with st.spinner('Generating answer...'):
                    response, token_used, main_topic = self.chat_service.invoke_response(
                        llm, persona, task, conditions, output_style, loaded_faiss_vs, query_to_process
                    )
            except Exception as e:
                ERROR = True
                st.error(f"An error occurred while processing your request: {str(e)}")

        if not ERROR:
            st.chat_message("assistant").markdown(response)

            # Increment chat counter and save chat
            increment_response = self.user_model.increment_chat_id(user_id)
            if increment_response["code"] == 200:
                cur_chat_id_counter = increment_response["data"]
                save_response = self.chat_model.save_chat(user_id, course_id,cur_chat_id_counter, query, response, main_topic)
                if save_response["code"] != 201:
                    st.error("Failed to save chat.")
                    return
            else:
                st.error("Failed to increment chat counter.")
                return

            # Update token usage
            update_tokens_response = self.user_model.update_tokens_used(user_id, token_used)
            if update_tokens_response["code"] != 200:
                st.error("Failed to update token usage.")

            print('Tokens used:', token_used)
    
