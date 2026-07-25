# ============================================================
# Rural Healthcare Navigator
#
# Streamlit Application Entry Point
#
# Responsibilities:
#   - UI orchestration
#   - User interaction
#   - Calling LangGraph workflow
#
# Does NOT contain:
#   - Agent logic
#   - Routing logic
#   - Triage logic
#
# ============================================================


import uuid

import streamlit as st

from dotenv import load_dotenv


load_dotenv()



from src.backend.graph.supervisor import run_graph



# UI Components


from src.frontend.ui.styles import (
    apply_styles
)


from src.frontend.ui.state import (
    init_session_state
)


from src.frontend.ui.sidebar import (
    render_sidebar
)


from src.frontend.ui.chat import (
    render_scrollable_chat,
    assistant_text,
    render_user_message,
)


from src.frontend.ui.providers import (
    render_provider_selection
)





# ============================================================
# PAGE CONFIG
# ============================================================


st.set_page_config(

    page_title="Rural Healthcare Navigator",

    page_icon="🏥",

    layout="wide"

)



apply_styles()




# ============================================================
# HEADER
# ============================================================


def render_header():

    st.markdown(

        """

        # 🩺 Rural Healthcare Navigator


        AI-powered healthcare navigation assistant


        """

    )





# ============================================================
# PROCESS GRAPH REQUEST
# ============================================================


def process_pending_message():


    st.divider()


    st.markdown(

        "## 💬 Conversation"

    )



    render_scrollable_chat(

        st.session_state.chat_messages

    )



    render_user_message(

        st.session_state.pending_message_display

        or

        st.session_state.pending_message

    )



    with st.spinner(

        "🩺 Thinking..."

    ):


        result = run_graph(

            most_recent_user_input=

                st.session_state.pending_message,


            thread_id=

                st.session_state.thread_id

        )



    print(

        f"[streamlit_app] result: {result}"

    )



    # Save user message


    st.session_state.chat_messages.append(

        {

            "role":

                "user",


            "content":

                st.session_state.pending_message_display

                or

                st.session_state.pending_message

        }

    )



    st.session_state.chat_output = (

        result.get(

            "chat_output",

            {}

        )

    )



    assistant_message = assistant_text(

        st.session_state.chat_output

    )



    is_emergency = (

        st.session_state.chat_output.get(

            "input_type"

        )

        ==

        "status_emergency"

    )



    if assistant_message:


        message = {

            "role":

                "assistant",


            "content":

                assistant_message

        }

        if is_emergency:

            message["kind"] = "emergency"

        st.session_state.chat_messages.append(message)



    # Reset


    st.session_state.pending_message = None


    st.session_state.pending_message_display = None


    st.session_state.is_processing = False



    st.rerun()





# ============================================================
# MAIN
# ============================================================


def main():


    init_session_state()



    render_sidebar()



    render_header()




    # --------------------------------------------------------
    # Waiting for LangGraph response
    # --------------------------------------------------------


    if (

        st.session_state.is_processing

        and

        st.session_state.pending_message

    ):


        process_pending_message()


        return





    # --------------------------------------------------------
    # Existing conversation
    # --------------------------------------------------------


    if st.session_state.chat_messages:


        st.divider()


        st.markdown(

            "## 💬 Conversation"

        )


        render_scrollable_chat(

            st.session_state.chat_messages

        )





    # --------------------------------------------------------
    # Determine if input should show
    #
    # SAME LOGIC AS ORIGINAL
    # --------------------------------------------------------


    input_required = (

        st.session_state.chat_output.get(

            "input_required",

            True

        )

    )



    show_input = (

        input_required

        or

        not st.session_state.chat_messages

    )




    if show_input:



        input_type = (

            st.session_state.chat_output.get(

                "input_type"

            )

        )





        # ====================================================
        # PROVIDER SELECTION
        # ====================================================


        if input_type == "provider_selection":



            selected_index, selected_name = (

                render_provider_selection(

                    st.session_state.chat_output,


                    disabled=

                        st.session_state.is_processing

                )

            )



            send_disabled = (

                st.session_state.is_processing

                or

                not input_required

                or

                selected_index is None

            )



            if st.button(

                "➡️ Continue",

                type="primary",

                disabled=send_disabled

            ):



                st.session_state.pending_message = (

                    str(selected_index)

                )



                st.session_state.pending_message_display = (

                    selected_name

                )



                st.session_state.is_processing = True



                st.session_state.input_version += 1



                st.rerun()





        # ====================================================
        # NORMAL INPUT
        # ====================================================


        else:



            prompt = (

                st.session_state.chat_output.get(

                    "question"

                )

                or

                "How can we help you today?"

            )



            user_input = st.text_input(

                prompt,


                key=(

                    f"user_input_"

                    f"{st.session_state.input_version}"

                ),


                disabled=

                    st.session_state.is_processing

            )



            send_disabled = (

                st.session_state.is_processing

                or

                not input_required

                or

                not user_input.strip()

            )



            if st.button(

                "➡️ Send",

                type="primary",

                disabled=send_disabled

            ):


                st.session_state.pending_message = (

                    user_input.strip()

                )



                st.session_state.pending_message_display = None



                st.session_state.is_processing = True



                st.session_state.input_version += 1



                st.rerun()





    # --------------------------------------------------------
    # New conversation
    # --------------------------------------------------------


    if not st.session_state.chat_output.get(

        "input_required",

        True

    ):


        st.divider()



        if st.button(

            "🔄 Start New Conversation"

        ):



            st.session_state.thread_id = (

                str(uuid.uuid4())

            )



            st.session_state.chat_messages = []



            st.session_state.chat_output = {

                "input_required":

                    True,


                "input_type":

                    "interview_question",


                "question":

                    "How can we help you today?",


                "display_message":

                    None

            }



            st.session_state.is_processing = False



            st.session_state.pending_message = None



            st.session_state.pending_message_display = None



            st.session_state.input_version += 1



            st.rerun()





# ============================================================
# RUN
# ============================================================


if __name__ == "__main__":

    main()