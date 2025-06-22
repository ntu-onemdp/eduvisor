import streamlit as st
from controllers.admin_requests_controller import AdminController


class StudentPortalView:
    """Displays the student portal UI in Streamlit."""

    def __init__(self, controller: AdminController, user_id):
        """Initialize with a controller instance and user ID."""
        self.controller = controller
        self.user_id = user_id

    def display_student_portal(self):
        """Displays the student portal for requesting access."""
        st.warning(
            "⚠︎ Students are not authorized to access this portal. If you are an instructor, please request access below."
        )

        email = st.text_input("Enter NTU email:")
        reason = st.text_input("Enter reason for request:")

        if st.button("Request Access", type="primary"):
            if email and reason:
                create_request_response = self.controller.create_admin_request(
                    self.user_id, email, reason
                )
                if create_request_response["code"] == 201:
                    st.success("Your request has been sent and will be reviewed.")
                else:
                    st.error(
                        f"Failed to create request: {create_request_response['status']}"
                    )
            else:
                st.error("Please fill out all fields before submitting.")
