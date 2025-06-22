import streamlit as st


def handle_logout():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.switch_page("app.py")
    st.rerun()


def custom_sidebar(email, chat=False):
    st.sidebar.markdown(
        f"""
        <style>
            .sidebar-title {{
                font-size: 20px;
                font-weight: 500;
            }}
             .email-text {{
                color: #1B62B7;  
                font-weight: 500;
            }}
        </style>
        <div class="sidebar-title">Welcome, <span class="email-text">{email}</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.write("")  # Add an empty line for spacing
    st.sidebar.write("")  # Add an empty line for spacing

    st.sidebar.page_link("pages/courses_page.py", label="Courses", icon="💬")

    if chat:
        st.sidebar.page_link("pages/chat_page.py", label="↳ Chat")

    st.sidebar.page_link("pages/insights_page.py", label="Insights", icon="💡")
    st.sidebar.page_link("pages/admin_page.py", label="Admin Portal", icon="📁")

    if not chat:
        st.sidebar.write("")
    st.sidebar.write("")
    if st.sidebar.button("Logout", key="logout_button"):
        handle_logout()

    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.markdown(
        """
    **Have any feedback?** \n
    👉 [**Share your thoughts**](https://tinyurl.com/VTAfeedback)
    """
    )
