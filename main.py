import streamlit as st
from db.init_db import init_db
from db.whisky_data_engine import WhiskyDataEngine
from ui.analytics_ui import AnalyticsUI

# --- CONFIG & CONSTANTS ---
st.set_page_config(page_title="Whisky Auction Data Explorer", layout="wide")


def main():
    init_db()
    ui = AnalyticsUI()
    engine = WhiskyDataEngine()

    ui.render_sidebar()
    st.title("🥃 Whisky Auction Data Explorer")

    try:
        full_market_df = engine.get_market_rankings()

        # TABBED NAVIGATION (Professional Layout)
        tab_market, tab_deepdive, tab_data = st.tabs(
            ["🌎 Market Overview", "🔍 Distillery Deep-Dive", "📋 Raw Data Audit"]
        )

        with tab_market:
            ui.render_top_lists(full_market_df)

        with tab_deepdive:
            all_dist = engine.get_all_distilleries()
            slug_list = all_dist["slug"].to_list()

            # Distillery Selection inside the tab
            col_search, _ = st.columns([1, 2])
            with col_search:
                selected_slug = st.selectbox(
                    "Select Distillery for Analysis", options=slug_list
                )

            if selected_slug:
                dist_data = engine.get_distillery_metrics(selected_slug)
                if not dist_data.is_empty():
                    ui.render_deep_dive(
                        dist_data, selected_slug.replace("-", " ").title()
                    )
                else:
                    st.warning("No time-series data found for this selection.")

        with tab_data:
            st.subheader("Complete Data Export")
            st.dataframe(full_market_df.to_pandas(), use_container_width=True)

    except Exception as e:
        st.error(f"System Error: {e}")


if __name__ == "__main__":
    main()
