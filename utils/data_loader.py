from pathlib import Path

import pandas as pd
import streamlit as st


PRIME_PICKUP_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "prime_pickup.parquet"
)


@st.cache_data
def load_prime_pickup_file():
    if not PRIME_PICKUP_PATH.exists():
        raise FileNotFoundError(
            "Prime Pickup data is missing. "
            "Run scripts/refresh_prime_pickup.py first."
        )

    return pd.read_parquet(PRIME_PICKUP_PATH)


def load_trip_data(weekday_num: int, start_hour: int) -> pd.DataFrame:
    df = load_prime_pickup_file()

    return df.loc[
        (df["weekday_num"] == weekday_num)
        & (df["start_hour"] == start_hour)
    ].copy()