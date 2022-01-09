import pandas as pd
import numpy as np
import nltk
import ast
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
#Importing the data
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

#Visualizing the data
movies.head(1)
credits.head(1)

#We need to work with one dataset, so we merge both dataframes on their common column ['title']
movies = movies.merge(credits, on='title')

#Selecting columns to use for our recommendations

# genres
# id
# keywords
# title
# overview
# cast
# crew

#Creating our final dataframe with the selected features above
movies = movies[['movie_id','title','overview','genres','keywords','cast','crew']]

#Cleaning the data
movies.isnull().sum()

movies.dropna(inplace=True)

movies.duplicated().sum()

#In our data frames the following columns['overview','genres','keywords','cast','crew'] are all string representations of list, using the ast library to ensure simplicity
def convert(obj):
    L = []
    counter =0
    for i in ast.literal_eval(obj):
        if counter !=3:
            L.append(i['name'])
            counter+=1
        else:
            break
    return L

movies.genres = movies.genres.apply(convert)
movies.keywords = movies.keywords.apply(convert)
movies.cast = movies.cast.apply(convert)

#For the crew feature, what we need is the job key in the dictionary with a value of 'Director'

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L
movies['crew'] = movies['crew'].apply(fetch_director)

#More Simplification
movies['overview'] = movies['overview'].apply(lambda x:x.split())
movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ","") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ","") for i in x])
movies['cast'] = movies['genres'].apply(lambda x:[i.replace(" ","") for i in x])
movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ","") for i in x])

#Feature Engineering
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
#Final df
new_df = movies[['movie_id','title','tags']]
new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
new_df.head()

#Summary of the above was, combining all similar features into a single one named tag, which is now in form of text
ps = PorterStemmer()
#Processing the text
def stem(text):
    y = []
    
    for i in text.split():
        y.append(ps.stem(i))
        
    return " ".join(y)
new_df['tags'].apply(stem)

#Building the recommender system
cv = CountVectorizer(max_features = 5000, stop_words = 'english')
vectors = cv.fit_transform(new_df['tags']).toarray()


sim = cosine_similarity(vectors)
sorted_sim = sorted(enumerate(sim[0]),reverse=True,key=lambda x:x[1])
sorted_sim = sorted_sim[1:6]
sorted_sim

def recommend(movie):
    movie_index = new_df[new_df['title']==movie].index[0]
    distances = sim[movie_index]
    movies_list = sorted(enumerate(distances),reverse=True,key=lambda x:x[1])[1:6]
    
    for i in movies_list:
        print(new_df.iloc[i[0]].title)
        
#Converting to pickle file to be used when deploying
pickle.dump(new_df.to_dict(),open('movies_dict.pkl','wb'))
pickle.dump(sim,open('sim.pkl','wb'))