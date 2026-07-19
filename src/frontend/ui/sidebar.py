# ============================================================
# Rural Healthcare Navigator
#
# Sidebar Component
#
# UI only.
#
# ============================================================


import streamlit as st



def render_sidebar() -> None:

    """
    Render application sidebar.

    Provides:
        - Application description
        - Capabilities
        - Architecture overview

    No workflow logic.
    """


    with st.sidebar:


        st.markdown(

            """

            ## 🏥 Rural Healthcare Navigator


            AI-powered healthcare assistant designed
            to help users navigate healthcare needs.


            ---


            ## 🤖 What I can help with


            💬 **Symptom Interview**

            Understand your healthcare concern
            through guided questions.



            🩺 **Medical Triage**

            Assess urgency and recommend
            appropriate next steps.



            📍 **Healthcare Resources**

            Find nearby clinics, providers,
            pharmacies, and community resources.



            📅 **Appointment Preparation**

            Prepare questions and information
            before visiting a provider.



            ---


            ## ⚙️ Powered By


            🔹 LangGraph Multi-Agent Workflow


            🔹 Retrieval Augmented Generation


            🔹 AI Tool Calling


            🔹 Healthcare Resource Search



            ---


            ## 🚨 Emergency Reminder


            If symptoms appear severe or life-threatening,
            seek immediate emergency assistance.



            """

        )