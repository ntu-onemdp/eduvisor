import streamlit as st
import time
from controllers.whitelist_controller import WhitelistController


class WhitelistStudentView:
    """Handles UI interactions for managing student whitelists in Streamlit."""

    def __init__(self, controller: WhitelistController):
        """Initialize the view with a controller instance."""
        self.controller = controller

    def list_whitelisted_students(self, course_id):
        """Displays the list of whitelisted students with a remove option."""
        students_response = self.controller.get_whitelisted_students(course_id)
        with st.container(height=150):
            if students_response["code"] == 200:
                whitelisted_students = students_response["data"]
                st.markdown(
                    f"<b>Students in course '{course_id}':</b>", unsafe_allow_html=True
                )

                for student_email in whitelisted_students:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(student_email)
                    with col2:
                        if st.button("Remove", key=student_email):
                            delete_response = self.controller.remove_student(
                                course_id, student_email
                            )
                            if delete_response["code"] == 200:
                                st.success(delete_response["status"])
                            else:
                                st.error(delete_response["status"])
                            st.rerun()
            else:
                st.warning(students_response["status"])

    def process_uploaded_file(self, course_id, uploaded_file):
        """Handles file uploads and processes student emails for whitelisting."""
        if (
            st.button("Upload whitelist files", type="primary")
            and uploaded_file
            and course_id
        ):
            status_placeholder = st.empty()
            try:
                status_placeholder.info(f"Checking if course '{course_id}' exists...")

                # Check if course exists
                course_response = self.controller.check_course_exists(course_id)
                if course_response["code"] == 404:
                    status_placeholder.error(
                        f"Course '{course_id}' not found. Please add the course first in the course page before proceeding."
                    )
                    return

                status_placeholder.info("Course found, analysing file...")

                # Extract emails using the controller
                emails = self.controller.process_whitelist_file(uploaded_file)

                if emails:
                    status_placeholder.info(
                        f"Extracted {len(emails)} emails successfully!"
                    )

                    # Add enrollments using the controller
                    update_response = self.controller.add_students(course_id, emails)

                    if update_response["code"] == 200:
                        status_placeholder.success(f"{update_response['status']}")
                        st.write("List of emails extracted:")
                        st.write(emails)
                        time.sleep(2)  # Allow viewer to see emails before rerun
                        st.rerun()
                    else:
                        status_placeholder.error(update_response["status"])
                else:
                    status_placeholder.error(
                        "No emails extracted from the uploaded file. Please check the format."
                    )

            except Exception as e:
                status_placeholder.error(f"Error processing file: {e}")

    def display_whitelist_manager(self):
        """Main UI for managing student whitelists."""
        self.display_css()

        with st.container(border=True):
            st.markdown(
                '<div class="container-title">👤 Manage Student Access: </div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="infobox-header">Upload student access file (csv attendance format)</div>',
                unsafe_allow_html=True,
            )

            course_id = (
                st.text_input(
                    "Enter Course ID",
                    label_visibility="collapsed",
                    placeholder="Enter course ID (e.g., SC2107)",
                    key="whitelist_course_id_input",
                )
                .strip()
                .upper()
            )

            # feature 1: List whitelisted students
            if course_id:
                self.list_whitelisted_students(course_id)

            # feature 2: Upload file and process students
            uploaded_file = st.file_uploader(
                "Upload files",
                accept_multiple_files=False,
                type=["csv"],
                label_visibility="collapsed",
            )

            self.process_uploaded_file(course_id, uploaded_file)

    def display_css(self):
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@300;400;500;600;700&display=swap');
            .container-title {
                font-family: 'Source Sans Pro';
                font-size: 20px;
                margin-bottom: 13px;  
                color: #1B62B7;
            }
            .infobox-header {
                font-family: 'Source Sans Pro';
                font-size: 16px;
                margin-bottom: 15px;  
                font-weight: normal;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


# import streamlit as st
# import pandas as pd
# from database import *
# import time
# # not done.  cross check the last controller function.
# # check if will update.

# def whitelist_student_manager(course_collection,enrolment_collection):

#     st.markdown(
#         """
#         <style>
#         @import url('https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@300;400;500;600;700&display=swap');
#         @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

#         .container-title{
#          font-family: 'Source Sans Pro';
#         font-size: 20px;
#         margin-bottom:13px;
#         color: #1B62B7;
#         }

#         .infobox-header{
#          font-family: 'Source Sans Pro';
#         font-size: 16px;
#         margin-bottom:15px;
#         font-weight: normal;
#         }

#         </style>
#             """, unsafe_allow_html=True)

#     with st.container(border=True):
#         st.markdown('<div class = "container-title">👤 Manage Student Access: </div>', unsafe_allow_html = True)

#         st.markdown('<div class = "infobox-header">Upload student access file (csv attendance format)</div>', unsafe_allow_html = True)

#         whitelist_course_id = st.text_input("Enter Course ID", label_visibility = "collapsed", placeholder="Enter course ID (Capital letters eg. SC2107)",key="whitelist_course_id_input").strip().upper()
#         st.write("")

#         if whitelist_course_id:
#             with st.spinner(f"Fetching whitelisted students for {whitelist_course_id}..."):
#                 students_response = enrolment_collection.get_whitelisted_students(whitelist_course_id)
#             with st.container(height=150):
#                 if students_response["code"] == 200:
#                     whitelisted_students = students_response["data"]

#                     st.markdown(f"<b>Students in course '{whitelist_course_id}':</b>", unsafe_allow_html=True)
#                     for student_email in whitelisted_students:

#                         col1, col2 = st.columns([3, 1])

#                         with col1:
#                             st.write(student_email)

#                         with col2:
#                             if st.button("Remove", key=student_email):
#                                 delete_response = enrolment_collection.remove_student_from_course(whitelist_course_id, student_email)

#                                 if delete_response["code"] == 200:
#                                     st.success(delete_response["status"])
#                                 elif delete_response["code"] == 404:
#                                     st.warning(delete_response["status"])
#                                 else:
#                                     st.error(delete_response["status"])
#                                 st.rerun()

#                 else:
#                     st.warning(students_response["status"])


#         uploaded_file = st.file_uploader("Upload files", accept_multiple_files=False, type=["csv"], label_visibility = "collapsed")
#         st.write("")

#         if st.button("Upload whitelist files", type='primary') and uploaded_file and whitelist_course_id:
#             status_placeholder = st.empty()
#             # 1. make the placeholder for the progress.
#             # 3. store it in course
#             try:
#                 status_placeholder.info(f"Checking if course '{whitelist_course_id}' exists...")
#                 course_response = course_collection.course_exists(whitelist_course_id)

#                 if course_response["code"] == 404:  # Course does not exist
#                     status_placeholder.error(f"Course '{whitelist_course_id}' not found. Please add the course first in the course page before proceeding.")
#                     return

#                 status_placeholder.info('Course found, analysing file...')
#                 emails = process_whitelist_file(uploaded_file)


#                 status_placeholder.info(f"Extracted {len(emails)} emails successfully!")

#                 status_placeholder.info(f"Updating emails in course...")
#                 update_response = enrolment_collection.add_enrollments(whitelist_course_id, emails)

#                 if update_response["code"] == 200:
#                     status_placeholder.success(f"{update_response['status']}")
#                     st.write('List of emails extracted:')
#                     st.write(emails)
#                     time.sleep(2) # allow viewer to see emails and then rerun to update the listing

#                 else:
#                     status_placeholder.error(update_response["status"])

#                 st.rerun()

#             except Exception as e:
#                 status_placeholder.error(f"Error processing file: {e}")
