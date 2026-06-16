import streamlit as st
import pickle
import pandas as pd
import requests

# Placeholder image
PLACEHOLDER = "https://via.placeholder.com/300x450?text=No+Poster"


# Fetch poster from TMDB
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=f0b188273a76c549a4dd8777889cdec2"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return PLACEHOLDER

        data = response.json()

        if data.get("poster_path"):
            return (
                "https://image.tmdb.org/t/p/w500"
                + data["poster_path"]
            )

        return PLACEHOLDER

    except Exception as e:
        print("TMDB Error:", e)
        return PLACEHOLDER


# Recommendation Function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_list:

        movie_row = movies.iloc[i[0]]

        movie_id = movie_row['movie_id']

        recommended_movies.append(
            movie_row['title']
        )

        recommended_movies_posters.append(
            fetch_poster(movie_id)
        )

    return recommended_movies, recommended_movies_posters


# Load Data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Debug
print("Columns:", movies.columns)

# UI
st.title("🎬 MOVIE RECOMMENDATION SYSTEM")

selected_movie_name = st.selectbox(
    "Select a movie",
    movies['title'].values
)

if st.button("Recommend"):

    recommended_movie_names, recommended_movie_posters = recommend(
        selected_movie_name
    )

    cols = st.columns(5)

    for idx, col in enumerate(cols):

        with col:

            st.write(
                recommended_movie_names[idx]
            )

            st.image(
                recommended_movie_posters[idx],
                width="stretch"
            )