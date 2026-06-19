import streamlit as st
import pickle
import pandas as pd
import requests

API_KEY = "f0b188273a76c549a4dd8777889cdec2"
PLACEHOLDER = "https://via.placeholder.com/300x450?text=No+Poster"


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
            poster = "https://image.tmdb.org/t/p/w500" + data["poster_path"]

        genres = ", ".join([g["name"] for g in data.get("genres", [])])

        return {
            "poster": poster,
            "rating": data.get("vote_average", "N/A"),
            "release_date": data.get("release_date", "N/A"),
            "overview": data.get("overview", "No overview available."),
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


def fetch_cast(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
        data = requests.get(url, timeout=30).json()
        cast_names = []

        for actor in data.get("cast", [])[:5]:
            cast_names.append(actor["name"])

        return ", ".join(cast_names)
    except:
        return "N/A"


def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
        data = requests.get(url, timeout=30).json()

        for video in data.get("results", []):
            if video["site"] == "YouTube":
                return "https://www.youtube.com/watch?v=" + video["key"]
        return None
    except:
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_details = []
    recommended_ids = []
    recommended_scores = []

    for i in movie_list:
        movie_row = movies.iloc[i[0]]
        movie_id = movie_row['movie_id']

        recommended_movies.append(movie_row['title'])
        recommended_details.append(fetch_movie_details(movie_id))
        recommended_ids.append(movie_id)
        recommended_scores.append(round(i[1] * 100, 2))

    return (
        recommended_movies,
        recommended_details,
        recommended_ids,
        recommended_scores
    )


# Load data files
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit App Configurations
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
h1, h2, h3 {
    color: white;
}
div.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    border: none;
}
div.stButton > button:hover {
    background-color: #ff6b6b;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 MOVIE RECOMMENDATION SYSTEM")

# Trending Section
st.subheader("🔥 Trending Movies")
trending_movies = ["Avatar", "Titanic", "Interstellar", "Inception", "The Dark Knight"]
st.write(" | ".join(trending_movies))
st.markdown("---")

# Genre Buttons Section
st.subheader("🎭 Popular Genres")
g1, g2, g3, g4, g5 = st.columns(5)
with g1:
    st.button("Action")
with g2:
    st.button("Adventure")
with g3:
    st.button("Comedy")
with g4:
    st.button("Sci-Fi")
with g5:
    st.button("Drama")
st.markdown("---")

# Dropdown Selection
selected_movie_name = st.selectbox(
    "🔍 Search Movie",
    sorted(movies['title'].values)
)

# Recommendation Logic Execution
if st.button("Recommend"):
    movie_names, movie_details, movie_ids, scores = recommend(selected_movie_name)

    for i in range(5):
        st.markdown("---")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(movie_details[i]["poster"], width=250)

        with col2:
            st.subheader(movie_names[i])
            st.write(f"🔥 Match Score: {scores[i]}%")
            st.write(f"⭐ Rating: {movie_details[i]['rating']}")
            st.write(f"📅 Release Date: {movie_details[i]['release_date']}")
            st.write(f"🎭 Genres: {movie_details[i]['genres']}")
            st.write(f"⏱ Runtime: {movie_details[i]['runtime']} min")
            st.write(f"💰 Budget: ${movie_details[i]['budget']:,}")
            st.write(f"💵 Revenue: ${movie_details[i]['revenue']:,}")

            cast = fetch_cast(movie_ids[i])
            st.write(f"🎬 Top Cast: {cast}")
            st.write(movie_details[i]["overview"])

            trailer = fetch_trailer(movie_ids[i])
            if trailer:
                st.markdown(f"[▶ Watch Trailer]({trailer})")

st.markdown("---")
st.markdown("### Developed by Teja G 🚀")
