# import plotly.graph_objects as go
# import pandas as pd
# import streamlit as st 
# from database import *
# from savefiles import list_pdfs_for_course


# def count_chats_per_topic(user_id, topic_list, course_id, admin=False):
#     chats = ChatHistoryCollection()

#     if admin:
#         chat_history_response = chats.get_chat_history_by_course(course_id)
#     else:
#         chat_history_response = chats.get_chat_history(user_id, course_id)

#     if chat_history_response["code"] == 200:
#         chat_history = chat_history_response["data"]
#     else:
#         # If no data is found or there's an error, return an empty counter
#         return {topic: 0 for topic in topic_list} | {"Unknown": 0}

#     topic_counter = {topic: 0 for topic in topic_list}
#     topic_counter['Unknown'] = 0 

#     for chat in chat_history:
#         main_topic = chat.get("main_topic", "Unknown")
#         if main_topic in topic_counter:
#             topic_counter[main_topic] += 1
#         else:
#             topic_counter['Unknown'] += 1

#     return topic_counter

# #1.  edit to add if no pdfs, then we will js not display. 
# #2. make a markdown for the title for each graph, in blue

# def topic_graph(user_id,course_id,admin):
#     st.markdown(
#         """
#         <style>
#         .stats-title{color: #1B62B7;
#     font-size: 18px;
#     FONT-WEIGHT: 600;
#     display: flex;
#     justify-content: space-around;
#     align-items: center;
#     }
     
#         </style>

#             """, unsafe_allow_html=True)
    
    
#     list_response = list_pdfs_for_course(course_id)
#     topic_list = None

#     if list_response["code"] ==200: 
        
#         topic_list = sorted(list_response['data'])
#         if topic_list ==[]:
#             return

#     else: 
#         st.error('Failed to retrive topic list')
#         return

#     topic_counts = count_chats_per_topic(user_id, topic_list,course_id, admin)

#     if topic_counts:
#         df = pd.DataFrame(list(topic_counts.items()), columns=['Topic', 'Number of Chats'])

#         fig = go.Figure(data=[
#             go.Bar(
#                 x=df['Topic'],
#                 y=df['Number of Chats'],
#                  text=df['Number of Chats'],
#                 textposition='auto',
#                 marker=dict(color='#1B62B7')
#             )
#         ])

#         fig.update_layout(
          
#             xaxis_title='Topic',
#             yaxis_title='Number of Chats',
            
#             template='plotly_white'
#         )
#         st.markdown(f'<div class="stats-title">{course_id}</div>', unsafe_allow_html=True)

#         st.plotly_chart(fig, use_container_width=True,  key=f"topic_chart_{user_id}_{course_id}")
#     else:
#         st.write("No chat data available for this user.")

# def topic_graph_for_courses(user_id, courses,admin): 
#     all_courses_reponse = courses.get_courses()

#     if all_courses_reponse["code"] == 200:  
#         courses_list = all_courses_reponse['data']

#     else: 
#         st.error('No courses available')
#         return 
    
#     for course in courses_list: 
#         with st.spinner("Generating insights"):
#             topic_graph(user_id,course['course_id'],admin)


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from controllers.insights_controller import InsightsController

class ChatAnalysisView:
    """Handles UI interactions for topic-based chat analysis in Streamlit."""

    def __init__(self, controller: InsightsController):
        """Initialize the view with a controller instance."""
        self.controller = controller

    def display_topic_graph(self, user_id, course_id, is_admin):
        """Displays a bar chart showing chat distribution across topics."""

        # Fetch chat counts per topic
        topic_counts = self.controller.get_chat_counts_by_topic(user_id, course_id, is_admin)
        if topic_counts is None:
            return  # No topics available, exit function

        # Convert data to DataFrame
        df = pd.DataFrame(list(topic_counts.items()), columns=["Topic", "Number of Chats"])

        if df.empty:
            st.write("No chat data available for this user.")
            return

        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=df["Topic"],
                y=df["Number of Chats"],
                text=df["Number of Chats"],
                textposition="auto",
                marker=dict(color="#1B62B7")
            )
        ])

        fig.update_layout(
            xaxis_title="Topic",
            yaxis_title="Number of Chats",
            template="plotly_white"
        )

        # Title styling
        st.markdown(
            f"""
            <style>
            .stats-title {{
                color: #1B62B7;
                font-size: 18px;
                font-weight: 600;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f'<div class="stats-title">{course_id}</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, key=f"topic_chart_{user_id}_{course_id}")

    def display_topic_graphs_for_all_courses(self, user_id, is_admin):
        """Displays topic graphs for all available courses."""

        courses_list = self.controller.get_all_courses()
        if not courses_list:
            return

        for course in courses_list:
            course_id = course["course_id"]
            with st.spinner(f"Generating insights for {course_id}..."):
                self.display_topic_graph(user_id, course_id, is_admin)
