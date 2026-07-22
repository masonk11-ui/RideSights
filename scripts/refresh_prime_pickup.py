from pathlib import Path

import pandas as pd
from sodapy import Socrata

START_DATE = "2026-05-04T00:00:00"
END_DATE = "2026-06-01T00:00:00"


DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "prime_pickup.parquet"
)


def get_client():
    return Socrata(
        "data.cityofchicago.org",
        app_token = "YFowgnbpx8mMjdYYeRr2g71KJ",
        timeout=5000
    )


def fetch_prime_pickup_data(client):
    results = client.get(
        "6dvr-xwnh",
        select="""
            date_extract_dow(trip_start_timestamp) AS weekday_num,
            date_extract_hh(trip_start_timestamp) AS start_hour,
            pickup_community_area,
            round(pickup_centroid_latitude, 2) AS latitude,
            round(pickup_centroid_longitude, 2) AS longitude,
            count(*) AS total_trips,
            sum(trip_total) AS total_trip_value,
            sum(trip_miles) AS total_miles,
            sum(trip_seconds) AS total_seconds
        """,
        where=f"""
            trip_start_timestamp >= '2026-05-25T00:00:00'
            AND trip_start_timestamp < '2026-06-01T00:00:00'
            AND pickup_centroid_latitude IS NOT NULL
            AND pickup_centroid_longitude IS NOT NULL
            AND pickup_community_area IS NOT NULL
            AND trip_miles > 0
            AND trip_seconds > 0
            AND fare > 1
        """,
        group="""
            date_extract_dow(trip_start_timestamp),
            date_extract_hh(trip_start_timestamp),
            pickup_community_area,
            round(pickup_centroid_latitude, 2),
            round(pickup_centroid_longitude, 2)
        """,
        limit=100000
    )

    return pd.DataFrame.from_records(results)


def clean_prime_pickup_data(df):
    numeric_columns = [
        "weekday_num",
        "start_hour",
        "pickup_community_area",
        "latitude",
        "longitude",
        "total_trips",
        "total_trip_value",
        "total_miles",
        "total_seconds",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=[
            "weekday_num",
            "start_hour",
            "pickup_community_area",
            "latitude",
            "longitude",
            "total_trips",
        ]
    ).copy()

    integer_columns = [
        "weekday_num",
        "start_hour",
        "pickup_community_area",
        "total_trips",
    ]

    for column in integer_columns:
        df[column] = df[column].astype(int)

    df["avg_trip_value"] = (
        df["total_trip_value"] / df["total_trips"]
    )

    df["avg_trip_miles"] = (
        df["total_miles"] / df["total_trips"]
    )

    df["avg_trip_minutes"] = (
        df["total_seconds"] / df["total_trips"] / 60
    )


    return df


def main():
    client = get_client()

    print("Downloading Prime Pickup data...")
    df = fetch_prime_pickup_data(client)

    print(f"Downloaded {len(df):,} aggregated rows.")

    if len(df) == 100000:
        raise RuntimeError(
            "The query returned exactly 100,000 rows and may be truncated."
        )

    df = clean_prime_pickup_data(df)

    df["data_start_date"] = pd.to_datetime(START_DATE).date()

    df["data_end_date"] = (
        pd.to_datetime(END_DATE) - pd.Timedelta(days=1)
    ).date()

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DATA_PATH, index=False)

    print(f"Saved {len(df):,} rows to {DATA_PATH}")


if __name__ == "__main__":
    main()