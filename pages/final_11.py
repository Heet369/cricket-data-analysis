import streamlit as st
import pandas as pd
import numpy as np
from utils.data import get_processed_data, get_batting_agg, get_bowling_agg

st.set_page_config(layout="wide", page_title="Final XI Builder", page_icon="🏆")

# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS — Final XI Builder: "Cricket Pitch" gamified dark UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --pitch:           #0b1120;
    --floodlight:      #f5c518;
    --floodlight-dim:  rgba(245,197,24,0.12);
    --neon-pink:       #ff2d78;
    --neon-cyan:       #00e5ff;
    --neon-green:      #39ff14;
    --slot-empty:      #141f35;
    --slot-filled:     #1a2d1a;
    --slate:           #1c2840;
    --slate-border:    #2a3a58;
    --glass:           rgba(255,255,255,0.04);
    --glass-border:    rgba(255,255,255,0.08);
    --text-primary:    #f0f4ff;
    --text-muted:      #6b7fa3;
}

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: var(--pitch) !important;
    color: var(--text-primary);
}

/* Atmospheric pitch grid bg */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 50% at 50% 0%, rgba(245,197,24,0.07) 0%, transparent 70%),
        radial-gradient(ellipse 40% 60% at 0% 100%, rgba(0,229,255,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 100% 80%, rgba(255,45,120,0.04) 0%, transparent 60%),
        repeating-linear-gradient(0deg, transparent, transparent 59px, rgba(255,255,255,0.015) 59px, rgba(255,255,255,0.015) 60px),
        repeating-linear-gradient(90deg, transparent, transparent 59px, rgba(255,255,255,0.01) 59px, rgba(255,255,255,0.01) 60px);
    pointer-events: none;
    z-index: 0;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1829 0%, #0b1120 100%) !important;
    border-right: 1px solid var(--slate-border);
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Page hero ── */
.page-hero {
    background: linear-gradient(135deg, #0f1b2d 0%, #0b1120 100%);
    border: 1px solid var(--slate-border);
    border-top: 3px solid var(--floodlight);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.page-hero::before {
    content: '🏆';
    position: absolute;
    right: -10px; top: -10px;
    font-size: 130px;
    opacity: 0.04;
}
.page-hero::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--floodlight), transparent);
    animation: shimmer 2.5s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { opacity: 0.3; }
    50%       { opacity: 1; }
}

.page-hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: .06em;
    color: #fff;
    line-height: 1;
    margin: 0;
}
.page-hero-title span { color: var(--floodlight); }
.page-hero-sub {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin: 8px 0 0 0;
}

/* ── Slot counter ── */
.slot-counter {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 12px 0 24px 0;
}
.slot-pip {
    width: 28px; height: 8px;
    border-radius: 4px;
    background: var(--slot-empty);
    border: 1px solid var(--slate-border);
    transition: all 0.3s;
}
.slot-pip.filled {
    background: var(--floodlight);
    border-color: var(--floodlight);
    box-shadow: 0 0 8px rgba(245,197,24,0.5);
}

/* ── Search & filter bar ── */
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] {
    background: var(--slate) !important;
    border: 1px solid var(--slate-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--floodlight) !important;
    box-shadow: 0 0 0 2px var(--floodlight-dim) !important;
}

/* ── Player card grid ── */
.player-grid { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }

.p-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 12px 16px;
    transition: all 0.2s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.p-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: transparent;
    transition: background 0.2s;
}
.p-card:hover { border-color: var(--floodlight); transform: translateX(3px); }
.p-card:hover::before { background: var(--floodlight); }
.p-card.in-team {
    background: rgba(57,255,20,0.06);
    border-color: rgba(57,255,20,0.35);
}
.p-card.in-team::before { background: var(--neon-green); }

