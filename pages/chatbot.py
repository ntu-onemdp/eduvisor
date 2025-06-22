import streamlit as st
from helpers import *
from controllers.auth_controller import AuthController


def main():
    hide_streamlit_bar()
    session_state_init()

    auth_controller = AuthController()
    auth_controller.authenticate_user()


if __name__ == "__main__":
    main()
