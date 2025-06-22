import streamlit as st
from controllers.course_material_controller import CourseMaterialController


class CourseMaterialView:
    """Handles UI interactions for managing course materials in Streamlit."""

    def __init__(self, controller: CourseMaterialController):
        """Initialize the view with a controller instance."""
        self.controller = controller

    def list_course_files(self, course_id):
        """Displays files for the given course ID with delete options."""
        filenames_response = self.controller.list_files(course_id)
        with st.container(height=150):
            if filenames_response["code"] == 200:
                filenames = filenames_response["data"]
                st.markdown(
                    f"<b>Files in course '{course_id}':</b>", unsafe_allow_html=True
                )
                for filename in filenames:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(filename)
                    with col2:
                        if st.button("Delete", key=filename):
                            delete_response = self.controller.delete_file(
                                course_id, filename
                            )
                            if delete_response["code"] == 200:
                                st.success(delete_response["status"])
                            else:
                                st.error(delete_response["status"])
                            st.rerun()
            else:
                st.warning(filenames_response["status"])

    def upload_course_files(self, course_id, uploaded_files):
        """Handles file uploads for a course."""
        if st.button("Add files", type="primary") and uploaded_files and course_id:
            status_placeholder = st.empty()
            for uploaded_file in uploaded_files:
                upload_response = self.controller.upload_file(uploaded_file, course_id)
                if upload_response["code"] == 201:
                    status_placeholder.success(upload_response["status"])

                else:
                    status_placeholder.error(upload_response["status"])

            # rerun only when all files are uploaded. prior rerun will clear the uploaded files.
            st.rerun()

    def update_chatbot(self, course_id):
        """Updates the chatbot with new course materials."""
        if st.button("Update chatbot", type="primary"):
            status_placeholder = st.empty()

            if course_id:
                # Get pdfs first
                status_placeholder.info("Fetching PDFs for course...")
                pdfs_response = self.controller.fetch_pdfs_in_memory(course_id)

                if pdfs_response["code"] == 200:
                    pdfs = pdfs_response["data"]

                    if not pdfs:
                        status_placeholder.error(
                            "No PDFs found for the given course ID."
                        )
                    else:
                        status_placeholder.success(
                            f"Fetched {len(pdfs)} PDFs for course."
                        )

                        # Generate vector store using retrieved pdfs
                        status_placeholder.info("Generating vector store from PDFs...")
                        vectorstore_response = self.controller.generate_vectorstore(
                            pdfs
                        )

                        if vectorstore_response["code"] == 200:
                            vectorstore = vectorstore_response["data"]

                            # Save vector store that was generated
                            status_placeholder.info("Saving vector store...")
                            save_response = self.controller.save_vectorstore(
                                vectorstore, course_id
                            )

                            if save_response["code"] == 201:
                                status_placeholder.success(save_response["status"])
                            else:
                                status_placeholder.error(save_response["status"])

                        else:
                            status_placeholder.error(vectorstore_response["status"])

                else:
                    status_placeholder.error(pdfs_response["status"])
            else:
                status_placeholder.error("Please enter a course ID.")

    def display_course_material_manager(self):
        """Main UI for managing course materials."""
        self.display_css()

        with st.container(border=True):
            st.markdown(
                '<div class="container-title">📁 Manage Course Materials: </div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="infobox-header">1. Upload / delete course material files</div>',
                unsafe_allow_html=True,
            )

            course_id = (
                st.text_input(
                    "Enter Course ID",
                    label_visibility="collapsed",
                    placeholder="Enter course ID (e.g., SC2107)",
                    key="course_id_input",
                )
                .strip()
                .upper()
            )

            # feature 1: list course files
            if course_id:
                self.list_course_files(course_id)

            # feature 2: upload course files
            uploaded_files = st.file_uploader(
                "Upload files",
                accept_multiple_files=True,
                type=["pdf"],
                label_visibility="collapsed",
            )

            self.upload_course_files(course_id, uploaded_files)

            # feature 3: update chatbot
            st.write("")
            st.markdown(
                '<div class="infobox-header">2. Update chatbot with new course materials </div>',
                unsafe_allow_html=True,
            )
            self.update_chatbot(course_id)
            st.write("")

    def display_css(self):
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@300;400;500;600;700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

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
