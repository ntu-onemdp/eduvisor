
import streamlit as st
from controllers.admin_requests_controller import AdminController

class AdminRequestsView:
    """Displays admin requests in Streamlit."""

    def __init__(self, controller: AdminController):
        self.controller = controller

    def display_admin_requests(self):
        """Displays the admin requests manager UI."""
        self.display_css()

        with st.container(border=True):
            st.markdown('<div class="container-title">⚙️ Manage Admin Requests: </div>', unsafe_allow_html=True)
            requests_response = self.controller.get_admin_requests()

            if requests_response["code"] == 200:
                requests = requests_response["data"]

                header_col1, header_col2, header_col3 = st.columns([3, 5, 2])
                with header_col1:
                    st.markdown('<div class="infobox-header">Email</div>', unsafe_allow_html=True)
                with header_col2:
                    st.markdown('<div class="infobox-header">Reason</div>', unsafe_allow_html=True)
                with header_col3:
                    st.markdown("")

                for request in requests:
                    req_user_id = request["user_id"]
                    email = request["email"]
                    reason = request["reason"]

                    col1, col2, col3 = st.columns([3, 5, 2])
                    with col1:
                        st.write(email)
                    with col2:
                        st.write(reason)
                    with col3:
                        if st.button("Approve", key=req_user_id):
                            approve_response = self.controller.approve_admin_request(req_user_id)
                            if approve_response["code"] == 200:
                                st.success(f"Approved {email}")
                                st.rerun()
                            else:
                                st.error(f"Failed to approve {email}: {approve_response['status']}")
            else:
                st.write("No pending admin requests.")

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
                font-size: 15px;
                margin-bottom: 15px;  
                font-weight: normal;
            }
            </style>
            """, unsafe_allow_html=True
        )
