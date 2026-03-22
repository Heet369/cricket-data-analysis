import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def get_opponent_stats(batting_df, player_name):
    """Get batting stats by opponent for a player"""
    player_data = batting_df[batting_df['batsmanName'] == player_name]
    
    if len(player_data) == 0:
        return pd.DataFrame()
    
    opp_stats = player_data.groupby('opponent').agg({
        'runs': 'sum',
        'balls': 'sum',
        'match_id': 'count',
        'out/not_out': lambda x: (x == 'out').sum()
    }).reset_index()
    
    opp_stats.columns = ['opponent', 'runs', 'balls', 'innings', 'dismissals']
    opp_stats['not_out'] = opp_stats['innings'] - opp_stats['dismissals']
    opp_stats['avg'] = opp_stats['runs'] / opp_stats['not_out'].replace(0, np.nan)
    opp_stats['avg'] = opp_stats['avg'].fillna(opp_stats['runs'])
    opp_stats['sr'] = (opp_stats['runs'] / opp_stats['balls'].replace(0, np.nan)) * 100
    opp_stats['balls_per_innings'] = opp_stats['balls'] / opp_stats['innings']
    
    return opp_stats


def plot_performance_over_opponents(batting_df, player_names, metric='avg'):
    """Line chart showing player performance over opponents"""
    if not player_names:
        return None
    
    all_stats = []
    for player in player_names:
        stats = get_opponent_stats(batting_df, player)
        if len(stats) > 0:
            stats['player'] = player
            all_stats.append(stats)
    
    if not all_stats:
        return None
    
    combined = pd.concat(all_stats, ignore_index=True)
    
    metric_label = 'Batting Average' if metric == 'avg' else 'Strike Rate'
    y_col = metric
    
    # Sort opponents by total runs across all players
    opp_order = combined.groupby('opponent')['runs'].sum().sort_values(ascending=False).index.tolist()
    combined['opponent'] = pd.Categorical(combined['opponent'], categories=opp_order, ordered=True)
    combined = combined.sort_values(['player', 'opponent'])
    
    colors = ['#FFD700', '#FF1493', '#00B7EB', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    fig = px.line(
        combined, 
        x='opponent', 
        y=y_col, 
        color='player',
        markers=True,
        title=f'📈 {metric_label} vs Opponents',
        color_discrete_sequence=colors[:len(player_names)]
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30,41,59,0.5)',
        font=dict(color='#e2e8f0', size=12),
        title=dict(font=dict(size=18, color='#FFD700')),
        xaxis=dict(
            title='Opponent',
            gridcolor='rgba(255,255,255,0.1)',
            tickangle=-45
        ),
        yaxis=dict(
            title=metric_label,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        legend=dict(
            title=dict(text='Player', font=dict(color='#FFD700')),
            font=dict(color='#e2e8f0'),
            bgcolor='rgba(30,41,59,0.8)'
        ),
        hovermode='x unified'
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=10, line=dict(width=1, color='#0f172a'))
    )
    
    return fig


