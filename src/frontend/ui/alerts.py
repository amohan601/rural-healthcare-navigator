# ============================================================
# Rural Healthcare Navigator
#
# Alert Components
#
# Handles:
#   - Emergency alerts
#   - Warning messages
#   - Informational status
#
# UI only.
#
# ============================================================


import streamlit as st



# ============================================================
# EMERGENCY ALERT
# ============================================================


def render_emergency_alert(
    message: str
) -> None:

    """
    Display emergency/high urgency alert.

    Used when:
        urgency == HIGH

    Designed to immediately attract attention.
    """


    st.markdown(

        f"""

        <div class="emergency-alert">


            <div class="emergency-title">

                🚨 Urgent Medical Attention

            </div>


            <br>


            <div style="
                font-size:18px;
                color:#7F1D1D;
            ">

                {message}

            </div>


            <hr>


            <div style="
                font-weight:700;
                color:#991B1B;
                font-size:16px;
            ">

                Recommended next steps:

            </div>


            <ul style="
                color:#7F1D1D;
                font-size:16px;
            ">


                <li>
                    Seek immediate medical evaluation
                </li>


                <li>
                    Call emergency services if symptoms worsen
                </li>


                <li>
                    Do not delay urgent care
                </li>


            </ul>


        </div>

        """,

        unsafe_allow_html=True,

    )



# ============================================================
# MEDIUM URGENCY
# ============================================================


def render_warning_alert(
    message: str
) -> None:

    """
    Display moderate urgency warning.
    """


    st.warning(

        f"""
        🟡 **Medical Attention Recommended**

        {message}

        """

    )



# ============================================================
# NORMAL INFORMATION
# ============================================================


def render_info_alert(
    message: str
) -> None:

    """
    Display normal assistant status.
    """


    st.info(

        message

    )



# ============================================================
# TRIAGE ROUTER
# ============================================================


def render_triage_message(
    urgency: str,
    message: str
) -> None:

    """
    Select alert style based on urgency
    or emergency wording.
    """


    emergency_keywords = [
        "immediate medical attention",
        "emergency",
        "seek immediate",
        "call 911",
        "nearest healthcare facility",
        "urgent medical",
        "life threatening",
    ]


    message_lower = (
        message.lower()
        if message
        else ""
    )


    is_emergency = any(
        keyword in message_lower
        for keyword in emergency_keywords
    )


    if (
        urgency == "HIGH"
        or is_emergency
    ):

        render_emergency_alert(
            message
        )


    elif urgency == "MEDIUM":

        render_warning_alert(
            message
        )


    else:

        render_info_alert(
            message
        )