import streamlit as st
import polars as pl
import pandas as pd
import plotly.express as px
from whisky_api import distilleries_info, distillery_data

# --- CONFIG & CONSTANTS ---
st.set_page_config(page_title="ASC Distillery Intelligence", layout="wide")

class WhiskyDataEngine:
    """Handles logic for distillery-centric data ingestion and metric engineering."""
    
    @staticmethod
    @st.cache_data
    def get_all_distilleries():
        return distilleries_info()

    @staticmethod
    @st.cache_data
    def get_distillery_metrics(slug):
        """Fetches time-series data for a specific distillery."""
        try:
            df = distillery_data(slug)
            if not df.is_empty():
                # Matching your JSON: dt, winning_bid_mean, trading_volume, lots_count
                return df.with_columns(pl.col("dt").str.to_date("%Y-%m-%d"))
        except Exception:
            return pl.DataFrame()
        return pl.DataFrame()

class AnalyticsUI:
    """Handles the rendering of the Distillery Dashboard."""
    
    @staticmethod
    def render_sidebar():
        st.sidebar.header("🛡️ Data Governance")
        st.sidebar.markdown("**Lead Role Prototype**\n**Focus:** Brand Performance\n**Engine:** Polars / Plotly")
        st.sidebar.success("Direct API Integration: Active")

    @staticmethod
    def render_market_overview(all_dist_df):
        st.header("🏆 Market Overview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distillery Index")
            st.markdown("Global footprint of distilleries currently tracked in the secondary market.")
            st.dataframe(all_dist_df.select(["name", "country", "slug"]).head(10), use_container_width=True)
            
        with col2:
            st.subheader("Market Momentum Insights")
            st.info("Selection-driven deep dives allow for precise ROI and Volatility analysis across the portfolio.")
            st.write("Use the selector below to perform a technical audit of specific distillery assets.")

    @staticmethod
    def render_deep_dive(df, name):
        st.header(f"🔍 Deep Dive Analysis: {name}")
        
        # Row 1: Price and Volume
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Mean Price Evolution (£)")
            fig1 = px.line(df.to_pandas(), x="dt", y="winning_bid_mean", 
                          line_shape="spline", render_mode="svg", color_discrete_sequence=['#D4AF37'])
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            st.subheader("Market Liquidity: Monthly Lots")
            # Using corrected 'lots_count'
            fig2 = px.bar(df.to_pandas(), x="dt", y="lots_count", color_discrete_sequence=['#8c510a'])
            st.plotly_chart(fig2, use_container_width=True)

        # Row 2: Value Spread and Trading Volume
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Value Spread (Min vs Max)")
            fig3 = px.area(df.to_pandas(), x="dt", y=["winning_bid_min", "winning_bid_max"], 
                           title="Price Range Variance", color_discrete_map={"winning_bid_max": "#C0C0C0", "winning_bid_min": "#8c510a"})
            st.plotly_chart(fig3, use_container_width=True)
            
        with c4:
            st.subheader("Total Trading Volume (£)")
            # Using corrected 'trading_volume'
            fig4 = px.scatter(df.to_pandas(), x="dt", y="trading_volume", size="lots_count",
                              color="winning_bid_mean", color_continuous_scale='Oryel')
            st.plotly_chart(fig4, use_container_width=True)

def main():
    ui = AnalyticsUI()
    engine = WhiskyDataEngine()
    
    ui.render_sidebar()
    st.title("🥃 ASC Distillery Intelligence Portal")

    try:
        # Part 1: Market Level
        all_dist = engine.get_all_distilleries()
        ui.render_market_overview(all_dist)
        
        st.divider()

        # Part 2: Custom Deep Dive
        st.header("Distillery Analysis Tool")
        
        # Searchable selectbox
        slug_list = all_dist["slug"].to_list()
        selected_slug = st.selectbox("Search & Select Distillery", 
                                    options=slug_list,
                                    index=slug_list.index("macallan") if "macallan" in slug_list else 0)
        
        if selected_slug:
            dist_data = engine.get_distillery_metrics(selected_slug)
            
            if not dist_data.is_empty():
                # Summary Stats - using the updated column names
                latest = dist_data.row(-1, named=True)
                s1, s2, s3, s4 = st.columns(4)
                
                s1.metric("Current Mean Bid", f"£{latest['winning_bid_mean']:.2f}")
                s2.metric("Peak Historical Price", f"£{dist_data['winning_bid_max'].max():.2f}")
                s3.metric("Latest Trading Vol", f"£{latest['trading_volume']:,.0f}")
                s4.metric("Market Liquidity", f"{int(latest['lots_count'])} Lots")
                
                ui.render_deep_dive(dist_data, selected_slug.replace("-", " ").title())
            else:
                st.warning(f"No specific time-series data returned for {selected_slug}. It may have limited auction history.")

    except Exception as e:
        st.error(f"Analysis Error: {e}")

if __name__ == "__main__":
    main()