import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.data import get_processed_data, get_batting_agg, get_bowling_agg

st.set_page_config(layout="wide", page_title="Final 11 - T20 Analytics", page_icon="🏏")

st.markdown("""
<style>
    .hero-header {
        background: linear-gradient(90deg, #1a2537 0%, #0f172a 100%);
        padding: 20px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-left: 5px solid #ffd700;
    }
    .kpi-card {
        background: linear-gradient(145deg, #1a2537 0%, #1e293b 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3748;
    }
    .player-card {
        background: #1a2537;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2d3748;
    }
    .player-card.selected {
        border-color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    .final-card {
        background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%);
        border-radius: 12px;
        padding: 20px;
        color: #0a192f;
    }
    h1, h2, h3 { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)


def main():
    _, batting, bowling, players = get_processed_data()
    
    if 'final_11' not in st.session_state:
        st.session_state.final_11 = []
    
    st.markdown("""
    <div class="hero-header">
        <h1>🏆 Build Your Final XI</h1>
        <p style="color: #94a3b8;">Select 11 players to create your dream team</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_list, col_team = st.columns([2, 1])
    
    with col_list:
        st.markdown("### 👥 Available Players")
        
        player_list = players[['name', 'team', 'playingRole', 'battingStyle', 'bowlingStyle']].dropna(subset=['name'])
        player_list = player_list.drop_duplicates(subset=['name'])
        
        search = st.text_input("🔍 Search players", "")
        
        if search:
            player_list = player_list[player_list['name'].str.contains(search, case=False)]
        
        role_filter = st.selectbox("Filter by Role", ["All", "Batter", "Bowler", "Allrounder", "Wicketkeeper"])
        
        if role_filter != "All":
            player_list = player_list[player_list['playingRole'].str.contains(role_filter, case=False, na=False)]
        
        for _, row in player_list.head(30).iterrows():
            is_selected = row['name'] in st.session_state.final_11
            card_class = "player-card selected" if is_selected else "player-card"
            
            with st.container():
                st.markdown(f"""
                <div class="{card_class}" style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: white;">{row['name']}</strong><br>
                        <span style="color: #94a3b8; font-size: 0.85rem;">{row['team']} • {row['playingRole']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"{'✅' if is_selected else '➕'} {row['name']}", key=f"add_{row['name']}"):
                    if is_selected:
                        st.session_state.final_11.remove(row['name'])
                    else:
                        if len(st.session_state.final_11) < 11:
                            st.session_state.final_11.append(row['name'])
                        else:
                            st.warning("Maximum 11 players allowed!")
                    st.rerun()
    
    with col_team:
        st.markdown("### 📋 Your Team")
        st.metric("Players Selected", f"{len(st.session_state.final_11)}/11")
        
        if st.button("Clear All", type="primary"):
            st.session_state.final_11 = []
            st.rerun()
        
        if st.session_state.final_11:
            st.write("**Selected Players:**")
            for i, p in enumerate(st.session_state.final_11, 1):
                st.write(f"{i}. {p}")
            
            with st.expander("📊 Team Statistics"):
                final_batting = batting[batting['batsmanName'].isin(st.session_state.final_11)]
                final_bowling = bowling[bowling['bowlerName'].isin(st.session_state.final_11)]
                
                if len(final_batting) > 0:
                    bat_agg = get_batting_agg(final_batting)
                    st.metric("Team Runs", bat_agg['total_runs'].sum())
                    st.metric("Team SR", f"{bat_agg['strike_rate'].mean():.1f}")
                
                if len(final_bowling) > 0:
                    bowl_agg = get_bowling_agg(final_bowling)
                    st.metric("Team Wickets", bowl_agg['wickets'].sum())
                    st.metric("Team Economy", f"{bowl_agg['economy'].mean():.2f}")
        else:
            st.info("Select players from the list")


if __name__ == "__main__":
    main()
