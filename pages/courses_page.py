import streamlit as st
from helpers import *
from view.navbar import *
from view.course_grid import CourseView
from controllers.course_controller import CoursesController
from controllers.user_controller import UserController


def main():
    hide_streamlit_bar()
    courses_css()

    # 0. mandatory check
    session_state_init()
    if check_logged_in() == False:
        redirect_to_main()
        return None

    user_email = st.session_state["user_email"]
    custom_sidebar(user_email)

    #  get user role and user email
    user_email = st.session_state["user_email"]
    user_id = st.session_state["user_id"]
    user_controller = UserController()
    user_role_response = user_controller.get_user_role(user_id)

    if user_role_response["code"] == 200:
        user_role = user_role_response["data"]
    else:
        st.error("Failed to retrieve user role. Please try again later.")
        return

    is_admin = user_role in ["OWNER", "ADMIN"]
    course_controller = CoursesController()

    st.markdown(
        '<div class = "coursestitle" >Course-specific chatbots</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class = "courses-header" >Chat with our chatbots to get course-related answers and guidance!</div>',
        unsafe_allow_html=True,
    )

    # get courses and student access
    with st.spinner("Loading"):
        # a. get courses first
        courses_list = course_controller.get_courses()

        course_view = CourseView(course_controller)

        # b. get student access
        if is_admin:  # dn student access if admin
            course_view.display_course_grid(courses_list)
            course_view.display_question_guide()
            course_view.display_add_course_section()
        else:
            # get student enrolments
            allowed_course_list = course_controller.get_student_enrollments(user_email)
            course_view.display_course_grid(
                courses_list, allowed_course_list, is_admin=False
            )
            course_view.display_question_guide()


def courses_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
        .coursestitle{ 
        font-family: 'Source Sans Pro';
        margin-bottom: 10px;
        font-size:30px}

        .courses-header{
         font-family: 'Source Sans Pro';
        font-size: 18px;
        margin-bottom:40px;  
        }
    
        .block-container {
            padding-top: 5rem !important;
        }
        </style>

            """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