.p-name {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-primary);
}
.p-meta {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 2px;
}
.p-role-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 999px;
    border: 1px solid;
}
.role-bat   { color: #f5c518; border-color: rgba(245,197,24,0.3); background: rgba(245,197,24,0.08); }
.role-bowl  { color: #ff2d78; border-color: rgba(255,45,120,0.3);  background: rgba(255,45,120,0.08); }
.role-all   { color: #00e5ff; border-color: rgba(0,229,255,0.3);   background: rgba(0,229,255,0.08); }
.role-wk    { color: #a78bfa; border-color: rgba(167,139,250,0.3); background: rgba(167,139,250,0.08); }

/* ── Add / Remove buttons ── */
div[data-testid="stButton"] > button {
    background: transparent !important;
    border: 1px solid var(--slate-border) !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    padding: 4px 14px !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: var(--floodlight) !important;
    color: var(--floodlight) !important;
    background: var(--floodlight-dim) !important;
}
/* Primary / danger button for Clear */
div[data-testid="stButton"] > button[kind="primary"] {
    border-color: var(--neon-pink) !important;
    color: var(--neon-pink) !important;
    background: rgba(255,45,120,0.08) !important;
}

/* ── Team board (right panel) ── */
.team-board {
    background: linear-gradient(160deg, #0f1e18 0%, #0b1120 100%);
    border: 1px solid rgba(57,255,20,0.2);
    border-radius: 18px;
    padding: 24px 20px;
    min-height: 600px;
    position: sticky;
    top: 20px;
}
.team-board-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: .06em;
    color: var(--neon-green);
    margin: 0 0 4px 0;
}
.team-board-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: .18em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* ── Pitch visual ── */
.pitch-visual {
    background: linear-gradient(180deg, #0d2a0d 0%, #0a1e0a 100%);
    border: 1px solid rgba(57,255,20,0.15);
    border-radius: 12px;
    padding: 16px 12px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.pitch-visual::before {
    content: '';
    position: absolute;
    left: 50%; top: 0; bottom: 0;
    width: 1px;
    background: repeating-linear-gradient(180deg, rgba(255,255,255,0.12) 0px, rgba(255,255,255,0.12) 4px, transparent 4px, transparent 12px);
    transform: translateX(-50%);
}
.pitch-row {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin-bottom: 6px;
}
.pitch-slot {
    background: rgba(245,197,24,0.08);
    border: 1px dashed rgba(245,197,24,0.25);
    border-radius: 8px;
    padding: 5px 8px;
    min-width: 90px;
    text-align: center;
    transition: all 0.25s;
}
.pitch-slot.filled {
    background: rgba(245,197,24,0.15);
    border: 1px solid rgba(245,197,24,0.5);
    box-shadow: 0 0 10px rgba(245,197,24,0.15);
}
.pitch-slot .slot-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: .1em;
}
.pitch-slot .slot-name {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--floodlight);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 84px;
}
.pitch-slot.empty .slot-name {
    color: var(--slate-border);
    font-weight: 400;
    font-style: italic;
}

/* ── Team stats row ── */
.team-stat-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 14px;
}
.team-stat {
    flex: 1;
    min-width: 70px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
}
.team-stat .ts-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem;
    color: #fff;
    line-height: 1;
}
.team-stat .ts-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: .12em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-top: 3px;
}

/* ── Capacity warning ── */
.cap-warning {
    background: rgba(255,45,120,0.1);
    border: 1px solid rgba(255,45,120,0.3);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: var(--neon-pink);
    margin-bottom: 12px;
    text-align: center;
}
.cap-ok {
    background: rgba(57,255,20,0.07);
    border: 1px solid rgba(57,255,20,0.2);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: var(--neon-green);
    margin-bottom: 12px;
    text-align: center;
}

/* ── Metric overrides ── */
div[data-testid="stMetric"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.72rem !important; }
div[data-testid="stMetricValue"] { color: #fff !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 1.7rem !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--slate-border) !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    padding: 9px 16px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--floodlight) !important;
    border-bottom: 2px solid var(--floodlight) !important;
    background: var(--floodlight-dim) !important;
}

hr { border-color: var(--slate-border) !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--pitch); }
::-webkit-scrollbar-thumb { background: var(--slate-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--floodlight); }

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* Stagger cards */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def role_badge(role_str: str) -> str:
    r = str(role_str).lower()
    if 'allrounder' in r or 'all-rounder' in r:
        return '<span class="p-role-badge role-all">All-Rounder</span>'
    if 'wicket' in r or 'keeper' in r or 'wk' in r:
        return '<span class="p-role-badge role-wk">WK-Batter</span>'
    if 'bowl' in r:
        return '<span class="p-role-badge role-bowl">Bowler</span>'
    return '<span class="p-role-badge role-bat">Batter</span>'


