import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_match_summary():
    df = pd.read_csv('../t20-csv-files/dim_match_summary.csv')
    return df

@st.cache_data
def load_players():
    df = pd.read_csv('../t20-csv-files/dim_players.csv')
    return df

@st.cache_data
def load_batting():
    df = pd.read_csv('../t20-csv-files/fact_bating_summary.csv')
    return df

@st.cache_data
def load_bowling():
    df = pd.read_csv('../t20-csv-files/fact_bowling_summary.csv')
    return df

@st.cache_data
def get_processed_data():
    matches = load_match_summary()
    batting = load_batting()
    bowling = load_bowling()
    players = load_players()
    
    batting = batting.merge(matches[['match_id', 'team1', 'team2', 'ground', 'matchDate']], on='match_id', how='left')
    batting['opponent'] = batting.apply(
        lambda x: x['team2'] if x['teamInnings'] == x['team1'] else x['team1'], axis=1
    )
    
    bowling = bowling.merge(matches[['match_id', 'team1', 'team2', 'ground', 'matchDate']], on='match_id', how='left')
    bowling['opponent'] = bowling.apply(
        lambda x: x['team2'] if x['bowlingTeam'] == x['team1'] else x['team1'], axis=1
    )
    
    batting['boundary_runs'] = batting['4s'] * 4 + batting['6s'] * 6
    batting['boundary_pct'] = (batting['boundary_runs'] / batting['runs'].replace(0, np.nan)) * 100
    batting['boundary_pct'] = batting['boundary_pct'].fillna(0)
    
    batting['role_group'] = batting['battingPos'].apply(lambda x: 
        'Power Hitter' if x <= 2 else 
        'Anchor' if x <= 5 else 
        'Finisher' if x <= 7 else 'Lower Order'
    )
    
    bowling['overs'] = pd.to_numeric(bowling['overs'], errors='coerce')
    bowling['maidens'] = pd.to_numeric(bowling['maiden'], errors='coerce')
    bowling['bowl_runs'] = pd.to_numeric(bowling['runs'], errors='coerce')
    bowling['wickets'] = pd.to_numeric(bowling['wickets'], errors='coerce')
    bowling['economy'] = pd.to_numeric(bowling['economy'], errors='coerce')
    
    players_clean = players[['name', 'team', 'image', 'battingStyle', 'bowlingStyle', 'playingRole']].copy()
    players_clean = players_clean.drop_duplicates(subset=['name'])
    
    batting = batting.merge(players_clean, left_on='batsmanName', right_on='name', how='left')
    bowling = bowling.merge(players_clean, left_on='bowlerName', right_on='name', how='left')
    
    return matches, batting, bowling, players_clean

@st.cache_data
def get_batting_agg(batting_df, group_col='batsmanName'):
    agg = batting_df.groupby(group_col).agg({
        'runs': 'sum',
        'balls': 'sum',
        'match_id': 'nunique',
        '4s': 'sum',
        '6s': 'sum',
        'out/not_out': lambda x: (x == 'out').sum()
    }).reset_index()
    agg.columns = [group_col, 'total_runs', 'total_balls', 'innings', 'fours', 'sixes', 'dismissals']
    agg['not_out'] = agg['innings'] - agg['dismissals']
    agg['batting_avg'] = agg['total_runs'] / agg['not_out'].replace(0, np.nan)
    agg['batting_avg'] = agg['batting_avg'].fillna(agg['total_runs'])
    agg['strike_rate'] = (agg['total_runs'] / agg['total_balls'].replace(0, np.nan)) * 100
    agg['boundary_pct'] = ((agg['fours'] * 4 + agg['sixes'] * 6) / agg['total_runs'].replace(0, np.nan)) * 100
    return agg

@st.cache_data
def get_bowling_agg(bowling_df, group_col='bowlerName'):
    agg = bowling_df.groupby(group_col).agg({
        'overs': 'sum',
        'bowl_runs': 'sum',
        'wickets': 'sum',
        'maidens': 'sum',
        'economy': 'mean',
        'match_id': 'nunique'
    }).reset_index()
    agg.columns = [group_col, 'overs', 'runs_conceded', 'wickets', 'maidens', 'avg_economy', 'matches']
    agg['bowling_avg'] = agg['runs_conceded'] / agg['wickets'].replace(0, np.nan)
    agg['bowling_avg'] = agg['bowling_avg'].fillna(agg['runs_conceded'])
    return agg

@st.cache_data
def get_team_list(batting_df):
    teams = sorted(batting_df['teamInnings'].unique())
    return teams
