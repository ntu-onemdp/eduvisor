import streamlit as st
import time
from controllers.course_controller import CoursesController


class CourseView:
    """Handles UI rendering for course selection and management."""

    def __init__(self, controller: CoursesController):
        """Initialize the view with a controller instance."""
        self.controller = controller

    def redirect_to_chat_page(self):
        st.switch_page("pages/chat_page.py")

    def display_course_grid(self, courses, allowed_courses=[], is_admin=True):
        """Displays courses in a grid format."""
        num_columns = min(3, len(courses))  # Adjust grid based on courses available
        columns = st.columns([6] * num_columns, gap="small")

        for i, course in enumerate(courses):
            avatar_url = f"https://api.dicebear.com/7.x/bottts-neutral/svg?seed={course['course_id']}"
            button_key = f"Course_{course['course_id']}"

            with columns[i % num_columns]:
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 7])
                    col_a.image(avatar_url, width=60)

                    with col_b:
                        st.markdown(
                            f"**{course['course_name']}**  \n*{course['course_id']}*"
                        )

                        button_disabled = False
                        if not is_admin and course["course_id"] not in allowed_courses:
                            button_disabled = True

                        if st.button(
                            "Chat Now →",
                            key=button_key,
                            disabled=button_disabled,
                            type="primary",
                        ):
                            st.session_state["course_id"] = course["course_id"]
                            st.session_state["course_name"] = course["course_name"]
                            self.redirect_to_chat_page()

                st.write("\n")

    def display_add_course_section(self):
        """Handles adding new courses via UI."""
        with st.expander("⨁ Add a new course", expanded=False):
            course_id = (
                st.text_input(
                    "Course ID",
                    key="new_course_id",
                    placeholder="Enter course ID (e.g., SC2107)",
                )
                .strip()
                .upper()
            )
            course_name = st.text_input("Course Name", key="new_course_name").strip()

            if st.button("Add Course", type="primary"):
                if course_id == "" or course_name == "":
                    st.error("Course ID and Course Name cannot be empty.")
                else:
                    result = self.controller.add_new_course(
                        course_id.strip(), course_name.strip()
                    )
                    if result["code"] == 200:
                        st.success(
                            f"Course '{course_name}' (ID: {course_id}) added successfully!"
                        )
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(result["status"])

            st.warning(
                "⚠︎ Kindly visit the admin portal to add course materials and grant student access after adding the course."
            )

    def display_question_guide(self):
        """Displays guidance on how to ask effective questions in the chatbot."""
        with st.expander(
            "🎯 How to ask better questions (and get better answers)", expanded=False
        ):
            st.markdown("""            
            - **Ask specific questions instead of broad slide summaries.**  
              **✓** *"Which registers need to be configured for a SysTick timer?"*  
              ✗ *"Explain all Timer slides."*  
                     
            - **Provide lab code snippets when seeking code explanations.** *(⚠︎ The chatbot does not have access to lab-specific code!)*  
              **✓** *"What does `insert code` do in GPIO configuration?"*  
              ✗ *"Provide me the entire lab code for GPIO configuration."*  
            
            - **Frame targeted questions rather than vague queries.**   
              **✓** *"What is tested in lab 2?"*  
              ✗ *"What is tested in the lab?"*  
            """)
