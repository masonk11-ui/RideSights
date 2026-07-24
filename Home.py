import streamlit as st


import streamlit as st
from utils.style import apply_global_styles


st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #1C2129;
        color: white;
        border: 1px solid #343B46;
        border-radius: 10px;
        padding: 0.7rem 1.25rem;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #252B34;
        border-color: #6B7280;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

apply_global_styles()

st.set_page_config(
    page_title="RideSights",
    layout="wide"
)

apply_global_styles()

st.title("RideSights")
st.write("### Make more. Drive less.")

st.write(
    "RideSights transforms millions of historical Chicago rideshare trips "
    "into actionable driving recommendations."
)

st.divider()

st.subheader("Find Your Ride Strategy")

st.write(
    "Choose when you plan to drive and what you want to optimize. "
    "Get a recommended pickup area, neighborhood rankings, and an interactive demand heatmap."
)

if st.button(
    "🚕 Get My Ride Strategy",
    key="ride_strategy_cta",
):
    st.switch_page("pages/1 Ride Strategy.py")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.metric("Historical Trips", "4M+")

with col2:
    st.metric("Chicago Community Areas", "77")


st.caption(
    "Built with historical rideshare data reported to the City of Chicago. "
    "Recommendations do not reflect live demand."
)