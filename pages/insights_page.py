import streamlit as st 
from database import * 
from helpers import *
from view.navbar import *
from view.usage_analysis import UsageAnalysisView
from view.chat_analysis import ChatAnalysisView
from controllers.user_controller import UserController
from controllers.insights_controller import InsightsController

def main():
    hide_streamlit_bar()
    insights_css()
    
    # 0. mandatory check
    session_state_init()
    if check_logged_in() == False: 
        redirect_to_main()
        return None
    
    user_email = st.session_state['user_email']
    custom_sidebar(user_email)
    
    user_id = st.session_state['user_id']

    # initialise controller
    user_controller = UserController()
    insights_controller = InsightsController()

    # courses = CoursesCollection()
    # users = UsersCollection()

    # get user role
    user_role_response = user_controller.get_user_role(user_id)
    if user_role_response["code"] == 200:
        user_role = user_role_response["data"]
    else:
        st.error("Failed to retrieve user role. Please try again later.")
        return

    is_admin = user_role in ['ADMIN', 'OWNER']


    # display tokens and chat usage 
    st.markdown('<div  class = "statstitle" >Tokens and chat usage:</div>', unsafe_allow_html=True)
    with st.spinner("Generating insights"):
        usage_view = UsageAnalysisView(insights_controller)
        usage_view.display_usage_graph(user_id, is_admin)

    
    st.markdown('<div  class = "statstitle" >Chat Analysis by Topic:</div>', unsafe_allow_html=True)
    chat_view = ChatAnalysisView(insights_controller)
    chat_view.display_topic_graphs_for_all_courses(user_id, is_admin)


    
       
def insights_css(): 
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

        .statstitle{ 
        font-family: 'Source Sans Pro';
        font-size:25px;
        margin-bottom: 15px;}

        .block-container {
            padding-top: 5rem !important;
        }
        </style>

            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
