import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data import get_processed_data, get_batting_agg, get_bowling_agg, get_team_list
from utils.visuals import plot_performance_over_opponents, plot_avg_vs_sr_scatter, get_combined_stats, plot_progress_bar

st.set_page_config(
    layout="wide",
    page_title="T20 Cricket Analytics",
    page_icon="🏏"
)

# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS — Stadium Nights × Neon Scoreboard aesthetic
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Root tokens ── */
:root {
    --pitch: #0b1120;
    --grass: #0d1f1a;
    --floodlight: #f5c518;
    --floodlight-dim: rgba(245,197,24,0.15);
    --neon-pink: #ff2d78;
    --neon-cyan: #00e5ff;
    --neon-green: #39ff14;
    --slate: #1c2840;
    --slate-border: #2a3a58;
    --text-primary: #f0f4ff;
    --text-muted: #6b7fa3;
    --glass: rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.08);
}

/* ── Global reset ── */
html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: var(--pitch) !important;
    color: var(--text-primary);
}

/* ── Animated stadium pitch background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 50% -10%, rgba(245,197,24,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 40% 40% at 10% 90%, rgba(0,229,255,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 90% 80%, rgba(255,45,120,0.05) 0%, transparent 60%),
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(255,255,255,0.018) 39px, rgba(255,255,255,0.018) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(255,255,255,0.012) 39px, rgba(255,255,255,0.012) 40px);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1829 0%, #0b1120 100%) !important;
    border-right: 1px solid var(--slate-border);
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Scoreboard hero ── */
.scoreboard-hero {
    position: relative;
    background: linear-gradient(135deg, #0d1829 0%, #111d35 60%, #0b1120 100%);
    border: 1px solid var(--slate-border);
    border-top: 3px solid var(--floodlight);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 32px;
    overflow: hidden;
}
.scoreboard-hero::before {
    content: '🏏';
    position: absolute;
    right: -20px;
    top: -20px;
    font-size: 160px;
    opacity: 0.04;
    transform: rotate(-20deg);
}
.scoreboard-hero::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--floodlight), var(--neon-pink), var(--neon-cyan), transparent);
    animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline {
    0%, 100% { opacity: 0.4; transform: scaleX(0.6); }
    50%       { opacity: 1;   transform: scaleX(1); }
}

.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    color: var(--floodlight);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.6rem;
    letter-spacing: 0.05em;
    line-height: 1;
    color: #ffffff;
    margin: 0 0 6px 0;
}
.hero-title span { color: var(--floodlight); }
.hero-subtitle {
    font-size: 0.95rem;
    color: var(--text-muted);
    margin: 0;
}

/* ── Live badge ── */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,45,120,0.15);
    border: 1px solid rgba(255,45,120,0.4);
    border-radius: 999px;
    padding: 4px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--neon-pink);
    letter-spacing: 0.1em;
    margin-bottom: 16px;
}
.live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--neon-pink);
    animation: pulse-dot 1.4s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.3; transform: scale(0.6); }
}

/* ── KPI ticker strip ── */
.ticker-strip {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 28px;
}
.ticker-card {
    flex: 1;
    min-width: 140px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 18px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.ticker-card:hover {
    border-color: var(--floodlight);
    transform: translateY(-3px);
}
.ticker-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 3px 0 0 3px;
}
.ticker-card.gold::before  { background: var(--floodlight); }
.ticker-card.pink::before  { background: var(--neon-pink); }
.ticker-card.cyan::before  { background: var(--neon-cyan); }
.ticker-card.green::before { background: var(--neon-green); }

.ticker-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 6px;
}
.ticker-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    letter-spacing: 0.04em;
    line-height: 1;
    color: #fff;
}
.ticker-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 2px;
}

/* ── Role selector pills ── */
.role-pill-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 24px; }
.role-pill {
    cursor: pointer;
    border: 1px solid var(--slate-border);
    border-radius: 999px;
    padding: 8px 20px;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-muted);
    background: var(--glass);
    transition: all 0.2s;
}
.role-pill:hover, .role-pill.active {
    background: var(--floodlight-dim);
    border-color: var(--floodlight);
    color: var(--floodlight);
}

