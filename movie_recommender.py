import csv
import pandas as pd

# --- PART 1: READING DATA ---

# 1.1
def read_ratings_data(f):
    """
    Reads the ratings file and returns a dictionary.
    Key: movie id (int), Value: list of ratings (float).
    """
    ratings_dict = {}
    with open(f, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            # Auto-detect tab vs comma separation
            parts = line.split('\t') if '\t' in line else line.split(',')
            try:
                user_id = int(parts[0].strip())
                movie_id = int(parts[1].strip())
                rating = float(parts[2].strip())
                if movie_id not in ratings_dict:
                    ratings_dict[movie_id] = []
                ratings_dict[movie_id].append(rating)
            except (ValueError, IndexError):
                continue
    return ratings_dict

# 1.2
def read_movies_data(f):
    """
    Reads a movies text file with high resilience against delimiters and internal commas.
    Returns a pandas DataFrame indexed by movie id, columns: ["title", "year", "genre"].
    """
    data = []
    with open(f, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            # Handle tab-separated files
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    try:
                        m_id = int(parts[0].strip())
                        title = parts[1].strip()
                        year = int(parts[2].strip())
                        genre = parts[3].strip()
                        data.append([m_id, title, year, genre])
                    except ValueError:
                        continue
            # Handle comma-separated files resiliently (even with commas inside titles)
            else:
                parts = line.split(',')
                if len(parts) >= 4:
                    try:
                        m_id = int(parts[0].strip())
                        genre = parts[-1].strip()
                        year = int(parts[-2].strip())
                        # Reconstruct title if it contains commas
                        title = ",".join(parts[1:-2]).strip()
                        if title.startswith('"') and title.endswith('"'):
                            title = title[1:-1].strip()
                        data.append([m_id, title, year, genre])
                    except ValueError:
                        continue
                        
    df = pd.DataFrame(data, columns=['movie_id', 'title', 'year', 'genre'])
    df.set_index('movie_id', inplace=True)
    df.index.name = None  # Clear index name to match clean test outputs
    df.sort_index(inplace=True)
    return df


# --- PART 2: PROCESSING DATA ---

# 2.1
def get_movie(movies_df, movie_id):
    """
    Helper function to extract a single movie row from the DataFrame.
    """
    if movie_id in movies_df.index:
        return movies_df.loc[movie_id]
    return None

# 2.2
def create_genre_dict(movies_df):
    """
    Returns a dictionary with each genre as a key and a list of movie ids as values.
    """
    genre_dict = {}
    for movie_id, row in movies_df.iterrows():
        genre = row['genre']
        if genre not in genre_dict:
            genre_dict[genre] = []
        genre_dict[genre].append(movie_id)
    return genre_dict

# 2.3
def calculate_average_rating(ratings_dict, movies_df): 
    """
    Returns a pandas Series where index is movie id and value is the average rating.
    """
    avg_dict = {}
    for movie_id in movies_df.index:
        if movie_id in ratings_dict and len(ratings_dict[movie_id]) > 0:
            avg_dict[movie_id] = sum(ratings_dict[movie_id]) / len(ratings_dict[movie_id])
        else:
            avg_dict[movie_id] = 0.0
            
    s = pd.Series(avg_dict)
    s.name = 'avg_ratings'
    return s


# --- PART 3: RECOMMENDATION ---

# 3.1
def get_popular_movies(avg_ratings, n=10):
    """
    Returns top n popular movies sorted in descending order by average rating.
    """
    return avg_ratings.sort_values(ascending=False).head(n)

# 3.2
def filter_movies(avg_ratings, thres_rating=3):
    """
    Filters out movies with an average rating below the specified threshold.
    """
    return avg_ratings[avg_ratings >= thres_rating]

# 3.3
def get_popular_in_genre(genre, genre_to_movies, avg_ratings, n=5):
    """
    Returns top n movies within a specific genre, sorted in descending order.
    """
    if genre not in genre_to_movies:
        return pd.Series(dtype=float)
    movie_ids = genre_to_movies[genre]
    genre_ratings = avg_ratings[avg_ratings.index.isin(movie_ids)]
    return genre_ratings.sort_values(ascending=False).head(n)

# 3.4
def get_genre_rating(genre, genre_to_movies, avg_ratings):
    """
    Computes the average rating across all movies belonging to a specified genre.
    """
    if genre not in genre_to_movies:
        return 0.0
    movie_ids = genre_to_movies[genre]
    genre_ratings = avg_ratings[avg_ratings.index.isin(movie_ids)]
    return genre_ratings.mean()

# 3.5
def get_movie_of_the_year(year, avg_ratings, movies_df):
    """
    Returns the title of the movie with the highest average rating released in a given year.
    """
    year_movies = movies_df[movies_df['year'] == year]
    if year_movies.empty:
        return None
    year_ratings = avg_ratings.loc[year_movies.index]
    best_movie_id = year_ratings.idxmax()
    return year_movies.loc[best_movie_id, 'title']


# --- PART 4: USER FOCUSED ---

# 4.1
def read_user_ratings(f):
    """
    Parses ratings file into a dictionary of user preferences.
    Key: user id (int), Value: list of tuples like [(movie_id, rating), ...]
    """
    user_dict = {}
    with open(f, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t') if '\t' in line else line.split(',')
            try:
                user_id = int(parts[0].strip())
                movie_id = int(parts[1].strip())
                rating = float(parts[2].strip())
                if user_id not in user_dict:
                    user_dict[user_id] = []
                user_dict[user_id].append((movie_id, rating))
            except (ValueError, IndexError):
                continue
    return user_dict

# 4.2
def get_user_genre(user_id, user_to_movies, movies_df):
    """
    Determines the favorite genre of a user based on their average rated scores per genre.
    """
    if user_id not in user_to_movies:
        return None
        
    user_ratings = user_to_movies[user_id]
    genre_ratings = {}
    genre_counts = {}
    
    for movie_id, rating in user_ratings:
        if movie_id in movies_df.index:
            genre = movies_df.loc[movie_id, 'genre']
            if genre not in genre_ratings:
                genre_ratings[genre] = 0.0
                genre_counts[genre] = 0
            genre_ratings[genre] += rating
            genre_counts[genre] += 1
            
    if not genre_ratings:
        return None
        
    genre_avgs = {g: genre_ratings[g] / genre_counts[g] for g in genre_ratings}
    return max(genre_avgs, key=genre_avgs.get)

# 4.3
def recommend_movies(user_id, user_to_movies, movies_df, avg_ratings):
    """
    Recommends up to 3 most popular movies within the user's top favorite genre.
    """
    top_genre = get_user_genre(user_id, user_to_movies, movies_df)
    if not top_genre:
        return pd.Series(dtype=float)
        
    genre_movies = movies_df[movies_df['genre'] == top_genre]
    genre_avg_ratings = avg_ratings.loc[genre_movies.index]
    
    recommended = genre_avg_ratings.sort_values(ascending=False).head(3)
    recommended.name = 'avg_ratings'
    return recommended