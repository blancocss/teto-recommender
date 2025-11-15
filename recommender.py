import os
import math
import pandas as pd

def load_movielens(data_folder="ml-20m"):
    movies_path = os.path.join(data_folder, "movies.csv")
    ratings_path = os.path.join(data_folder, "ratings.csv")

    movies = pd.read_csv(movies_path, usecols=["movieId", "title", "genres"])
    ratings = pd.read_csv(ratings_path, usecols=["userId", "movieId", "rating"])

    return movies, ratings

def recommend_movie(title, movies_df, ratings_df, top_n=12, min_overlap=20, min_rating=3.5):
    matches = movies_df[movies_df["title"].str.contains(title, case=False, na=False)]
    if matches.empty:
        return None, None

    seed = matches.iloc[0]
    seed_id = seed["movieId"]

    liked_by = ratings_df[
        (ratings_df["movieId"] == seed_id) &
        (ratings_df["rating"] >= min_rating)
    ]
    if liked_by.empty:
        return seed["title"], []

    user_ids = liked_by["userId"].unique()

    candidate_ratings = ratings_df[
        (ratings_df["userId"].isin(user_ids)) &
        (ratings_df["movieId"] != seed_id) &
        (ratings_df["rating"] >= min_rating)
    ]
    if candidate_ratings.empty:
        return seed["title"], []

    stats = candidate_ratings.groupby("movieId")["rating"].agg(["mean", "count"]).reset_index()
    stats = stats[stats["count"] >= min_overlap]
    if stats.empty:
        return seed["title"], []

    max_count = float(stats["count"].max())
    stats["score"] = (stats["mean"] / 5.0) * (stats["count"] / max_count)

    stats = stats.sort_values(by=["score", "mean"], ascending=False).head(top_n)

    recs = stats.merge(movies_df, on="movieId", how="left")

    emoji_map = {
        "Action": "🔥",
        "Adventure": "🗺️",
        "Animation": "🎨",
        "Comedy": "😂",
        "Crime": "🚔",
        "Drama": "🎭",
        "Fantasy": "🪄",
        "Horror": "👻",
        "Romance": "💘",
        "Science Fiction": "🛸",
        "Thriller": "🔪",
        "Family": "👨‍👩‍👧‍👦",
        "Mystery": "🕵️",
        "Music": "🎵",
        "War": "⚔️",
        "Western": "🤠"
    }

    display_genres = []
    for value in recs["genres"]:
        if isinstance(value, str):
            parts = [g for g in value.split("|") if g and g != "(no genres listed)"]
        else:
            parts = []
        tagged = []
        for p in parts:
            emoji = emoji_map.get(p, "🎬")
            tagged.append(emoji + " " + p)
        display_genres.append("|".join(tagged))

    recs["genres"] = display_genres
    recs = recs[["title", "genres", "mean", "score", "count"]]
    recs = recs.rename(columns={"mean": "avg_rating", "count": "num_ratings"})

    return seed["title"], recs.to_dict(orient="records")