/* ── Streamlit button overrides — role tabs ── */
div[data-testid="stHorizontalBlock"] > div > div > div > button {
    background: var(--glass) !important;
    border: 1px solid var(--slate-border) !important;
    border-radius: 999px !important;
    color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
div[data-testid="stHorizontalBlock"] > div > div > div > button:hover {
    border-color: var(--floodlight) !important;
    color: var(--floodlight) !important;
    background: var(--floodlight-dim) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 4px;
    border-bottom: 1px solid var(--slate-border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    padding: 10px 18px !important;
    border: none !important;
    transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
    color: var(--floodlight) !important;
    border-bottom: 2px solid var(--floodlight) !important;
    background: var(--floodlight-dim) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 20px !important;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 0.08em;
    color: #fff;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-heading .accent { color: var(--floodlight); }

/* ── Data table wrapper ── */
div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid var(--slate-border) !important;
}
div[data-testid="stDataFrame"] table {
    background: #0f1927 !important;
}
div[data-testid="stDataFrame"] thead tr th {
    background: #131e30 !important;
    color: var(--floodlight) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--slate-border) !important;
}
div[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(245,197,24,0.06) !important;
}

/* ── Multiselect ── */
div[data-baseweb="select"] {
    background: var(--slate) !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] * { color: var(--text-primary) !important; }

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 14px !important;
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.75rem !important; }
div[data-testid="stMetricValue"] { color: #fff !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 1.8rem !important; }

/* ── Combined player card ── */
.combined-card {
    background: linear-gradient(135deg, #f5c518 0%, #e5a800 100%);
    border-radius: 16px;
    padding: 24px 28px;
    color: #0b1120;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.combined-card::after {
    content: '★';
    position: absolute;
    right: 20px; top: 10px;
    font-size: 80px;
    opacity: 0.1;
}
.combined-card h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.06em;
    color: #0b1120 !important;
    margin: 0 0 14px 0;
}
.combined-stats { display: flex; gap: 24px; flex-wrap: wrap; }
.combined-stat { }
.combined-stat .val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    line-height: 1;
    color: #0b1120;
}
.combined-stat .lbl {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(11,17,32,0.6);
}

/* ── Role info card ── */
.role-info-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-left: 3px solid var(--floodlight);
    border-radius: 12px;
    padding: 20px;
}
.role-info-card p { color: var(--text-muted) !important; font-size: 0.88rem; line-height: 1.6; }
.role-info-card strong { color: var(--floodlight) !important; }

/* ── Divider ── */
hr { border-color: var(--slate-border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--pitch); }
::-webkit-scrollbar-thumb { background: var(--slate-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--floodlight); }

