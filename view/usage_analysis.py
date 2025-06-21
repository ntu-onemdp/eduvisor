
# from database import *
# import streamlit as st
# from streamlit_elements import elements, mui

# MAX_CHAR_LIMIT = 400
# MAX_TOKEN_LIMIT = 150000

# def tokens_and_chat_card(progress_value, num_chats, admin = False):
#     title_chat = "Total Chat Interactions" 
#     title_tokens = "Token Utilization" if not admin else "Average Token Utilization"
#     if admin: 
#         st.info('ⓘ The statistics below reflect data for all students.')

#     with elements("mui_card"):
#         mui.Card(
#             sx={
#                 "maxWidth": 700,
#                 "margin": "auto",
#                 "padding": 3,
#                 "boxShadow": 3,
#                 "borderRadius": 2,
#                 "@media (max-width: 600px)": {"padding": 2, "maxWidth": "100%"},
#             }
#         )(
#             mui.CardContent(
#                 sx={
#                     "display": "flex",
#                     "flexDirection": "column",
#                     "alignItems": "center",
#                     "justifyContent": "center",
#                     "gap": 3,
#                 }
#             )(
#                 mui.Box(
#                     sx={
#                         "display": "flex",
#                         "flexDirection": "row",
#                         "alignItems": "center",
#                         "justifyContent": "space-around",
#                         "gap": 8,
#                         "width": "100%",
#                         "@media (max-width: 600px)": {"flexDirection": "column", "gap": 4},
#                     }
#                 )(
#                     # Token Utilization Section
#                     mui.Box(
#                         sx={"display": "flex", "flexDirection": "column", "alignItems": "center", "gap": 1}
#                     )(
#                         mui.Box(
#                             sx={
#                                 "position": "relative",
#                                 "display": "inline-flex",
#                                 "alignItems": "center",
#                                 "justifyContent": "center",
#                             }
#                         )(
#                             mui.CircularProgress(
#                                 variant="determinate",
#                                 value=100,
#                                 size=100,
#                                 thickness=4,
#                                 sx={"color": "#e0e0e0", "@media (max-width: 600px)": {"size": 80}},
#                             ),
#                             mui.CircularProgress(
#                                 variant="determinate",
#                                 value=progress_value,
#                                 size=100,
#                                 thickness=4,
#                                 sx={
#                                     "& .MuiCircularProgress-circle": {"strokeLinecap": "round"},
#                                     "color": "#1B62B7",
#                                     "position": "absolute",
#                                     "@media (max-width: 600px)": {"size": 80},
#                                 },
#                             ),
#                             mui.Typography(
#                                 variant="h6",
#                                 component="div",
#                                 sx={
#                                     "position": "absolute",
#                                     "color": "#1B62B7",
#                                     "@media (max-width: 600px)": {"fontSize": "0.9rem"},
#                                 },
#                             )(f"{progress_value:.2f}%"),
#                         ),
#                         mui.Typography(
#                             variant="subtitle1",
#                             component="div",
#                             color="textPrimary",
#                             sx={"@media (max-width: 600px)": {"fontSize": "0.8rem"}},
#                         )(title_tokens),
#                     ),
#                     # Chat Interactions Section
#                     mui.Box(
#                         sx={"display": "flex", "flexDirection": "column", "alignItems": "center", "gap": 1}
#                     )(
#                         mui.Typography(
#                             variant="h3",
#                             component="div",
#                             sx={
            
#                                 "color": "#1B62B7",
#                                 "@media (max-width: 600px)": {"fontSize": "1.5rem"},
#                             },
#                         )(f"{num_chats}"),
#                         mui.Typography(
#                             variant="subtitle1",
#                             component="div",
#                             color="textPrimary",
#                             sx={"@media (max-width: 600px)": {"fontSize": "0.8rem"}},
#                         )(title_chat),
#                     ),
#                 ),
#             ),
#         )



# def usage_graph(user_id, users, admin): 
   
#     # get tokens used
#     if admin: 
#         tokens_used_response = users.get_average_token_usage()
#     else:
#         tokens_used_response = users.get_user_tokens_used(user_id)

#     if tokens_used_response["code"] == 200:
#         user_tokens_used = tokens_used_response["data"]
#     else:
#         st.error("Failed to retrieve token usage.")
#         return
    
#     token_progress_value = round((user_tokens_used / MAX_TOKEN_LIMIT) * 100, 2)
#     if token_progress_value >100: 
#         token_progress_value = 100
    
