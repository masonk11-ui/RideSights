import streamlit as st

st.set_page_config(
    page_title="RideSights",
    layout="wide"
)

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

st.page_link(
    "pages/1 Ride Strategy.py",
    label="Get My Ride Strategy",
    icon= "🚕",
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Historical Trips", "4M+")

with col2:
    st.metric("Community Areas", "77")

with col3:
    st.metric("Driving Strategies", "3")

st.caption(
    "Built with historical rideshare data reported to the City of Chicago. "
    "Recommendations do not reflect live demand."
)