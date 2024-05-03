import os


ASSET_DIR = os.path.join("MLBTunnelBot", "assets")
TUNNEL_PLOT_DIR = os.path.join(ASSET_DIR, "tunnel_plot.png")
PROFILE_PIC_DIR = os.path.join(ASSET_DIR, "profile_pic.jpg")
DEFAULT_PROFILE_PIC_DIR = os.path.join(ASSET_DIR, "default_profile_pic.png")


keeper_cols: list[str] = [
    "pitcher",
    "batter",
    "home_team",
    "away_team",
    "inning",
    "prev_inning",
    "balls",
    "prev_balls",
    "strikes",
    "prev_strikes",
    "outs_when_up",
    "prev_outs_when_up",
    "des",
    "prev_des",
    "pitch_type",
    "prev_pitch_type",
    "pitch_name",
    "prev_pitch_name",
    "game_date",
    "tunnel_distance",
    "actual_distance",
    "p_throws",
    "stand",
    "inning_topbot",
    "plate_x",
    "plate_z",
    "plate_z_no_movement",
    "plate_x_no_movement",
    "prev_plate_x",
    "prev_plate_z",
    "prev_plate_z_no_movement",
    "prev_plate_x_no_movement",
    "tunnel_score",
    "at_bat_number",
    "pitch_number",
    "prev_pitch_number",
]

# 2024 mlb team official hashtags
# https://lwosports.com/the-offical-mlb-hashtags-for-the-2024-season/
hashtag_map = {
    "DET": "RepDetroit",
    "CLE": "ForTheLand",
    "MNT": "MNTwins",
    "KCR": "WelcomeToTheCity",
    "CWS": "WhiteSox",
    "HOU": "Relentless",
    "LAA": "RepTheHalo",
    "SEA": "TridentsUp",
    "TXR": "StraightUpTX",
    "OAK": "Athletics",
    "CIN": "ATOBTTR",
    "STL": "ForTheLou",
    "MIL": "ThisIsMyCrew",
    "PIT": "LetsGoBucs",
    "CHC": "YouHaveToSeeIt",
    "LAD": "LetsGoDodgers",
    "SDP": "LetsGoPadres",
    "SFG": "SFGiants",
    "ARI": "DBacks",
    "DEN": "Rockies",
    "NYY": "RepBX",
    "BOS": "DirtyWater",
    "TOR": "TOTHECORE",
    "TBR": "RaysUp",
    "BOR": "Birdland",
    "ATL": "BravesCountry",
    "NYM": "LGM",
    "PHI": "RingTheBell",
    "MIA": "HomeOfBeisbol",
    "WSH": "NATITUDE",
}
