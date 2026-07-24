# utils/style.py
import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* General text elements */
        .stApp,
        .stApp p,
        .stApp label,
        .stApp button,
        .stApp input,
        .stApp select,
        .stApp textarea {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* Streamlit headings and titles */
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6,
        [data-testid="stHeading"],
        [data-testid="stHeading"] * {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            letter-spacing: -0.035em;
        }

        .stApp h1 {
            font-weight: 800 !important;
        }

        .stApp h2,
        .stApp h3 {
            font-weight: 700 !important;
        }

        /* Preserve Streamlit/Material icons */
        .material-symbols-rounded,
        .material-symbols-outlined,
        [data-testid="stIconMaterial"] {
            font-family: "Material Symbols Rounded",
                         "Material Symbols Outlined" !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )