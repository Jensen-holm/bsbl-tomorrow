import polars as pl
import numpy as np
import pybaseball
import datetime
from matplotlib import axes

from plot_tunnel import plot_strike_zone
from film_room import get_pitch


YEAR = str(datetime.date.today().year)
MONTH = str(datetime.date.today().month)
YESTERDAY = datetime.date.today() - datetime.timedelta(days=1)


def _get_yesterdays_pitches() -> pl.DataFrame:
    return pl.from_pandas(pybaseball.statcast(
        start_dt=str(YESTERDAY),
        end_dt=str(YESTERDAY),
    ))


def _tie_pitches_to_previous(pitches_df: pl.DataFrame) -> pl.DataFrame:
    sorted_pitches = pitches_df.sort(
        ["game_date", "pitcher", "at_bat_number", "pitch_number"],
        descending=True,
    )

    for col_name in sorted_pitches.columns:
        sorted_pitches = sorted_pitches.with_columns(
            pl.col(col_name).shift(1).over("pitcher").alias(f"prev_{col_name}")
        )
    return sorted_pitches


def _get_player_names(pitches_df: pl.DataFrame) -> pl.DataFrame:
    pitchers=pybaseball.playerid_reverse_lookup(
        [pitcher["pitcher"] for pitcher in pitches_df.iter_rows(named=True)],
        key_type="mlbam",
    )
    pitchers["name"] = (pitchers["name_first"] + " " + pitchers["name_last"]).str.title()

    return pitches_df.join(
        other=pl.from_pandas(pitchers[["key_mlbam", "name"]]),
        left_on="pitcher",
        right_on="key_mlbam",
    )

def _compute_tunnel_score(statcast_pitches_df: pl.DataFrame) -> pl.DataFrame:
    def _euclidean_distance(point1: tuple[pl.Expr, ...], point2: tuple[pl.Expr, ...]):
        x1, y1 = point1
        x2, y2 = point2
        return np.sqrt(((x1 - x2) ** 2 + (y1 - y2) ** 2))

    statcast_with_no_move = statcast_pitches_df.with_columns(
        plate_x_no_movement=pl.col("plate_x") - pl.col("pfx_x"),
        plate_z_no_movement=pl.col("plate_z") - pl.col("pfx_z"),
        prev_plate_x_no_movement=pl.col("prev_plate_x") - pl.col("prev_pfx_x"),
        prev_plate_z_no_movement=pl.col("prev_plate_z") - pl.col("prev_pfx_z"),
    )

    return statcast_with_no_move.with_columns(
        tunnel_distance=_euclidean_distance(
            point1=(pl.col("plate_x_no_movement"), pl.col("plate_z_no_movement")),
            point2=(
                pl.col("prev_plate_x_no_movement"),
                pl.col("prev_plate_z_no_movement"),
            ),
        ),
        actual_distance=_euclidean_distance(
            point1=(pl.col("plate_x"), pl.col("plate_z")),
            point2=(pl.col("prev_plate_x"), pl.col("prev_plate_z")),
        ),

        release_distance=_euclidean_distance(
            point1=(pl.col("release_pos_x"), pl.col("release_pos_z")),
            point2=(pl.col("prev_release_pos_x"), pl.col("release_pos_z")),
        )
    ).with_columns(
        tunnel_score=pl.col("actual_distance") / pl.col("tunnel_distance"),
    )


def _plot_pitches(tunneled_pitch: pl.DataFrame) -> axes.Axes:
    # input should be a polars dataframe with just one pitch
    # and it s previous one
    
    p1 = tunneled_pitch.select(
        "game_date",
        "at_bat_number",
        "pitch_number",
        "pitch_type",
        "pitch_name",
        "plate_x",
        "plate_z",
        "plate_x_no_movement",
        "plate_z_no_movement",
    )

    pitch2 = tunneled_pitch.select(
        "game_date",
        "at_bat_number",
        "prev_pitch_number",
        "prev_pitch_type",
        "prev_pitch_name",
        "prev_plate_x",
        "prev_plate_z",
        "plate_x_no_movement",
        "plate_z_no_movement",
    )

    p2 = pitch2.rename({
        col: "_".join(col.split("_")[1:]) if col.startswith("prev") else col for col in pitch2.columns
    })

    tunnel_score = tunneled_pitch.select("tunnel_score").item()
    print(tunneled_pitch.select("tunnel_distance").item())
    pitcher = tunneled_pitch.select("name").item() 
    df = pitch2.join(other=pl.concat([p1, p2,]), on=["game_date", "at_bat_number"]).to_pandas()

    fig = plot_strike_zone(
        data=df,
        title=f"Best Pitch Yesterday by Tunnel Score\n{pitcher} {tunnel_score:.2f}",
        colorby="pitch_name",
        annotation="pitch_number",
    )
    return fig


def _get_film_room_video(pitch: pl.DataFrame) -> tuple[str, str]:
    inning = pitch.select("inning").item()
    top_bot = pitch.select("inning_topbot").item() # needs to be either TOP or BOT
    balls = pitch.select("balls").item()
    strikes = pitch.select("strikes").item()
    pitcher_id = pitch.select("pitcher").item()
    outs = pitch.select("outs_when_up").item()

    prev_outs = pitch.select("prev_outs_when_up").item()
    prev_strikes = pitch.select("prev_strikes").item()
    prev_balls = pitch.select("prev_balls").item()

    url1 = f"https://www.mlb.com/video/?q=Season+%3D+%5B{YEAR}%5D+AND+Date+%3D+%5B%22{YESTERDAY}%22%5D+AND+PitcherId+%3D+%5B{pitcher_id}%5D+AND+TopBottom+%3D+%5B%22{top_bot.upper()}%22%5D+AND+Outs+%3D+%5B{outs}%5D+AND+Balls+%3D+%5B{balls}%5D+AND+Strikes+%3D+%5B{strikes}%5D+AND+Inning+%3D+%5B{inning}%5D+Order+By+Timestamp+DESC"
    url2 = f"https://www.mlb.com/video/?q=Season+%3D+%5B{YEAR}%5D+AND+Date+%3D+%5B%22{YESTERDAY}%22%5D+AND+PitcherId+%3D+%5B{pitcher_id}%5D+AND+TopBottom+%3D+%5B%22{top_bot.upper()}%22%5D+AND+Outs+%3D+%5B{prev_outs}%5D+AND+Balls+%3D+%5B{prev_balls}%5D+AND+Strikes+%3D+%5B{prev_strikes}%5D+AND+Inning+%3D+%5B{inning}%5D+Order+By+Timestamp+DESC"
    return url1, url2


def main() -> None:
    yesterdays_df: pl.DataFrame = _get_yesterdays_pitches()
    tied_df: pl.DataFrame = _tie_pitches_to_previous(yesterdays_df)
    tunnel_df: pl.DataFrame = _compute_tunnel_score(tied_df)

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

    # drop missing values from tunnel_df
    tunnel_df = tunnel_df.drop_nulls(subset=keeper_cols).select(
        keeper_cols,
    )

    tunnel_df = (
        tunnel_df
        .drop_nulls(subset=keeper_cols)
        .select(keeper_cols)
        .sort("tunnel_score", descending=True)
    )

    tunnel_df = _get_player_names(tunnel_df)
    fig = _plot_pitches(tunnel_df.head(1))
    f1, f2 = _get_film_room_video(pitch=tunnel_df.head(1))
    print(f1, f2)

if __name__ == "__main__":
    main()
