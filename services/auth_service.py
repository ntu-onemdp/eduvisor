from msal import ConfidentialClientApplication
import streamlit as st

class AuthService:
    def __init__(self):
        self.app = ConfidentialClientApplication(
            st.secrets["CLIENT_ID"],
            authority=st.secrets["AUTHORITY"],
            client_credential=st.secrets["CLIENT_SECRET"],
        )
        self.redirect_path = st.secrets["REDIRECT_PATH"]

    def get_auth_url(self):
        """Generates an authentication URL"""
        return self.app.get_authorization_request_url(
            scopes=st.secrets["SCOPE"],
            redirect_uri=self.redirect_path
        )

    def acquire_token(self, auth_code):
        """Exchanges auth code for an access token"""
        return self.app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=st.secrets["SCOPE"],
            redirect_uri=self.redirect_path
        )