def plot_avg_vs_sr_scatter(batting_df, player_names=None):
    """Scatter plot: Batting Average vs Strike Rate with bubble size = runs"""
    # Get aggregated stats for all players
    agg = batting_df.groupby('batsmanName').agg({
        'runs': 'sum',
        'balls': 'sum',
        'match_id': 'nunique',
        'out/not_out': lambda x: (x == 'out').sum(),
        'teamInnings': 'first'
    }).reset_index()
    
    agg.columns = ['batsmanName', 'runs', 'balls', 'innings', 'dismissals', 'team']
    agg['not_out'] = agg['innings'] - agg['dismissals']
    agg['avg'] = agg['runs'] / agg['not_out'].replace(0, np.nan)
    agg['avg'] = agg['avg'].fillna(agg['runs'])
    agg['sr'] = (agg['runs'] / agg['balls'].replace(0, np.nan)) * 100
    
    # Filter to selected players if provided
    if player_names:
        agg = agg[agg['batsmanName'].isin(player_names)]
    
    if len(agg) == 0:
        return None
    
    # Calculate league averages
    league_avg = agg['avg'].mean()
    league_sr = agg['sr'].mean()
    
    # Team colors
    team_colors = {
        'India': '#FF9933', 'England': '#CE1124', 'Australia': '#FFDD00',
        'Pakistan': '#01411C', 'South Africa': '#007A4D', 'New Zealand': '#00247D',
        'Sri Lanka': '#003594', 'Bangladesh': '#006A4E', 'Afghanistan': '#BB0000',
        'West Indies': '#790919', 'Ireland': '#169B62', 'Zimbabwe': '#CB0000',
        'Netherlands': '#FF6600', 'Scotland': '#005EB8', 'Namibia': '#00247D',
        'U.A.E.': '#007A3D'
    }
    
    agg['color'] = agg['team'].map(team_colors).fillna('#888888')
    
    fig = px.scatter(
        agg,
        x='avg',
        y='sr',
        size='runs',
        color='batsmanName',
        hover_data={'runs': True, 'innings': True, 'avg': ':.1f', 'sr': ':.1f', 'team': True},
        title='⚡ Batting Average vs Strike Rate',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.add_hline(
        y=league_sr, 
        line_dash='dash', 
        line_color='#FFD700',
        annotation_text=f'Avg SR: {league_sr:.1f}',
        annotation_position='top right'
    )
    
    fig.add_vline(
        x=league_avg, 
        line_dash='dash', 
        line_color='#FF1493',
        annotation_text=f'Avg: {league_avg:.1f}',
        annotation_position='top'
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30,41,59,0.5)',
        font=dict(color='#e2e8f0', size=12),
        title=dict(font=dict(size=18, color='#FFD700')),
        xaxis=dict(
            title='Batting Average',
            gridcolor='rgba(255,255,255,0.1)',
            range=[0, agg['avg'].max() * 1.1]
        ),
        yaxis=dict(
            title='Strike Rate',
            gridcolor='rgba(255,255,255,0.1)',
            range=[0, agg['sr'].max() * 1.1]
        ),
        legend=dict(
            title=dict(text='Player', font=dict(color='#FFD700')),
            font=dict(color='#e2e8f0'),
            bgcolor='rgba(30,41,59,0.8)'
        ),
        hovermode='closest'
    )
    
    fig.update_traces(
        marker=dict(
            opacity=0.8,
            line=dict(width=1, color='#ffffff')
        )
    )
    
    return fig


def get_combined_stats(batting_df, player_names):
    """Get combined stats for selected players"""
    if not player_names:
        return {}
    
    player_data = batting_df[batting_df['batsmanName'].isin(player_names)]
    
    if len(player_data) == 0:
        return {}
    
    total_runs = player_data['runs'].sum()
    total_balls = player_data['balls'].sum()
    matches = player_data['match_id'].nunique()
    dismissals = (player_data['out/not_out'] == 'out').sum()
    not_out = matches - dismissals
    
    avg = total_runs / not_out if not_out > 0 else total_runs
    sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
    boundary_runs = (player_data['4s'].sum() * 4 + player_data['6s'].sum() * 6)
    boundary_pct = (boundary_runs / total_runs * 100) if total_runs > 0 else 0
    avg_balls_faced = total_balls / matches if matches > 0 else 0
    
    return {
        'players': len(player_names),
        'matches': matches,
        'total_runs': total_runs,
        'avg': avg,
        'sr': sr,
        'boundary_pct': boundary_pct,
        'avg_balls_faced': avg_balls_faced
    }


def plot_progress_bar(value, max_value, color='#FF1493', width=150):
    """Generate HTML for a progress bar"""
    if max_value == 0:
        pct = 0
    else:
        pct = min((value / max_value) * 100, 100)
    
    return f"""
    <div style="display: flex; align-items: center; gap: 8px;">
        <div style="flex-grow: 1; height: 12px; background: #1e293b; border-radius: 6px; overflow: hidden;">
            <div style="width: {pct}%; height: 100%; background: {color}; border-radius: 6px;"></div>
        </div>
        <span style="color: #e2e8f0; font-size: 12px; min-width: 40px; text-align: right;">{value}</span>
    </div>
    """