#     # get chat count
#     if admin: 
#         chat_count_response = users.get_total_chat_count()
#     else: 
#         chat_count_response = users.get_user_chat_count(user_id)

#     if chat_count_response["code"] == 200:
#         chat_progress_value = chat_count_response["data"]
#     else:
#         st.error("Failed to retrieve chat count.")
#         return

#     tokens_and_chat_card(token_progress_value, chat_progress_value,admin)


import streamlit as st
from streamlit_elements import elements, mui
from controllers.insights_controller import InsightsController

MAX_TOKEN_LIMIT = 150000

class UsageAnalysisView:
    """Handles UI interactions for usage analysis in Streamlit."""

    def __init__(self, controller: InsightsController):
        """Initialize the view with a controller instance."""
        self.controller = controller

    def display_usage_graph(self, user_id, is_admin):
        """Fetches and displays token and chat usage statistics."""

        with st.spinner("Fetching usage statistics..."):
            tokens_used, chat_count = self.controller.get_token_and_chat_usage(user_id, is_admin)

            if tokens_used is None or chat_count is None:
                st.error("Failed to retrieve usage data.")
                return

            # Normalize token usage percentage
            token_progress_value = round((tokens_used / MAX_TOKEN_LIMIT) * 100, 2)
            token_progress_value = min(token_progress_value, 100)

            self._display_usage_card(token_progress_value, chat_count, is_admin)

    def _display_usage_card(self, progress_value, num_chats, is_admin):
        """Displays the UI for token and chat usage statistics."""
        title_chat = "Total Chat Interactions"
        title_tokens = "Token Utilization" if not is_admin else "Average Token Utilization"

        if is_admin:
            st.info("ⓘ The statistics below reflect data for all users.")

        with elements("mui_card"):
            mui.Card(
                sx={
                    "maxWidth": 700,
                    "margin": "auto",
                    "padding": 3,
                    "boxShadow": 3,
                    "borderRadius": 2,
                    "@media (max-width: 600px)": {"padding": 2, "maxWidth": "100%"},
                }
            )(
                mui.CardContent(
                    sx={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "gap": 3,
                    }
                )(
                    mui.Box(
                        sx={
                            "display": "flex",
                            "flexDirection": "row",
                            "alignItems": "center",
                            "justifyContent": "space-around",
                            "gap": 8,
                            "width": "100%",
                            "@media (max-width: 600px)": {"flexDirection": "column", "gap": 4},
                        }
                    )(
                        # Token Utilization Section
                        mui.Box(
                            sx={"display": "flex", "flexDirection": "column", "alignItems": "center", "gap": 1}
                        )(
                            mui.Box(
                                sx={
                                    "position": "relative",
                                    "display": "inline-flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                }
                            )(
                                mui.CircularProgress(
                                    variant="determinate",
                                    value=100,
                                    size=100,
                                    thickness=4,
                                    sx={"color": "#e0e0e0", "@media (max-width: 600px)": {"size": 80}},
                                ),
                                mui.CircularProgress(
                                    variant="determinate",
                                    value=progress_value,
                                    size=100,
                                    thickness=4,
                                    sx={
                                        "& .MuiCircularProgress-circle": {"strokeLinecap": "round"},
                                        "color": "#1B62B7",
                                        "position": "absolute",
                                        "@media (max-width: 600px)": {"size": 80},
                                    },
                                ),
                                mui.Typography(
                                    variant="h6",
                                    component="div",
                                    sx={
                                        "position": "absolute",
                                        "color": "#1B62B7",
                                        "@media (max-width: 600px)": {"fontSize": "0.9rem"},
                                    },
                                )(f"{progress_value:.2f}%"),
                            ),
                            mui.Typography(
                                variant="subtitle1",
                                component="div",
                                color="textPrimary",
                                sx={"@media (max-width: 600px)": {"fontSize": "0.8rem"}},
                            )(title_tokens),
                        ),
                        # Chat Interactions Section
                        mui.Box(
                            sx={"display": "flex", "flexDirection": "column", "alignItems": "center", "gap": 1}
                        )(
                            mui.Typography(
                                variant="h3",
                                component="div",
                                sx={
                                    "color": "#1B62B7",
                                    "@media (max-width: 600px)": {"fontSize": "1.5rem"},
                                },
                            )(f"{num_chats}"),
                            mui.Typography(
                                variant="subtitle1",
                                component="div",
                                color="textPrimary",
                                sx={"@media (max-width: 600px)": {"fontSize": "0.8rem"}},
                            )(title_chat),
                        ),
                    ),
                ),
            )
