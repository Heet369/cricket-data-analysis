import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data import get_processed_data, get_batting_agg, get_bowling_agg, get_team_list

st.set_page_config(
    layout="wide",
    page_title="T20 Cricket Analytics",
    page_icon="🏏"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Roboto', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a192f 0%, #0f172a 100%);
    }
    
    .hero-header {
        background: linear-gradient(90deg, #1a2537 0%, #0f172a 100%);
        padding: 20px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-left: 5px solid #ffd700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin: 5px 0 0 0;
    }
    
    .kpi-card {
        background: linear-gradient(145deg, #1a2537 0%, #1e293b 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .pink-highlight {
        color: #ff1493 !important;
    }
    
    .yellow-accent {
        color: #ffd700 !important;
    }
    
    .role-tab {
        background: #1e293b;
        border-radius: 10px;
        padding: 15px 25px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .role-tab:hover {
        background: #2d3748;
    }
    
    .role-tab.active {
        background: linear-gradient(90deg, #ff1493 0%, #ff69b4 100%);
        color: white;
    }
    
    .combined-card {
        background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%);
        border-radius: 12px;
        padding: 20px;
        color: #0a192f;
    }
    
    .combined-card .kpi-value {
        color: #0a192f;
    }
    
    .player-card {
        background: #1a2537;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2d3748;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .player-card:hover {
        border-color: #ff1493;
        box-shadow: 0 0 15px rgba(255, 20, 147, 0.3);
    }
    
    .player-card.selected {
        border-color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    
    .stDataFrame {
        background: #1a2537;
        border-radius: 10px;
    }
    
    div[data-testid="stMetric"] {
        background: #1a2537;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2d3748;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    .stRadio > div {
        background: #1a2537;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stCheckbox > label {
        color: #e2e8f0;
    }
    
    .stMultiSelect > div > div {
        background: #1a2537;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    div[data-testid="stExpander"] {
        background: #1a2537;
        border-radius: 10px;
        border: 1px solid #2d3748;
    }
    
    .stTab {
        background: #1e293b;
    }
    
    .stTab[aria-selected="true"] {
        background: #ff1493;
    }
</style>
""", unsafe_allow_html=True)


def create_kpi_card(value, label, delta=None, highlight=False):
    color_class = "pink-highlight" if highlight else ""
    delta_html = f"<span style='color: #22c55e; font-size: 0.9rem;'>▲ {delta}</span>" if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {color_class}">{value}</div>
        {delta_html}
    </div>
    """


def main():
    _, batting, bowling, players = get_processed_data()
    
    if 'selected_players' not in st.session_state:
        st.session_state.selected_players = []
    if 'current_role' not in st.session_state:
        st.session_state.current_role = "Power Hitters"
    
    with st.sidebar:
        st.markdown("### 🏏 Filters")
        
        teams = get_team_list(batting)
        selected_team = st.selectbox("Select Team", ["All Teams"] + teams)
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        total_matches = batting['match_id'].nunique()
        total_runs = batting['runs'].sum()
        total_wickets = bowling['wickets'].sum()
        st.metric("Total Matches", total_matches)
        st.metric("Total Runs", f"{total_runs:,}")
        st.metric("Total Wickets", total_wickets)
    
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">🏏 ICC Men's T20 World Cup 2022</h1>
        <p class="hero-subtitle">Advanced Analytics Dashboard • Explore player performances, team stats & build your Final XI</p>
    </div>
    """, unsafe_allow_html=True)
    
    roles = ["Power Hitters", "Anchors", "Finishers", "All Rounders", "Fast Bowlers"]
    
    col_role = st.columns([1] * len(roles))
    
    for i, role in enumerate(roles):
        with col_role[i]:
            if st.button(f"{role}", key=f"role_{role}", 
                        use_container_width=True):
                st.session_state.current_role = role
    
    st.markdown("---")
    
    role_tabs = st.tabs(roles)
    
    with role_tabs[0]:
        show_role_section(batting, bowling, players, "Power Hitters", [1, 2])
    with role_tabs[1]:
        show_role_section(batting, bowling, players, "Anchor", [3, 4, 5])
    with role_tabs[2]:
        show_role_section(batting, bowling, players, "Finisher", [6, 7])
    with role_tabs[3]:
        show_allrounder_section(batting, bowling, players)
    with role_tabs[4]:
        show_bowler_section(batting, bowling, players)


def show_role_section(batting, bowling, players, role_name, batting_positions):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 📋 Player Statistics")
        
        role_batting = batting[batting['battingPos'].isin(batting_positions)].copy()
        
        bat_agg = get_batting_agg(role_batting)
        bat_agg = bat_agg.merge(players[['name', 'team', 'battingStyle', 'bowlingStyle', 'playingRole', 'image']], 
                                left_on='batsmanName', right_on='name', how='left')
        
        display_cols = ['batsmanName', 'team', 'innings', 'total_runs', 'batting_avg', 'strike_rate', 'boundary_pct']
        bat_agg_display = bat_agg[display_cols].copy()
        bat_agg_display.columns = ['Name', 'Team', 'Innings', 'Runs', 'Avg', 'SR', 'Boundary %']
        bat_agg_display = bat_agg_display.sort_values('Runs', ascending=False).head(30)
        
        st.dataframe(
            bat_agg_display.style.background_gradient(subset=['SR'], cmap='Reds')
            .background_gradient(subset=['Runs'], cmap='Blues')
            .format({'Avg': '{:.1f}', 'SR': '{:.1f}', 'Boundary %': '{:.1f}%'}),
            use_container_width=True,
            height=400
        )
        
        selected = st.multiselect(
            "👆 Select Player(s) to analyze (click names above)",
            bat_agg['batsmanName'].tolist(),
            default=st.session_state.selected_players if st.session_state.current_role == role_name else []
        )
        st.session_state.selected_players = selected
        
    with col2:
        st.markdown("#### 🎯 Role Info")
        st.info(f"**{role_name}** are players batting in positions {batting_positions[0]}-{batting_positions[-1]}. Click on player names above to see detailed analysis.")


def show_allrounder_section(batting, bowling, players):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 📋 All-Rounder Statistics")
        
        allrounder_names = players[players['playingRole'].str.contains('Allrounder|All-Rounder', case=False, na=False)]['name'].tolist()
        
        role_batting = batting[batting['batsmanName'].isin(allrounder_names)].copy()
        role_bowling = bowling[bowling['bowlerName'].isin(allrounder_names)].copy()
        
        bat_agg = get_batting_agg(role_batting)
        bowl_agg = get_bowling_agg(role_bowling)
        
        combined = bat_agg.merge(bowl_agg, on='batsmanName', how='outer')
        combined = combined.fillna(0)
        combined['total_value'] = combined['runs'] + combined['wickets'] * 25
        combined = combined.sort_values('total_value', ascending=False)
        
        combined = combined.merge(players[['name', 'team', 'battingStyle', 'bowlingStyle', 'playingRole']], 
                                left_on='batsmanName', right_on='name', how='left')
        
        display_cols = ['batsmanName', 'team', 'innings', 'total_runs', 'batting_avg', 'strike_rate', 'wickets', 'economy']
        comb_display = combined[display_cols].copy()
        comb_display.columns = ['Name', 'Team', 'Innings', 'Runs', 'Avg', 'SR', 'Wkts', 'Econ']
        comb_display = comb_display.head(25)
        
        st.dataframe(
            comb_display.style.background_gradient(subset=['SR'], cmap='Reds')
            .background_gradient(subset=['Runs', 'Wkts'], cmap='Blues')
            .format({'Avg': '{:.1f}', 'SR': '{:.1f}', 'Econ': '{:.2f}'}),
            use_container_width=True,
            height=400
        )
        
        selected = st.multiselect(
            "👆 Select All-Rounder(s) to analyze",
            combined['batsmanName'].tolist(),
            default=st.session_state.selected_players if st.session_state.current_role == "All Rounders" else []
        )
        st.session_state.selected_players = selected
        
    with col2:
        st.markdown("#### 🎯 Role Info")
        st.info("**All-Rounders** contribute with both bat and ball. Sorted by total value (runs + wickets×25).")


def show_bowler_section(batting, bowling, players):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 📋 Fast Bowler Statistics")
        
        bowler_agg = get_bowling_agg(bowling)
        bowler_agg = bowler_agg.merge(players[['name', 'team', 'bowlingStyle', 'playingRole']], 
                                      left_on='bowlerName', right_on='name', how='left')
        
        bowler_agg = bowler_agg[bowler_agg['wickets'] >= 5].sort_values('wickets', ascending=False)
        
        display_cols = ['bowlerName', 'team', 'matches', 'overs', 'wickets', 'bowling_avg', 'economy']
        bowl_display = bowler_agg[display_cols].copy()
        bowl_display.columns = ['Name', 'Team', 'Matches', 'Overs', 'Wkts', 'Avg', 'Econ']
        
        st.dataframe(
            bowl_display.style.background_gradient(subset=['Wkts'], cmap='Reds')
            .background_gradient(subset=['Econ'], cmap='Greens')
            .format({'Avg': '{:.1f}', 'Econ': '{:.2f}'}),
            use_container_width=True,
            height=400
        )
        
        selected = st.multiselect(
            "👆 Select Bowler(s) to analyze",
            bowler_agg['bowlerName'].tolist(),
            default=st.session_state.selected_players if st.session_state.current_role == "Fast Bowlers" else []
        )
        st.session_state.selected_players = selected
        
    with col2:
        st.markdown("#### 🎯 Role Info")
        st.info("**Fast Bowlers** sorted by wickets taken (min 5 wickets). Lower economy is better.")


if __name__ == "__main__":
    main()
