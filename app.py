from flask import Flask, render_template, request
from recommender import load_movielens, recommend_movie

movies, ratings = load_movielens()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = None
    error = None
    movie_searched = None

    if request.method == "POST":
        movie_name = request.form.get("movie_name", "").strip()

        if not movie_name:
            error = "Please enter a movie name."
        else:
            movie_searched, recs = recommend_movie(movie_name, movies, ratings)
            if recs is None:
                error = "Movie not found."
            else:
                recommendations = recs

    return render_template(
        "index.html",
        error=error,
        recommendations=recommendations,
        movie_searched=movie_searched
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
