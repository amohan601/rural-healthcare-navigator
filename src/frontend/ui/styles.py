# ============================================================
# Rural Healthcare Navigator
#
# Streamlit UI Theme
#
# Contains:
#   - Healthcare color palette
#   - Global CSS
#   - Component styling
#
# No application logic.
#
# ============================================================


import streamlit as st



def apply_styles() -> None:

    """
    Apply global Streamlit styling.

    Theme:
        Healthcare Blue
        Medical Green
        Emergency Red

    """

    st.markdown(
        """

<style>


/* ==========================================================
   GLOBAL PAGE
========================================================== */


.stApp {

    background-color:#F8FAFC;

}


.block-container {

    max-width:1000px;

    padding-top:2rem;

    padding-bottom:3rem;

}




/* ==========================================================
   HIDE STREAMLIT DEFAULT UI
========================================================== */


#MainMenu {

    visibility:hidden;

}


footer {

    visibility:hidden;

}


header {

    visibility:hidden;

}




/* ==========================================================
   TYPOGRAPHY
========================================================== */


h1 {

    color:#1E3A8A;

    font-weight:800;

}


h2 {

    color:#1E40AF;

}


h3 {

    color:#334155;

}


p {

    color:#334155;

}





/* ==========================================================
   SIDEBAR
========================================================== */


section[data-testid="stSidebar"] {


    background:

    linear-gradient(

        180deg,

        #EFF6FF,

        #F0FDF4

    );

}



section[data-testid="stSidebar"] h2 {


    color:#1E3A8A;

}




/* ==========================================================
   BUTTONS
========================================================== */


.stButton > button {


    background:#2563EB;


    color:white;


    border-radius:12px;


    height:45px;


    font-weight:600;


    border:none;


}



.stButton > button:hover {


    background:#1D4ED8;


    color:white;


}




/* ==========================================================
   INPUT BOX
========================================================== */


.stTextInput input {


    background:white;


    border-radius:12px;


    border:1px solid #CBD5E1;


    height:45px;


    font-size:16px;


}




/* ==========================================================
   CHAT MESSAGE CONTAINERS
========================================================== */


div[data-testid="stChatMessage"] {


    border-radius:18px;


    padding:12px;


    margin-bottom:12px;


    border:1px solid #E2E8F0;


    background:white;


}




/* ==========================================================
   PROVIDER CARDS
========================================================== */


div[data-testid="stVerticalBlockBorderWrapper"] {


    background:white;


    border-radius:18px;


    border:

        1px solid #E2E8F0;


    padding:10px;


    box-shadow:

        0px 4px 12px rgba(15,23,42,0.06);


}



/* ==========================================================
   METRIC CARDS
========================================================== */


div[data-testid="metric-container"] {


    background:#EFF6FF;


    border-radius:14px;


    padding:12px;


    border:

        1px solid #DBEAFE;


}




/* ==========================================================
   BADGES
========================================================== */


.provider-badge {


    display:inline-block;


    padding:

        5px 12px;


    margin:

        3px;


    border-radius:

        20px;


    font-size:

        14px;


    font-weight:

        600;


}



.badge-open {


    background:#DCFCE7;

    color:#166534;

}



.badge-telehealth {


    background:#DBEAFE;

    color:#1E40AF;

}



.badge-scale {


    background:#F3E8FF;

    color:#6B21A8;

}



.badge-fqhc {


    background:#FFEDD5;

    color:#9A3412;

}




/* ==========================================================
   EMERGENCY ALERT
========================================================== */


@keyframes emergencyPulse {


    0% {


        box-shadow:

        0 0 0 0 rgba(220,38,38,0.5);

    }



    70% {


        box-shadow:

        0 0 0 15px rgba(220,38,38,0);

    }



    100% {


        box-shadow:

        0 0 0 0 rgba(220,38,38,0);

    }


}




.emergency-alert {


    background:#FEF2F2;


    border-left:

        8px solid #DC2626;


    border-radius:16px;


    padding:20px;


    animation:

        emergencyPulse 2s infinite;


}




.emergency-title {


    color:#B91C1C;


    font-size:24px;


    font-weight:800;


}





/* ==========================================================
   SELECTED PROVIDER
========================================================== */


.selected-provider {


    background:#F0FDF4;


    border:

        3px solid #16A34A;


    border-radius:18px;


    padding:15px;


}




/* ==========================================================
   SCROLLABLE CHAT WINDOW
========================================================== */


.chat-window {


    height:500px;


    overflow-y:auto;


    padding:10px;


    border-radius:16px;


}




/* ==========================================================
   DIVIDERS
========================================================== */


hr {


    border-color:#E2E8F0;


}



</style>

        """,

        unsafe_allow_html=True,

    )