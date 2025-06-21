import streamlit as st
from models.user_model import UserModel
from services.auth_service import AuthService
from helpers import session_state_init, check_logged_in

class AuthController:
    def __init__(self):
        self.user_model = UserModel()
        self.auth_service = AuthService()

    def redirect_to_chatbot(self):
        """Redirects user to the chatbot page."""
        st.switch_page("pages/courses_page.py")

    def authenticate_user(self):
        """Handles authentication and session management."""
        session_state_init()
        query_params = st.query_params

        # Edge case: If user is already logged in
        if check_logged_in():
            self.redirect_to_chatbot()
            return

        # If authentication code is present in URL
        if "code" in query_params:
            auth_code = query_params["code"]
            print('auth_code')
            print(auth_code)
            token = self.auth_service.acquire_token(auth_code)
            print('token')
            print(token)


            if "access_token" in token:
                with st.spinner("Verifying user..."):
                    id_token_claims = token.get("id_token_claims", {})
                    oid = id_token_claims.get("oid")
                    email = id_token_claims.get("preferred_username")

                    if oid:
                        user_response = self.user_model.user_exists(oid)

                        # Case 1: User Exists
                        if user_response["code"] == 200 and user_response["data"]:
                    
                            login_response = self.user_model.login_user(oid)

                            if login_response["code"] == 200:
                                user = login_response["data"]

                                # Set session state
                                st.session_state["logged_in"] = True
                                st.session_state["user_id"] = user["user_id"]
                                st.session_state["user_email"] = user["email"]
               
                     
                                self.redirect_to_chatbot()

                            elif login_response["code"] == 403:
                                st.error("Your account has been deactivated. Please contact support.")

                            else:
                                st.error("Failed to log in. Please try again later.")
                                st.error(login_response)

                        # Case 2: User Does Not Exist - Create New User
                        elif user_response["code"] == 200 and not user_response["data"]:
                            create_response = self.user_model.create_user(oid, email)

                            if create_response["code"] == 201:
                                user = create_response["data"]
                                st.session_state["logged_in"] = True
                                st.session_state["user_id"] = user["user_id"]
                                st.session_state["user_email"] = user["email"]
                                
                                self.redirect_to_chatbot()
                            else:
                                st.error("Failed to create a new user. Please try again.")
                        else:
                            st.error(f"An error occurred: {user_response['status']}. Please try again.")

        else:
            st.error("Failed to acquire token. Please try logging in again.")

