import streamlit as st
from utils.data_loader import load_trip_data
import pydeck as pdk
from utils.community_areas import COMMUNITY_AREA_NAMES
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils.style import apply_global_styles


def get_metric_status(pct_better):
    if pct_better >= 10:
        return "🟢", "green"
    elif pct_better >= -10:
        return "🟡", "orange"
    else:
        return "🔴", "red"
    


chicago_now = datetime.now(ZoneInfo("America/Chicago"))
next_hour = chicago_now + timedelta(hours=1)

default_weekday_num = (next_hour.weekday() + 1) % 7
default_hour_num = next_hour.hour


st.set_page_config(
    page_title="Prime Pickup | RideSights",
    page_icon="📍",
    layout="wide"
)

apply_global_styles()

st.title("Ride Strategy")
st.write("Personalized driving recommendations powered by historical City of Chicago rideshare data.")

weekday_options = {
    "Sunday": 0,
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6
}

default_weekday_index = list(weekday_options.values()).index(
    default_weekday_num
)

optimization_options = {
    "Staying Busy": "total_trips",
    "Quick Trip Turnover": "quick_trip_turnover",
    "Best Earnings Opportunity": "earnings_opportunity",
}


col1, col2 = st.columns(2)

with col1:
    selected_weekday = st.selectbox(
        "Day",
        weekday_options.keys(),
        index=default_weekday_index
    )

hour_options = {
    "12:00 AM": 0,
    "1:00 AM": 1,
    "2:00 AM": 2,
    "3:00 AM": 3,
    "4:00 AM": 4,
    "5:00 AM": 5,
    "6:00 AM": 6,
    "7:00 AM": 7,
    "8:00 AM": 8,
    "9:00 AM": 9,
    "10:00 AM": 10,
    "11:00 AM": 11,
    "12:00 PM": 12,
    "1:00 PM": 13,
    "2:00 PM": 14,
    "3:00 PM": 15,
    "4:00 PM": 16,
    "5:00 PM": 17,
    "6:00 PM": 18,
    "7:00 PM": 19,
    "8:00 PM": 20,
    "9:00 PM": 21,
    "10:00 PM": 22,
    "11:00 PM": 23,
}   

default_hour_index = list(hour_options.values()).index(
    default_hour_num
)

with col2:
    selected_hour = st.selectbox(
        "Hour",
        options=list(hour_options.keys()),
        index=default_hour_index
    )

selected_optimization = st.selectbox(
    "Optimize for",
    options=list(optimization_options.keys()),
)

df = load_trip_data(
    weekday_num=weekday_options[selected_weekday],
    start_hour=hour_options[selected_hour],
)

trips_analyzed = int(df["total_trips"].sum())


area_summary = (
    df.groupby("pickup_community_area", as_index=False)
    .agg(
        total_trips=("total_trips", "sum"),
        total_trip_value=("total_trip_value", "sum"),
        total_miles=("total_miles", "sum"),
        total_seconds=("total_seconds", "sum"),
    )
)

area_summary["avg_trip_value"] = (
    area_summary["total_trip_value"]
    / area_summary["total_trips"]
)

area_summary["avg_trip_miles"] = (
    area_summary["total_miles"]
    / area_summary["total_trips"]
)

area_summary["avg_trip_minutes"] = (
    area_summary["total_seconds"]
    / area_summary["total_trips"]
    / 60
)

area_summary["demand_percentile"] = (
    area_summary["total_trips"].rank(pct=True)
)

area_summary["short_trip_percentile"] = (
    area_summary["avg_trip_minutes"].rank(
        pct=True,
        ascending=False,
    )
)

area_summary["quick_trip_turnover"] = (
    0.30 * area_summary["demand_percentile"]
    + 0.70 * area_summary["short_trip_percentile"]
)

area_summary["pickup_community_area"] = pd.to_numeric(
    area_summary["pickup_community_area"],
    errors="coerce",
).astype("Int64")

area_summary["area_name"] = (
    area_summary["pickup_community_area"]
    .map(COMMUNITY_AREA_NAMES)
    .fillna("Unknown Area")
)

area_summary["gross_trip_value_per_hour"] = (
    area_summary["avg_trip_value"]
    / area_summary["avg_trip_minutes"]
    * 60
)

area_summary["gross_value_rate_percentile"] = (
    area_summary["gross_trip_value_per_hour"]
    .rank(pct=True)
)

demand_cutoff = area_summary["total_trips"].median()

