# ============================================================
# Rural Healthcare Navigator
#
# Chat UI Component
#
# Handles:
#   - Conversation rendering
#   - Message formatting
#   - Scrollable chat window
#
# No backend logic.
#
# ============================================================


import streamlit as st

from src.frontend.ui.alerts import render_emergency_alert



# ============================================================
# CHAT HISTORY
# ============================================================


def render_chat_history(history: list) -> None:

    """
    Render previous conversation messages.

    Uses Streamlit chat_message
    with healthcare themed avatars.
    """


    for message in history:


        role = message.get(
            "role",
            "assistant"
        )


        content = message.get(
            "content",
            ""
        )


        kind = message.get(
            "kind"
        )


        avatar = (

            "🩺"

            if role == "assistant"

            else

            "🙂"

        )


        with st.chat_message(

            role,

            avatar=avatar

        ):

            if kind == "emergency":

                render_emergency_alert(content)

            else:

                st.markdown(content)




# ============================================================
# SCROLLABLE CHAT WINDOW
# ============================================================


def render_scrollable_chat(history: list) -> None:

    """
    Render chat inside fixed-height window.

    This prevents users from scrolling through
    the entire browser page.

    Input section stays visible below.
    """


    with st.container(
        height=500
    ):


        render_chat_history(
            history
        )



    # Move browser view to bottom

    _auto_scroll()



# ============================================================
# AUTO SCROLL
# ============================================================


def _auto_scroll() -> None:

    """
    Automatically scroll browser to latest message.

    Streamlit does not expose native chat
    scrolling control, so JavaScript is used.
    """


    st.markdown(

        """

        <script>

        window.scrollTo(
            0,
            document.body.scrollHeight
        );

        </script>

        """,

        unsafe_allow_html=True,

    )



# ============================================================
# ASSISTANT MESSAGE FORMATTER
# ============================================================


def assistant_text(chat_output: dict) -> str:

    """
    Convert graph chat_output into
    displayable assistant message.

    Logic preserved from original app.
    """


    question = chat_output.get(
        "question"
    )


    display_message = chat_output.get(
        "display_message"
    )



    if chat_output.get(
        "input_required"
    ):


        if (
            display_message
            and
            question
        ):

            return (

                "{}\n\n{}".format(

                    display_message,

                    question

                )

            )


        return (

            question

            or

            display_message

            or

            ""

        )



    return (

        display_message

        or

        ""

    )



# ============================================================
# USER MESSAGE DISPLAY
# ============================================================


def render_user_message(
    message: str
) -> None:

    """
    Display user submitted message.
    """


    with st.chat_message(

        "user",

        avatar="🙂"

    ):

        st.markdown(
            message
        )