def slot_pips_html(count: int, total: int = 11) -> str:
    pips = ''.join(
        f'<div class="slot-pip {"filled" if i < count else ""}"></div>'
        for i in range(total)
    )
    return f'<div class="slot-counter">{pips}</div>'


PITCH_LAYOUT = [
    ["Opener 1", "Opener 2"],
    ["No. 3", "No. 4", "No. 5"],
    ["No. 6", "No. 7"],
    ["No. 8", "No. 9"],
    ["No. 10", "No. 11"],
]

def pitch_visual_html(final_11: list) -> str:
    rows_html = ""
    idx = 0
    for row in PITCH_LAYOUT:
        slots_html = ""
        for label in row:
            if idx < len(final_11):
                name = final_11[idx]
                short = name.split()[-1] if name else "—"
                slots_html += f"""
                <div class="pitch-slot filled">
                    <div class="slot-num">{label}</div>
                    <div class="slot-name" title="{name}">{short}</div>
                </div>"""
            else:
                slots_html += f"""
                <div class="pitch-slot empty">
                    <div class="slot-num">{label}</div>
                    <div class="slot-name">Empty</div>
                </div>"""
            idx += 1
        rows_html += f'<div class="pitch-row">{slots_html}</div>'
    return f'<div class="pitch-visual">{rows_html}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    _, batting, bowling, players = get_processed_data()

    if 'final_11' not in st.session_state:
        st.session_state.final_11 = []

    count = len(st.session_state.final_11)

    # ── Hero ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-hero">
        <div class="page-hero-title">Build Your <span>Final XI</span></div>
        <p class="page-hero-sub">Analyse stats · Compare roles · Assemble your dream team</p>
        {slot_pips_html(count)}
    </div>
    """, unsafe_allow_html=True)

    col_list, col_team = st.columns([2, 1], gap="large")

    # ── LEFT: Player selection ────────────────────────────────────────────
    with col_list:
        st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;letter-spacing:.06em;color:#fff;margin-bottom:12px;">👥 Available Players</div>', unsafe_allow_html=True)

        s_col1, s_col2 = st.columns([2, 1])
        with s_col1:
            search = st.text_input("🔍 Search by name", "", placeholder="e.g. Kohli, Buttler…")
        with s_col2:
            role_filter = st.selectbox("Role", ["All", "Batter", "Bowler", "Allrounder", "Wicketkeeper"])

        player_list = (
            players[['name','team','playingRole','battingStyle','bowlingStyle']]
            .dropna(subset=['name'])
            .drop_duplicates(subset=['name'])
        )
        if search:
            player_list = player_list[player_list['name'].str.contains(search, case=False, na=False)]
        if role_filter != "All":
            player_list = player_list[player_list['playingRole'].str.contains(role_filter, case=False, na=False)]

        # Tabs: All / In Team
        tab_all, tab_squad = st.tabs(["All Players", "Your XI"])

        with tab_all:
            for _, row in player_list.head(40).iterrows():
                in_team   = row['name'] in st.session_state.final_11
                card_cls  = "p-card in-team" if in_team else "p-card"
                badge_html = role_badge(row.get('playingRole',''))

                st.markdown(f"""
                <div class="{card_cls}" style="margin-bottom:4px;">
                    <div>
                        <div class="p-name">{row['name']}</div>
                        <div class="p-meta">{row.get('team','—')}</div>
                    </div>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)

                btn_label = f"✓ Remove" if in_team else f"+ Add"
                if st.button(btn_label, key=f"btn_{row['name']}"):
                    if in_team:
                        st.session_state.final_11.remove(row['name'])
                    else:
                        if len(st.session_state.final_11) < 11:
                            st.session_state.final_11.append(row['name'])
                        else:
                            st.warning("Maximum 11 players reached! Remove someone first.")
                    st.rerun()

        with tab_squad:
            if not st.session_state.final_11:
                st.markdown('<p style="color:#6b7fa3;font-style:italic;margin-top:16px;">No players selected yet.</p>', unsafe_allow_html=True)
            else:
                for i, p in enumerate(st.session_state.final_11, 1):
                    p_row = player_list[player_list['name'] == p]
                    team  = p_row.iloc[0]['team'] if len(p_row) > 0 else "—"
                    role  = p_row.iloc[0]['playingRole'] if len(p_row) > 0 else ""
                    badge = role_badge(role)

                    st.markdown(f"""
                    <div class="p-card in-team" style="margin-bottom:4px;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#f5c518;width:22px;text-align:center;">{i}</div>
                            <div>
                                <div class="p-name">{p}</div>
                                <div class="p-meta">{team}</div>
                            </div>
                        </div>
                        {badge}
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"✕ Remove", key=f"rem_{p}_{i}"):
                        st.session_state.final_11.remove(p)
                        st.rerun()

    # ── RIGHT: Team board ─────────────────────────────────────────────────
    with col_team:
        st.markdown("""
        <div class="team-board">
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="team-board-title">Your XI</div>
        <div class="team-board-sub">ICC T20 World Cup 2022</div>
        """, unsafe_allow_html=True)

        # Capacity status
        if count == 11:
            st.markdown('<div class="cap-ok">✅ XI Complete — Ready for battle!</div>', unsafe_allow_html=True)
        elif count > 0:
            st.markdown(f'<div class="cap-warning">{11 - count} slots remaining</div>', unsafe_allow_html=True)

        # Pitch visual
        st.markdown(pitch_visual_html(st.session_state.final_11), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Clear button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑 Clear All", type="primary", use_container_width=True):
            st.session_state.final_11 = []
            st.rerun()

        # ── Team aggregate stats ──────────────────────────────────────────
        if st.session_state.final_11:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;letter-spacing:.06em;color:#fff;margin-bottom:10px;">📊 Team Stats</div>', unsafe_allow_html=True)

            final_batting = batting[batting['batsmanName'].isin(st.session_state.final_11)]
            final_bowling = bowling[bowling['bowlerName'].isin(st.session_state.final_11)]

            bat_runs = "—"
            bat_sr   = "—"
            bow_wkts = "—"
            bow_econ = "—"

            if len(final_batting) > 0:
                bat_agg  = get_batting_agg(final_batting)
                bat_runs = f"{int(bat_agg['total_runs'].sum()):,}"
                bat_sr   = f"{bat_agg['strike_rate'].mean():.1f}"

            if len(final_bowling) > 0:
                bowl_agg = get_bowling_agg(final_bowling)
                bow_wkts = str(int(bowl_agg['wickets'].sum()))
                try:
                    bow_econ = f"{bowl_agg['economy'].mean():.2f}"
                except Exception:
                    bow_econ = f"{bowl_agg['avg_economy'].mean():.2f}"

            st.markdown(f"""
            <div class="team-stat-row">
                <div class="team-stat">
                    <div class="ts-val">{bat_runs}</div>
                    <div class="ts-lbl">Total Runs</div>
                </div>
                <div class="team-stat">
                    <div class="ts-val">{bat_sr}</div>
                    <div class="ts-lbl">Avg SR</div>
                </div>
                <div class="team-stat">
                    <div class="ts-val">{bow_wkts}</div>
                    <div class="ts-lbl">Wickets</div>
                </div>
                <div class="team-stat">
                    <div class="ts-val">{bow_econ}</div>
                    <div class="ts-lbl">Economy</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()