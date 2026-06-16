import streamlit as st
import pickle
import pandas as pd
import requests

# ==========================
# TMDB API KEY
# ==========================
API_KEY = "f0b188273a76c549a4dd8777889cdec2"

# Placeholder image
PLACEHOLDER = "https://via.placeholder.com/300x450?text=No+Poster"

# ==========================
# Fetch Movie Details
# ==========================
def fetch_movie_details(movie_id):

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

        response = requests.get(url, timeout=30)

        if response.status_code != 200:

            return {
                "poster": PLACEHOLDER,
                "rating": "N/A",
                "release_date": "N/A",
                "overview": "No overview available.",
                "genres": "N/A",
                "runtime": "N/A",
                "budget": 0,
                "revenue": 0
            }

        data = response.json()

        poster = PLACEHOLDER

        if data.get("poster_path"):

            poster = (
                "https://image.tmdb.org/t/p/w500"
                + data["poster_path"]
            )

        genres = ", ".join(
            [g["name"] for g in data.get("genres", [])]
        )

        return {
            "poster": poster,
            "rating": data.get("vote_average", "N/A"),
            "release_date": data.get("release_date", "N/A"),
            "overview": data.get(
                "overview",
                "No overview available."
            ),
            "genres": genres if genres else "N/A",
            "runtime": data.get("runtime", "N/A"),
            "budget": data.get("budget", 0),
            "revenue": data.get("revenue", 0)
        }

    except Exception as e:

        print("TMDB Error:", e)

        return {
            "poster": PLACEHOLDER,
            "rating": "N/A",
            "release_date": "N/A",
            "overview": "No overview available.",
            "genres": "N/A",
            "runtime": "N/A",
            "budget": 0,
            "revenue": 0
        }


# ==========================
# Fetch Cast
# ==========================
def fetch_cast(movie_id):

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"

        data = requests.get(
            url,
            timeout=30
        ).json()

        cast_names = []

        for actor in data.get("cast", [])[:5]:

            cast_names.append(
                actor["name"]
            )

        return ", ".join(cast_names)

    except:

        return "N/A"


# ==========================
# Fetch Trailer
# ==========================
def fetch_trailer(movie_id):

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

        data = requests.get(
            url,
            timeout=30
        ).json()

        for video in data.get("results", []):

            if video["site"] == "YouTube":

                return (
                    "https://www.youtube.com/watch?v="
                    + video["key"]
                )

        return None

    except:

        return None


# ==========================
# Recommendation Function
# ==========================
def recommend(movie):

    movie_index = movies[
        movies['title'] == movie
    ].index[0]

    distances = similarity[
        movie_index
    ]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_details = []
    recommended_ids = []

    for i in movie_list:

        movie_row = movies.iloc[i[0]]

        movie_id = movie_row['movie_id']

        recommended_movies.append(
            movie_row['title']
        )

        recommended_details.append(
            fetch_movie_details(movie_id)
        )

        recommended_ids.append(
            movie_id
        )

    return (
        recommended_movies,
        recommended_details,
        recommended_ids
    )


# ==========================
# Load Data
# ==========================
movies_dict = pickle.load(
    open('movie_dict.pkl', 'rb')
)

movies = pd.DataFrame(
    movies_dict
)

similarity = pickle.load(
    open('similarity.pkl', 'rb')
)

# ==========================
# Page Config
# ==========================
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# ==========================
# Title
# ==========================
st.title(
    "🎬 MOVIE RECOMMENDATION SYSTEM"
)

# ==========================
# Searchable Movie Dropdown
# ==========================
selected_movie_name = st.selectbox(
    "🔍 Search Movie",
    sorted(
        movies['title'].values
    )
)

# ==========================
# Recommendation Button
# ==========================
if st.button("Recommend"):

    movie_names, movie_details, movie_ids = recommend(
        selected_movie_name
    )

    for i in range(5):

        st.markdown("---")

        col1, col2 = st.columns(
            [1, 2]
        )

        with col1:

            st.image(
                movie_details[i]["poster"],
                width=250
            )

        with col2:

            st.subheader(
                movie_names[i]
            )

            st.write(
                f"⭐ Rating: {movie_details[i]['rating']}"
            )

            st.write(
                f"📅 Release Date: {movie_details[i]['release_date']}"
            )

            st.write(
                f"🎭 Genres: {movie_details[i]['genres']}"
            )

            st.write(
                f"⏱ Runtime: {movie_details[i]['runtime']} min"
            )

            st.write(
                f"💰 Budget: ${movie_details[i]['budget']:,}"
            )

            st.write(
                f"💵 Revenue: ${movie_details[i]['revenue']:,}"
            )

            cast = fetch_cast(
                movie_ids[i]
            )

            st.write(
                f"🎬 Top Cast: {cast}"
            )

            st.write(
                movie_details[i]["overview"]
            )

            trailer = fetch_trailer(
                movie_ids[i]
            )

            if trailer:

                st.markdown(
                    f"[▶ Watch Trailer]({trailer})"
                )