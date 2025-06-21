import streamlit as st 
from view.navbar import *
from view.course_material_manager import *
from view.admin_requests_manager import *
from view.student_portal import *
from view.whitelist_student_manager import *
from controllers.course_material_controller import CourseMaterialController
from controllers.admin_requests_controller import AdminController
from controllers.whitelist_controller import WhitelistController
from controllers.user_controller import UserController
from helpers import *


def main():
    hide_streamlit_bar()
    admin_css()
    
    # mandatory check
    session_state_init()
    if check_logged_in() == False: 
        redirect_to_main()
        return None
    
    user_id = st.session_state['user_id']
    user_email = st.session_state['user_email']
    custom_sidebar(user_email)

    st.markdown('<div  class = "admintitle" >Admin Portal</div>', unsafe_allow_html=True)
    st.markdown('<div  class = "admin-header"> Organize course materials and manage student access.</div>', unsafe_allow_html=True)

    # get user role first
    user_controller = UserController()
    user_role_response = user_controller.get_user_role(user_id)

    if user_role_response["code"] == 200:
        user_role = user_role_response["data"]
    else:
        st.error("Failed to retrieve user role. Please try again later.")
        return
    
    admin_controller = AdminController()
    course_material_controller = CourseMaterialController()
    whitelist_controller = WhitelistController()
    
    if user_role in ['ADMIN', 'OWNER']:
        # show course manager and whitelist manager
        course_material_view = CourseMaterialView(controller=course_material_controller)
        course_material_view.display_course_material_manager()
        
        whitelist_view = WhitelistStudentView(whitelist_controller)
        whitelist_view.display_whitelist_manager()

        if user_role =="OWNER": 
            # show admin requests manager
            admin_requests_view = AdminRequestsView(controller=admin_controller)
            admin_requests_view.display_admin_requests()

    else: 
        # show student portal (request for access)
        student_portal_view = StudentPortalView(controller=admin_controller, user_id=user_id)
        student_portal_view.display_student_portal()


def admin_css(): 
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
        .admintitle{ 
        font-family: 'Source Sans Pro';
        margin-bottom: 10px;
        font-size:30px;}

        .admin-header{
         font-family: 'Source Sans Pro';
        font-size: 18px;
        margin-bottom:25px;  
        }

         .block-container {
            padding-top: 5rem !important;
        }
        </style>
            """, unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()


