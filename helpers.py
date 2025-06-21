import streamlit as st 

def session_state_init():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'user_email' not in st.session_state: 
        st.session_state['user_email'] = None
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = True 
    if'show_verification' not in st.session_state:
        st.session_state['show_verification'] = False 
    if 'llm' not in st.session_state: 
        st.session_state['llm'] = None
    if 'course_id' not in st.session_state: 
        st.session_state['course_id'] = None
    if 'course_name' not in st.session_state: 
        st.session_state['course_name'] = None
    
def hide_streamlit_bar():
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def check_logged_in(): 
    if st.session_state['logged_in'] == False or st.session_state['user_id'] == None: 
        return False 
    return True

def redirect_to_main(): 
    st.switch_page("app.py")
    st.rerun()

def redirect_to_courses(): 
    st.switch_page("pages/courses_page.py")
    st.rerun()