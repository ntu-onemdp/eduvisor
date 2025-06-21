import streamlit as st
from services.auth_service import AuthService
from helpers import *
from models.chat_history_model import ChatHistoryModel

#TODO: make component for key features box

def main():
    st.set_page_config(layout="wide",page_title="Home")
    
    with st.spinner('Loading'):
        hide_streamlit_bar()
        auth_service = AuthService()
        auth_url = auth_service.get_auth_url()
        
        app_css()

        st.markdown(
            f"""
            <div class="mainpage">
                <div class="welcome-header">Welcome to Eduvisor,</div>
                <div class="sub-header">your learning companion for academic support.</div>
                <div class="login-button">
                        <a href="{auth_url}" target="_blank" style="
                    background-color: #1B62B7;
                    color: white;
                    border: none;
                    padding: 2vh 3vw;
                    border-radius: 15px;
                    cursor: pointer;
                    text-decoration: none;
                    font-family: 'Source Sans Pro', sans-serif;
                    font-size: 2vh;
                    font-weight : normal;
                ">
                    Log in with NTU Account 📨</a>
                </div>
        <div class="information-box">ⓘ Only available for NTU 365 acccounts</div>  

        <div class = "key-features"> 
            <div class = "key-feature-box">
                <div class ="key-feature-box-title">✎ 24/7 Student Access</div> 
                <div class = "key-feature-box-content">Students can access the virtual teaching assistant at any time, extending support beyond traditional office hours.</div></div> 
            <div class = "key-feature-box">
        <div class ="key-feature-box-title"> ⊹₊⟡⋆ Insights Generation </div> 
            <div class = "key-feature-box-content">Students can access personalized insights to identify weaker topics and focus their questions for improved understanding.</div></div> 
                <div class = "key-feature-box">
                <div class ="key-feature-box-title">⋆.˚Easy Customisablity</div> 
            <div class = "key-feature-box-content">Educators can easily customize learning content to align with their course-specific goals and targetted educational outcomes.</div></div> 
        </div> </div>
            """,
            unsafe_allow_html=True,
        )

      
    

def app_css(): 
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lexend+Deca:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

        /* Main Page Layout */
        .mainpage { 
            font-family: 'Source Sans Pro';
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            color: black;
        }
        
        .welcome-header { 
            font-size: 6.5vh;
            padding: 0.2vw;
            text-align: center;
            margin-top: 7vh;
        }

        .sub-header {
            font-size: 2.4vh;
            text-align: center;
        }

        /* Login Button */
        .login-button { 
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 3.5vh;
            font-weight: 400;
        }
        
        .login-button a {
            background-color: #1B62B7;
            color: white;
            border: none;
            padding: 2vh 3vw;
            border-radius: 15px;
            cursor: pointer;
            text-decoration: none;
            font-family: 'Source Sans Pro', sans-serif;
            font-size: 2vh;
            font-weight: normal;
        }

        /* Information Box */
        .information-box { 
            display: flex;
            justify-content: center;
            align-items: center;
            color: black;
            background-color: #c2d6ff87;
            font-size: 1.53vh;
            padding: 1vw 2vw;
            border-radius: 8px;
        }

        /* Key Features Section */
        .key-features { 
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            width: 70%;
            margin-top: 5vh;
        }

        .key-feature-box {
            background-color: white;
            box-shadow: 0px 0px 50px 0.5px rgb(205, 208, 227);
            color: black;
            padding: 1vw;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 20px;
            text-align: center;
            font-size: 1.7vh;
            flex: 1 1 calc(30% - 2vw);
            margin: 1vh;
            min-height: 200px;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .key-features {
                flex-direction: column;
                align-items: center;
                width: 100%;
            }

            .key-feature-box {
                flex: 1 1 90%;
                min-height: auto;
            }
        }

        .key-feature-box-title {
            color: #1B62B7;
            font-weight: 500;
            font-size: 2vh;
            margin-bottom: 5px;
            margin-top: 5px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
if __name__ == "__main__":
    main()