area_summary["demand_rank"] = (
    area_summary["total_trips"]
    .rank(method="min", ascending=False)
    .astype(int)
)

area_summary["earnings_opportunity"] = (
    0.65 * area_summary["gross_value_rate_percentile"]
    + 0.35 * area_summary["demand_percentile"]
)

eligible_areas = area_summary[
    area_summary["total_trips"] >= demand_cutoff
].copy()

eligible_areas["earnings_rank"] = (
    eligible_areas["earnings_opportunity"]
    .rank(method="min", ascending=False)
    .astype(int)
)

eligible_area_count = len(eligible_areas)

median_trip_value = area_summary["avg_trip_value"].median()
median_trip_miles = area_summary["avg_trip_miles"].median()
median_trip_minutes = area_summary["avg_trip_minutes"].median()

### set recommended location equal to top area based on selected metric
if selected_optimization == "Staying Busy":
    ranked_areas = area_summary.sort_values(
        "total_trips",
        ascending=False,
    ).copy()

else:
    ranked_areas = eligible_areas.sort_values(
        optimization_options[selected_optimization],
        ascending=False,
    ).copy()

recommended = ranked_areas.iloc[0]

trip_value_pct_vs_median = (
    (recommended["avg_trip_value"] - median_trip_value)
    / median_trip_value
    * 100
)

trip_miles_pct_better = (
    (median_trip_miles - recommended["avg_trip_miles"])
    / median_trip_miles
    * 100
)

trip_minutes_pct_better = (
    (median_trip_minutes - recommended["avg_trip_minutes"])
    / median_trip_minutes
    * 100
)

minutes_direction = (
    "faster"
    if trip_minutes_pct_better >= 0
    else "slower"
)

minutes_icon, minutes_color = get_metric_status(
    trip_minutes_pct_better
)

miles_icon, miles_color = get_metric_status(
    trip_miles_pct_better
)

value_icon, value_color = get_metric_status(
    trip_value_pct_vs_median
)


st.subheader(f"Recommendation for {selected_optimization}")

recommended_demand_rank = int(recommended["demand_rank"])

if selected_optimization == "Best Earnings Opportunity":
    recommended_earnings_rank = int(recommended["earnings_rank"])

total_areas = len(area_summary)

first_third_end = total_areas / 3
second_third_end = 2 * total_areas / 3

if recommended_demand_rank <= first_third_end:
    demand_icon = "🟢"
    demand_label = "Strong pickup demand"
    demand_color = "green"

elif recommended_demand_rank <= second_third_end:
    demand_icon = "🟡"
    demand_label = "Moderate pickup demand"
    demand_color = "orange"

else:
    demand_icon = "🔴"
    demand_label = "Lower pickup demand"
    demand_color = "red"


with st.container(border=True):
    st.markdown(f"### {recommended['area_name']}")

    st.markdown(
    f"{demand_icon} **Pickup demand** — "
    f":{demand_color}[**ranked #{recommended_demand_rank} "
    f"of {total_areas} areas**]"
)

    if selected_optimization == "Quick Trip Turnover":
        st.markdown(
            f"{minutes_icon} **Average trip time** — "
            f"**{recommended['avg_trip_minutes']:.1f} minutes**, "
            f":{minutes_color}[**{abs(trip_minutes_pct_better):.0f}% "
            f"{minutes_direction}** than the median area]"
        )

        miles_direction = (
            "shorter"
            if trip_miles_pct_better >= 0
            else "longer"
        )

        st.markdown(
            f"{miles_icon} **Average trip distance** — "
            f"**{recommended['avg_trip_miles']:.1f} miles**, "
            f":{miles_color}[**{abs(trip_miles_pct_better):.0f}% "
            f"{miles_direction}** than the median area]"
        )

    elif selected_optimization == "Best Earnings Opportunity":
        value_direction = (
            "above"
            if trip_value_pct_vs_median >= 0
            else "below"
        )

        st.markdown(
            f"🟢 **Earnings opportunity** — "
            f":green[**ranked #{recommended_earnings_rank} "
            f"of {total_areas} areas**]"
        )

        st.markdown(
            f"{value_icon} **Average gross trip value** — "
            f"**${recommended['avg_trip_value']:.2f}**, "
            f":{value_color}[**{abs(trip_value_pct_vs_median):.0f}% "
            f"{value_direction} the median area**]"
        )

        st.caption(
            "Earnings Opportunity combines historical pickup demand, "
            "average gross trip value, and average trip duration."
        )


