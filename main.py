import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

# --- CONFIG & CONSTANTS ---
st.set_page_config(page_title="Whisky Auction Data Explorer", layout="wide")
DB_PATH = "whisky_data.db"


class WhiskyDataEngine:
    """Handles logic for database-centric data retrieval."""

    @staticmethod
    def get_all_distilleries():
        """Reads master list from local SQLite."""
        conn = sqlite3.connect(DB_PATH)
        df = pl.read_database("SELECT * FROM master_distilleries", conn)
        conn.close()
        return df

    @staticmethod
    def get_distillery_metrics(slug):
        """Targeted SQL query for specific distillery deep-dive."""
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT * FROM distillery_stats WHERE distillery_slug = '{slug}'"
        df = pl.read_database(query, conn)
        conn.close()

        if not df.is_empty():
            return df.with_columns(
                pl.col("dt").str.to_date("%Y-%m-%d").alias("Timestamp")
            )
        return pl.DataFrame()

    @staticmethod
    def get_market_rankings():
        """Calculates top performers from the entire local dataset."""
        conn = sqlite3.connect(DB_PATH)
        df = pl.read_database("SELECT * FROM distillery_stats", conn)
        conn.close()
        return df


class AnalyticsUI:
    """Handles the rendering of the Distillery Dashboard."""

    @staticmethod
    def render_sidebar():
        with st.sidebar:
            st.header("🛡️ Data Governance")
            st.markdown("""
            **Environment:** Production Prototype  
            **Architecture:** SQLite Persistence  
            **Strategy:** API Decoupling  
            """)
            st.divider()
            st.status("Database: Connected", state="complete")
            st.status("Engine: Polars 1.0", state="complete")
            st.info("Commercial Insights Hub v2.1")

    @staticmethod
    def render_top_lists(df):
        st.header("🏆 Market Leaders (Top 10)")

        # Aggregation Logic
        top_volume = (
            df.group_by("distillery_slug")
            .agg(
                (pl.col("trading_volume").sum() / 1000000).alias(
                    "Total Volume Millions"
                )
            )
            .rename({"distillery_slug": "Distillery"})
            .sort("Total Volume Millions", descending=True)
            .head(10)
        )
        tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt
        top_revenue = (
            df.group_by("distillery_slug")
            .agg(
                [
                    (pl.col("winning_bid_max").max()).alias("Price (£)"),
                ]
            )
            .rename({"distillery_slug": "Distillery"})
            .sort("Price (£)", descending=True)
            .head(10)
        )

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Market Share by Volume")
            fig_vol = px.bar(
                top_volume.to_pandas(),
                x="Distillery",
                y="Total Volume Millions",
                template="plotly_white",
                color_discrete_sequence=["#D4AF37"],
            )
            fig_vol.update_layout(xaxis={"categoryorder": "total descending"})
            st.plotly_chart(fig_vol, use_container_width=True)

        with c2:
            st.subheader("Highest Recorded Hammer Prices")
            fig_price = px.bar(
                top_revenue.to_pandas(),
                x="Distillery",
                y="Price (£)",
                template="plotly_white",
                color_discrete_sequence=["#8c510a"],
            )
            fig_price.update_layout(xaxis={"categoryorder": "total descending"})
            st.plotly_chart(fig_price, use_container_width=True)

    @staticmethod
    def render_deep_dive(df, name):
        st.header(f"🔍 Brand Performance Audit: {name}")

        # Professional Summary Stats
        latest = df.row(-1, named=True)
        s1, s2, s3 = st.columns(3)
        s1.metric("Avg Bid", f"£{latest['winning_bid_mean']:.2f}")
        s2.metric("Peak Record", f"£{df['winning_bid_max'].max():.2f}")
        s3.metric("Monthly Vol", f"£{latest['trading_volume']:,.0f}")

        st.divider()

        # Row 1: Price and Liquidity
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Price Momentum (Mean)")
            fig_mean = px.line(
                df.to_pandas(),
                x="Timestamp",
                y="winning_bid_mean",
                template="plotly_white",
            )
            fig_mean.update_traces(line_color="#D4AF37")
            st.plotly_chart(fig_mean, use_container_width=True)
        with c2:
            st.subheader("Auction Velocity (Lots)")
            fig_lots = px.bar(
                df.to_pandas(), x="Timestamp", y="lots_count", template="plotly_white"
            )
            fig_lots.update_traces(marker_color="#8c510a")
            st.plotly_chart(fig_lots, use_container_width=True)

        # Row 2: Range Comparison (Professional Area Chart)
        st.subheader("Market Spread Analysis (Floor vs. Ceiling)")
        df_pd = df.to_pandas()

        fig_spread = go.Figure()
        # Max Price
        fig_spread.add_trace(
            go.Scatter(
                x=df_pd["Timestamp"],
                y=df_pd["winning_bid_max"],
                name="Market Ceiling",
                line=dict(color="#D4AF37", width=1),
            )
        )
        # Min Price with Shaded Area
        fig_spread.add_trace(
            go.Scatter(
                x=df_pd["Timestamp"],
                y=df_pd["winning_bid_min"],
                name="Market Floor",
                fill="tonexty",
                line=dict(color="#8c510a", width=1),
            )
        )

        fig_spread.update_layout(
            template="plotly_white",
            hovermode="x unified",
            yaxis_title="Price (£)",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )
        st.plotly_chart(fig_spread, use_container_width=True)


def main():
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
