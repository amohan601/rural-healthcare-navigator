# ============================================================
# Rural Healthcare Navigator
#
# Provider UI Components
#
# Handles:
#   - Provider cards
#   - Provider selection
#   - Ratings
#   - Distance
#   - Healthcare badges
#
# UI only.
#
# ============================================================


import streamlit as st




# ============================================================
# SAFE FIELD ACCESS
# ============================================================


def _field(
    obj,
    name,
    default=None
):

    """
    Supports both:
        dict objects
        pydantic objects
    """


    if isinstance(obj, dict):

        return obj.get(
            name,
            default
        )


    return getattr(
        obj,
        name,
        default
    )




# ============================================================
# BADGE
# ============================================================


def _badge(
    text,
    css_class
):

    st.markdown(

        f"""

        <span class="provider-badge {css_class}">

            {text}

        </span>

        """,

        unsafe_allow_html=True,

    )




# ============================================================
# PROVIDER CARD
# ============================================================


def render_provider_card(
    idx,
    provider,
    selected_index=None
):

    """
    Render one provider.

    Compact healthcare card.
    """


    is_selected = (

        idx == selected_index

    )



    container_class = (

        "selected-provider"

        if is_selected

        else

        ""

    )



    if container_class:


        st.markdown(

            '<div class="selected-provider">',

            unsafe_allow_html=True

        )



    with st.container(
        border=True
    ):


        name = _field(
            provider,
            "name",
            "Unknown Provider"
        )


        specialty = _field(
            provider,
            "specialty"
        )



        # --------------------------------
        # Header
        # --------------------------------


        st.markdown(

            f"""

            ### 🏥 {name}

            """,

        )


        if specialty:


            st.caption(

                f"🩺 {specialty}"

            )



        # --------------------------------
        # Metrics
        # --------------------------------


        col1, col2 = st.columns(2)



        with col1:


            rating = _field(
                provider,
                "rating"
            )


            if rating is not None:


                reviews = _field(
                    provider,
                    "review_count"
                )


                text = (

                    f"⭐ {rating}"

                )


                if reviews:


                    text += (

                        f" ({reviews})"

                    )


                st.metric(

                    "Rating",

                    text

                )



        with col2:


            distance = _field(
                provider,
                "distance_miles"
            )


            if distance is not None:


                st.metric(

                    "Distance",

                    f"🚗 {distance} mi"

                )



        # --------------------------------
        # Contact
        # --------------------------------


        address = _field(
            provider,
            "address"
        )


        if address:


            st.write(

                f"📍 {address}"

            )



        phone = _field(
            provider,
            "phone"
        )


        if phone:


            st.write(

                f"📞 {phone}"

            )



        # --------------------------------
        # Status badges
        # --------------------------------


        open_now = _field(
            provider,
            "open_now"
        )


        if open_now is True:


            _badge(

                "🟢 Open Now",

                "badge-open"

            )


        elif open_now is False:


            _badge(

                "Closed",

                "badge-fqhc"

            )



        if _field(
            provider,
            "telehealth"
        ):


            _badge(

                "💻 Telehealth",

                "badge-telehealth"

            )



        if _field(
            provider,
            "sliding_scale"
        ):


            _badge(

                "💲 Sliding Scale",

                "badge-scale"

            )



        if _field(
            provider,
            "is_fqhc"
        ):


            _badge(

                "🏥 FQHC",

                "badge-fqhc"

            )



        # --------------------------------
        # Hours
        # --------------------------------


        hours = _field(
            provider,
            "weekday_hours"
        )


        if hours:


            with st.expander(
                "🕒 Hours"
            ):

                for item in hours:

                    st.write(
                        item
                    )



        # --------------------------------
        # Pharmacy
        # --------------------------------


        pharmacy = _field(
            provider,
            "pharmacy_nearby"
        )



        if pharmacy:


            st.markdown(
                "**💊 Nearby Pharmacy**"
            )


            pharmacy_name = _field(
                pharmacy,
                "name"
            )


            if pharmacy_name:


                st.write(

                    pharmacy_name

                )


            pharmacy_distance = _field(
                pharmacy,
                "distance_miles"
            )


            if pharmacy_distance is not None:


                st.caption(

                    f"🚗 {pharmacy_distance} miles away"

                )



    if container_class:


        st.markdown(

            "</div>",

            unsafe_allow_html=True

        )



# ============================================================
# PROVIDER SELECTION
# ============================================================


def render_provider_selection(
    chat_output: dict,
    disabled: bool,
    selected_index=None
):

    """
    Render providers and selection radio.

    Returns:

        (
            selected_index,
            selected_provider_name
        )

    """


    providers = (

        chat_output.get(
            "options"
        )

        or []

    )



    if not providers:


        st.info(
            "No providers found."
        )


        return None, None



    st.markdown(

        "## 📍 Healthcare Providers Near You"

    )


    st.caption(

        f"Found {len(providers)} healthcare options"

    )



    # --------------------------------
    # Two-column layout
    # --------------------------------


    cols = st.columns(2)



    for idx, provider in enumerate(providers):


        with cols[idx % 2]:


            render_provider_card(

                idx,

                provider,

                selected_index

            )



    # --------------------------------
    # Selection
    # --------------------------------


    labels = [

        f"{idx+1}. {_field(provider,'name','Unknown Provider')}"

        for idx, provider

        in enumerate(providers)

    ]



    selected_label = st.radio(

        chat_output.get(

            "question",

            "Select a provider"

        ),


        labels,


        index=None,


        disabled=disabled,


        key=(

            f"provider_radio_"

            f"{st.session_state.input_version}"

        )

    )



    if selected_label is None:


        return None, None



    index = labels.index(
        selected_label
    )


    return (

        index,

        _field(

            providers[index],

            "name",

            "Unknown Provider"

        )

    )