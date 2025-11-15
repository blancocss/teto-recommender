from flask import Flask, render_template, request
from recommender import load_movielens, recommend_movie

movies, ratings = load_movielens("ml-20m")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = None
    error = None
    movie_searched = None

    if request.method == "POST":
        user_input = request.form.get("movie_name", "").strip()

        if not user_input:
            error = "Please enter a movie name."
        else:
            movie_searched, recs = recommend_movie(user_input, movies, ratings)
            if recs is None:
                error = "Movie not found. Try another name."
            else:
                recommendations = recs

    return render_template(
        "index.html",
        recommendations=recommendations,
        movie_searched=movie_searched,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