st.subheader(f"Top Recommendations") 

strategy_descriptions = {
    "Staying Busy": "Ranked by historical pickup demand.",
    "Quick Trip Turnover": (
        "Ranked among areas with at least median demand, prioritizing shorter trip times while also accounting for demand."
    ),
    "Best Earnings Opportunity": (
        "Ranked using historical pickup demand, average gross trip value, "
        "and average trip duration."
    ),
}

st.caption(strategy_descriptions[selected_optimization])

rows_to_show = st.segmented_control(
    "Areas to show",
    options=[5, 10],
    default=5,
    format_func=lambda x: f"Top {x}",
)

ranked_df = (
    ranked_areas
    .reset_index(drop=True)
    .copy()
)

ranked_df["Rank"] = ranked_df.index + 1


display_df = (
    ranked_df
    .head(rows_to_show)
    [
        [
            "Rank",
            "area_name",
            "total_trips",
            "avg_trip_value",
            "gross_trip_value_per_hour",
            "avg_trip_miles",
            "avg_trip_minutes",
        ]
    ]
    .rename(
        columns={
            "area_name": "Pickup Area",
            "total_trips": "Trips",
            "avg_trip_value": "Avg Trip Value",
            "gross_trip_value_per_hour": "Gross Value / Trip Hour",
            "avg_trip_miles": "Avg Miles",
            "avg_trip_minutes": "Avg Minutes",
        }
    )
)

highlight_col_map = {
    "Staying Busy": "Trips",
    "Quick Trip Turnover": "Avg Minutes",
    "Best Earnings Opportunity": "Gross Value / Trip Hour",
}
highlight_col = highlight_col_map[selected_optimization]

RANK_CHIP_BG = "rgba(55, 138, 221, 0.22)"
RANK_TEXT_COLOR = "#7FB4EE"


def style_rank_cell(rank):
    if rank <= 3:
        return (
            f"background-color: {RANK_CHIP_BG}; "
            f"color: {RANK_TEXT_COLOR}; "
            "font-weight: 700; "
            "border-radius: 12px; "
            "text-align: center;"
        )
    return "text-align: center;"


# per-column display config, so each metric can be the progress column when active
col_specs = {
    "Trips": {"label": "Trips in Dataset", "fmt": "%d"},
    "Avg Trip Value": {"label": "Avg Gross Trip Value*", "fmt": "$%.2f"},
    "Gross Value / Trip Hour": {"label": "Gross Value / Trip Hour*", "fmt": "$%.2f"},
    "Avg Miles": {"label": "Avg Miles", "fmt": "%.1f"},
    "Avg Minutes": {"label": "Avg Minutes", "fmt": "%.1f"},
}

def format_rank(rank):
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    return medals.get(rank, str(rank))


format_dict = {
    col: ("{:,.0f}" if spec["fmt"] == "%d" else "${:.2f}" if "$" in spec["fmt"] else "{:.1f}")
    for col, spec in col_specs.items()
    if col != highlight_col
}
format_dict["Rank"] = format_rank

styled_df = (
    display_df.style
    .format(format_dict)
    .set_properties(
        subset=["Rank"],
        **{"text-align": "center", "font-size": "16px"},
    )
)

metric_min = float(display_df[highlight_col].min())
metric_max = float(display_df[highlight_col].max())

column_config = {
    "Rank": st.column_config.Column("Rank", width="small"),
}

for col, spec in col_specs.items():
    if col == highlight_col:
        column_config[col] = st.column_config.ProgressColumn(
            spec["label"],
            format=spec["fmt"],
            min_value=metric_min * 0.9,
            max_value=metric_max,
        )
    else:
        column_config[col] = st.column_config.Column(spec["label"])

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True,
    column_config=column_config,
)
st.caption(
    "*Avg Trip Value reflects the total amount charged for the trip "
    "and does not represent the driver's net earnings."
)

st.caption(
    f"Based on {trips_analyzed:,} historical trips recorded for "
    f"{selected_weekday}s from {selected_hour} to the following hour."
)



layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position="[longitude, latitude]",
    get_weight="total_trips",
    radius_pixels=35,
    intensity=1.0,
    threshold=0.08,
    opacity=0.7,
)

view_state = pdk.ViewState(
    latitude=41.90,
    longitude=-87.68,
    zoom=9.8,
    pitch=0
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_provider="carto",
    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
)

st.pydeck_chart(deck, use_container_width=True)

