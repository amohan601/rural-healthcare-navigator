# ============================================================
# Rural Healthcare Navigator
#
# Streamlit Session State Management
#
# Keeps frontend state initialization separate
# from UI rendering.
#
# ============================================================


import uuid

import streamlit as st



def init_session_state() -> None:

    """
    Initialize Streamlit session variables.

    IMPORTANT:
    These keys are shared with the LangGraph workflow.

    Do not rename without updating the rest
    of the application.
    """


    defaults = {


        # Unique conversation identifier
        #
        # Used by LangGraph checkpointing
        #

        "thread_id":

            str(uuid.uuid4()),



        # Messages displayed in chat window
        #

        "chat_messages":

            [],



        # Current response state from graph
        #

        "chat_output": {


            "input_required":

                True,


            "input_type":

                "interview_question",


            "question":

                "How can we help you today?",


            "display_message":

                None,


        },



        # Prevent duplicate submissions
        #

        "is_processing":

            False,



        # Raw value sent to graph
        #

        "pending_message":

            None,



        # Human readable value displayed
        #
        # Example:
        # Provider selection:
        #
        # pending_message = "2"
        #
        # pending_message_display =
        # "WakeMed Primary Care"
        #

        "pending_message_display":

            None,



        # Forces Streamlit widgets
        # to recreate after rerun
        #

        "input_version":

            0,


    }



    for key, value in defaults.items():


        if key not in st.session_state:


            st.session_state[key] = value