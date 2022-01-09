import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=9ed714e432cc3acec94db293d3b2b20c&language=en-US'.format(movie_id))
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']

def recommend(item):
    movie_index = movie[movie['title']==item].index[0]
    distances = sim[movie_index]
    movies_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
    
    result = []
    result_posters = []
    for i in movies_list:
        movie_id = movie.iloc[i[0]].movie_id
        
        result.append(movie.iloc[i[0]].title)
        #Fetch poster from API
        result_posters.append(fetch_poster(movie_id))
    return result, result_posters
movies_list = pickle.load(open('movies_dict.pkl','rb'))
movie = pd.DataFrame(movies_list)

sim = pickle.load(open('sim.pkl','rb'))
st.title('Movie Recommender')

sel_movie  =st.selectbox(
'How would you like to be contacted?',
movie['title'].values)

if st.button('Recommend'):
    names,posters = recommend(sel_movie)
    col1, col2, col3, col4, col5 = st.beta_columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])