/* ── Stagger animation for cards on load ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.ticker-card { animation: fadeUp 0.5s ease both; }
.ticker-card:nth-child(1) { animation-delay: 0.05s; }
.ticker-card:nth-child(2) { animation-delay: 0.12s; }
.ticker-card:nth-child(3) { animation-delay: 0.19s; }
.ticker-card:nth-child(4) { animation-delay: 0.26s; }

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly, .plot-container { background: transparent !important; }

/* Hide default Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PLAYER DETAILS PANEL
# ─────────────────────────────────────────────────────────────────────────────
def show_player_details(player_names, batting, bowling, players):
    if not player_names:
        return

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Combined card (multi-select) ──────────────────────────────────────
    if len(player_names) > 1:
        from utils.visuals import get_combined_stats
        combined = get_combined_stats(batting, player_names)
        if combined:
            st.markdown(f"""
            <div class="combined-card">
                <h3>🏆 Combined Performance &nbsp;·&nbsp; {len(player_names)} Players</h3>
                <div class="combined-stats">
                    <div class="combined-stat"><div class="val">{combined['matches']}</div><div class="lbl">Matches</div></div>
                    <div class="combined-stat"><div class="val">{combined['total_runs']}</div><div class="lbl">Total Runs</div></div>
                    <div class="combined-stat"><div class="val">{combined['avg']:.1f}</div><div class="lbl">Bat Avg</div></div>
                    <div class="combined-stat"><div class="val">{combined['sr']:.1f}</div><div class="lbl">Strike Rate</div></div>
                    <div class="combined-stat"><div class="val">{combined['boundary_pct']:.1f}%</div><div class="lbl">Boundary %</div></div>
                    <div class="combined-stat"><div class="val">{combined['avg_balls_faced']:.1f}</div><div class="lbl">Balls/Inn</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────
    if len(player_names) > 0:
        from utils.visuals import plot_performance_over_opponents, plot_avg_vs_sr_scatter
        fig_line = plot_performance_over_opponents(batting, player_names, metric='avg')
        if fig_line:
            fig_line.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#6b7fa3',
                title_font_color='#f0f4ff',
            )
            st.plotly_chart(fig_line, use_container_width=True)

        fig_scatter = plot_avg_vs_sr_scatter(batting, player_names)
        if fig_scatter:
            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15,25,39,0.6)',
                font_color='#6b7fa3',
                title_font_color='#f0f4ff',
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Individual cards ──────────────────────────────────────────────────
    st.markdown('<div class="section-heading">📊 <span class="accent">Individual</span> Player Details</div>', unsafe_allow_html=True)

    for player in player_names:
        player_bat  = batting[batting['batsmanName'] == player]
        player_bowl = bowling[bowling['bowlerName'] == player]
        player_info = players[players['name'] == player].iloc[0] if len(players[players['name'] == player]) > 0 else None

        role_icon = '🎯' if len(player_bowl) > 0 and len(player_bat) > 0 else '🏏' if len(player_bat) > 0 else '🎳'

        with st.expander(f"{role_icon}  {player}", expanded=True):
            col1, col2, col3 = st.columns([1, 2, 2])

            with col1:
                st.markdown("**👤 Player Info**")
                if player_info is not None:
                    st.write(f"**Team:** {player_info.get('team', 'N/A')}")
                    st.write(f"**Role:** {player_info.get('playingRole', 'N/A')}")
                    st.write(f"**Batting:** {player_info.get('battingStyle', 'N/A')}")
                    st.write(f"**Bowling:** {player_info.get('bowlingStyle', 'N/A')}")
                else:
                    st.write("No info available")

            with col2:
                st.markdown("**🏏 Batting Stats**")
                if len(player_bat) > 0:
                    bat_agg = get_batting_agg(player_bat)
                    if len(bat_agg) > 0:
                        row = bat_agg.iloc[0]
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Runs", int(row['total_runs']))
                        c2.metric("Avg",  f"{row['batting_avg']:.1f}")
                        c3.metric("SR",   f"{row['strike_rate']:.1f}")
                        c4.metric("4s/6s", f"{int(row['fours'])}/{int(row['sixes'])}")
                else:
                    st.info("No batting data")

            with col3:
                st.markdown("**🎳 Bowling Stats**")
                if len(player_bowl) > 0:
                    bowl_agg = get_bowling_agg(player_bowl)
                    if len(bowl_agg) > 0:
                        row = bowl_agg.iloc[0]
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Wickets", int(row['wickets']))
                        c2.metric("Overs",   f"{row['overs']:.1f}")
                        c3.metric("Econ",    f"{row['avg_economy']:.2f}")
                        c4.metric("Avg",     f"{row['bowling_avg']:.1f}")
                else:
                    st.info("No bowling data")

            if len(player_bat) > 0:
                st.markdown("**📈 Performance by Match**")
                match_stats = player_bat[['match_id','runs','balls','SR','opponent','matchDate']].sort_values('match_id')
                match_stats = match_stats.fillna('')
                st.dataframe(match_stats, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    _, batting, bowling, players = get_processed_data()

    if 'selected_players' not in st.session_state:
        st.session_state.selected_players = []
    if 'current_role' not in st.session_state:
        st.session_state.current_role = "Power Hitters"

    # ── Sidebar ──────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 20px 0;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#f5c518;letter-spacing:.06em;">T20 ANALYTICS</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#6b7fa3;letter-spacing:.2em;">ICC WORLD CUP 2022</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7rem;letter-spacing:.18em;color:#6b7fa3;text-transform:uppercase;margin-bottom:8px;">Filters</div>', unsafe_allow_html=True)
        teams = get_team_list(batting)
        selected_team = st.selectbox("Team", ["All Teams"] + teams)

        st.markdown("---")
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7rem;letter-spacing:.18em;color:#6b7fa3;text-transform:uppercase;margin-bottom:12px;">Tournament Stats</div>', unsafe_allow_html=True)

        total_matches  = int(batting['match_id'].nunique())
        total_runs     = int(batting['runs'].sum())
        total_wickets  = int(bowling['wickets'].sum())

        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:12px;">
            <div style="background:rgba(245,197,24,0.08);border:1px solid rgba(245,197,24,0.2);border-radius:10px;padding:14px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:.18em;color:#6b7fa3;text-transform:uppercase;">Matches</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#f5c518;">{total_matches}</div>
            </div>
            <div style="background:rgba(255,45,120,0.08);border:1px solid rgba(255,45,120,0.2);border-radius:10px;padding:14px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:.18em;color:#6b7fa3;text-transform:uppercase;">Total Runs</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#ff2d78;">{total_runs:,}</div>
            </div>
            <div style="background:rgba(0,229,255,0.06);border:1px solid rgba(0,229,255,0.15);border-radius:10px;padding:14px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:.18em;color:#6b7fa3;text-transform:uppercase;">Wickets</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#00e5ff;">{total_wickets}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.page_link("pages/final_11.py", label="🏆 Build Your Final XI", use_container_width=True)

    # ── Hero scoreboard ───────────────────────────────────────────────────
    st.markdown("""
    <div class="scoreboard-hero">
        <div class="live-badge"><span class="live-dot"></span>LIVE ANALYTICS</div>
        <div class="hero-title">ICC Men's T20 <span>World Cup</span></div>
        <div class="hero-title" style="font-size:2.2rem;color:#6b7fa3;margin-top:4px;">AUSTRALIA 2022</div>
        <p class="hero-subtitle" style="margin-top:12px;">Explore player performances · Compare strategies · Build your dream XI</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ticker ────────────────────────────────────────────────────────
    # Convert SR and economy to numeric for calculations
    batting_sr = pd.to_numeric(batting['SR'], errors='coerce')
    bowling_econ = pd.to_numeric(bowling['economy'], errors='coerce')
    
    top_scorer_row  = get_batting_agg(batting).sort_values('total_runs', ascending=False).iloc[0] if len(batting) > 0 else None
    top_wicket_row  = get_bowling_agg(bowling).sort_values('wickets', ascending=False).iloc[0]    if len(bowling) > 0 else None
    avg_sr          = f"{batting_sr.mean():.1f}"  if batting_sr.notna().sum() > 0 else "—"
    avg_econ        = f"{bowling_econ.mean():.2f}" if bowling_econ.notna().sum() > 0 else "—"

    ts_name = top_scorer_row['batsmanName'] if top_scorer_row is not None else "—"
    ts_runs = int(top_scorer_row['total_runs']) if top_scorer_row is not None else 0
    tw_name = top_wicket_row['bowlerName'] if top_wicket_row is not None else "—"
    tw_wkts = int(top_wicket_row['wickets']) if top_wicket_row is not None else 0

    st.markdown(f"""
    <div class="ticker-strip">
        <div class="ticker-card gold">
            <div class="ticker-label">Top Scorer</div>
            <div class="ticker-value">{ts_runs}</div>
            <div class="ticker-sub">{ts_name}</div>
        </div>
        <div class="ticker-card pink">
            <div class="ticker-label">Top Wickets</div>
            <div class="ticker-value">{tw_wkts}</div>
            <div class="ticker-sub">{tw_name}</div>
        </div>
        <div class="ticker-card cyan">
            <div class="ticker-label">Avg Strike Rate</div>
            <div class="ticker-value">{avg_sr}</div>
            <div class="ticker-sub">Tournament-wide</div>
        </div>
        <div class="ticker-card green">
            <div class="ticker-label">Avg Economy</div>
            <div class="ticker-value">{avg_econ}</div>
            <div class="ticker-sub">Tournament-wide</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Role tabs ─────────────────────────────────────────────────────────
    roles     = ["Power Hitters", "Anchors", "Finishers", "All Rounders", "Fast Bowlers"]
    role_icons = ["⚡", "⚓", "🎯", "🔄", "🔥"]

    role_tabs = st.tabs([f"{icon} {role}" for icon, role in zip(role_icons, roles)])

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


# ─────────────────────────────────────────────────────────────────────────────
# ROLE SECTIONS
# ─────────────────────────────────────────────────────────────────────────────
ROLE_DESCRIPTIONS = {
    "Power Hitters": ("⚡ Power Hitters", "Positions 1–2", "Explosive openers who set the tone. Look for high Strike Rate (>140) and Boundary % above 60% to identify the true destroyers."),
    "Anchor":        ("⚓ Anchors",        "Positions 3–5", "The backbone of the innings. Prioritise Batting Average (>35) — these players hold the team together when wickets fall."),
    "Finisher":      ("🎯 Finishers",      "Positions 6–7", "Death-over specialists. Elite finishers combine a Strike Rate >130 with nerves of steel in the last 5 overs."),
    "All Rounders":  ("🔄 All-Rounders",   "Ranked by Value", "Double the impact. Ranked by composite value (Runs + Wickets × 25). The best XIs are built around elite all-rounders."),
    "Fast Bowlers":  ("🔥 Fast Bowlers",   "Min 5 Wickets", "The strike force. Lower economy wins matches. Focus on Avg < 20 and Economy < 7.5 for world-class pacers."),
}

def _role_info_html(role_key):
    title, positions, desc = ROLE_DESCRIPTIONS.get(role_key, ("", "", ""))
    return f"""
    <div class="role-info-card">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;letter-spacing:.06em;color:#f5c518;margin-bottom:4px;">{title}</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#6b7fa3;letter-spacing:.12em;margin-bottom:10px;">{positions}</div>
        <p>{desc}</p>
    </div>
    """


def show_role_section(batting, bowling, players, role_name, batting_positions):
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f'<div class="section-heading">📋 <span class="accent">Player</span> Statistics</div>', unsafe_allow_html=True)

        role_batting = batting[batting['battingPos'].isin(batting_positions)].copy()
        bat_agg = get_batting_agg(role_batting)
        bat_agg = bat_agg.merge(
            players[['name','team','battingStyle','bowlingStyle','playingRole','image']],
            left_on='batsmanName', right_on='name', how='left'
        )

        display_cols = ['batsmanName','team','innings','total_runs','batting_avg','strike_rate','boundary_pct']
        bat_agg_display = bat_agg[display_cols].copy()
        bat_agg_display.columns = ['Name','Team','Innings','Runs','Avg','SR','Boundary %']
        bat_agg_display = bat_agg_display.sort_values('Runs', ascending=False).head(30)

        max_runs = float(bat_agg_display['Runs'].max()) if bat_agg_display['Runs'].max() > 0 else 1
        max_sr   = 200.0
        max_avg  = float(bat_agg_display['Avg'].max())  if bat_agg_display['Avg'].max()  > 0 else 1

        styled = (
            bat_agg_display.style
            .format({'Avg': '{:.1f}', 'SR': '{:.1f}', 'Boundary %': '{:.1f}%'}, na_rep='-')
            .bar(subset=['Runs'], color='#FF1493', vmin=0, vmax=max_runs)
            .bar(subset=['SR'],   color='#f5c518', vmin=0, vmax=max_sr)
            .bar(subset=['Avg'],  color='#00e5ff', vmin=0, vmax=max_avg)
        )
        st.dataframe(styled, use_container_width=True, height=400)

        selected = st.multiselect(
            "👆 Select Player(s) to analyse",
            bat_agg['batsmanName'].tolist(),
            default=st.session_state.selected_players if st.session_state.current_role == role_name else []
        )
        st.session_state.selected_players = selected
        show_player_details(selected, batting, bowling, players)

    with col2:
        st.markdown(_role_info_html(role_name), unsafe_allow_html=True)


def show_allrounder_section(batting, bowling, players):
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="section-heading">📋 <span class="accent">All-Rounder</span> Statistics</div>', unsafe_allow_html=True)

        allrounder_names = players[players['playingRole'].str.contains('Allrounder|All-Rounder', case=False, na=False)]['name'].tolist()
        role_batting = batting[batting['batsmanName'].isin(allrounder_names)].copy()
        role_bowling = bowling[bowling['bowlerName'].isin(allrounder_names)].copy()

        bat_agg  = get_batting_agg(role_batting)
        bowl_agg = get_bowling_agg(role_bowling)
        combined = bat_agg.merge(bowl_agg, left_on='batsmanName', right_on='bowlerName', how='outer').fillna(0)
        combined['total_value'] = combined['total_runs'] + combined['wickets'] * 25
        combined = combined.sort_values('total_value', ascending=False)
        combined = combined.merge(players[['name','team','battingStyle','bowlingStyle','playingRole']], left_on='batsmanName', right_on='name', how='left')

        display_cols = ['batsmanName','team','innings','total_runs','batting_avg','strike_rate','wickets','avg_economy']
        comb_display = combined[display_cols].copy()
        comb_display.columns = ['Name','Team','Innings','Runs','Avg','SR','Wkts','Econ']

        st.dataframe(
            comb_display.head(25).style
            .background_gradient(subset=['SR'],         cmap='Reds')
            .background_gradient(subset=['Runs','Wkts'],cmap='Blues')
            .format({'Avg': '{:.1f}', 'SR': '{:.1f}', 'Econ': '{:.2f}'}),
            use_container_width=True, height=400
        )

        selected = st.multiselect(
            "👆 Select All-Rounder(s)",
            combined['batsmanName'].tolist(),
            default=st.session_state.selected_players if st.session_state.current_role == "All Rounders" else []
        )
        st.session_state.selected_players = selected
        show_player_details(selected, batting, bowling, players)

    with col2:
        st.markdown(_role_info_html("All Rounders"), unsafe_allow_html=True)


def show_bowler_section(batting, bowling, players):
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="section-heading">📋 <span class="accent">Fast Bowler</span> Statistics</div>', unsafe_allow_html=True)

        bowler_agg = get_bowling_agg(bowling)
        bowler_agg = bowler_agg.merge(players[['name','team','bowlingStyle','playingRole']], left_on='bowlerName', right_on='name', how='left')
        bowler_agg = bowler_agg[bowler_agg['wickets'] >= 5].sort_values('wickets', ascending=False)

        display_cols = ['bowlerName','team','matches','overs','wickets','bowling_avg','avg_economy']
        bowl_display = bowler_agg[display_cols].copy()
        bowl_display.columns = ['Name','Team','Matches','Overs','Wkts','Avg','Econ']

        st.dataframe(
            bowl_display.style
            .background_gradient(subset=['Wkts'], cmap='Reds')
            .background_gradient(subset=['Econ'],  cmap='Greens')
            .format({'Avg': '{:.1f}', 'Econ': '{:.2f}'}),
            use_container_width=True, height=400
        )

        selected = st.multiselect(
            "👆 Select Bowler(s)",
            bowler_agg['bowlerName'].tolist(),
            default=st.session_state.selected_players if st.session_state.current_role == "Fast Bowlers" else []
        )
        st.session_state.selected_players = selected
        show_player_details(selected, batting, bowling, players)

    with col2:
        st.markdown(_role_info_html("Fast Bowlers"), unsafe_allow_html=True)


if __name__ == "__main__":
    main()