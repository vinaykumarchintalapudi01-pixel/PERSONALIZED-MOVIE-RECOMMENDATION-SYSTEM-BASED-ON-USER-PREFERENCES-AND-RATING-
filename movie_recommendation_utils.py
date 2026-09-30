"""
Movie Recommendation System Utilities and Dataset Generation
Provides utilities for data preprocessing, feature extraction, and dataset generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MovieDataProcessor:
    """
    Comprehensive movie data processing and feature extraction class
    """
    
    def __init__(self):
        """Initialize the movie data processor"""
        self.genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'Animation']
        self.languages = ['English', 'Hindi', 'Spanish', 'French', 'German', 'Japanese']
        self.current_year = 2024
    
    def calculate_movie_age(self, release_year):
        """Calculate movie age in years"""
        if pd.isna(release_year):
            return np.nan
        return self.current_year - int(release_year)
    
    def calculate_quality_score(self, imdb_score, viewer_count, popularity):
        """Calculate composite quality score"""
        # Normalize components
        imdb_normalized = imdb_score / 10.0  # 0-1
        viewer_normalized = min(viewer_count / 1000000, 1.0)  # 0-1
        popularity_normalized = popularity / 100.0  # 0-1
        
        # Weighted average
        quality_score = (imdb_normalized * 0.5 + 
                        viewer_normalized * 0.3 + 
                        popularity_normalized * 0.2)
        
        return quality_score
    
    def calculate_recommendation_score(self, rating, quality_score, user_preference_match):
        """Calculate final recommendation score"""
        recommendation_score = (rating * 0.5 + 
                              quality_score * 0.3 + 
                              user_preference_match * 0.2)
        return recommendation_score
    
    def categorize_movie_by_rating(self, imdb_score):
        """Categorize movie by IMDb rating"""
        if imdb_score >= 8.0:
            return 'Excellent'
        elif imdb_score >= 7.0:
            return 'Very Good'
        elif imdb_score >= 6.0:
            return 'Good'
        elif imdb_score >= 5.0:
            return 'Average'
        else:
            return 'Poor'
    
    def categorize_movie_by_popularity(self, popularity_score):
        """Categorize movie by popularity"""
        if popularity_score >= 80:
            return 'Blockbuster'
        elif popularity_score >= 60:
            return 'Popular'
        elif popularity_score >= 40:
            return 'Moderate'
        elif popularity_score >= 20:
            return 'Niche'
        else:
            return 'Obscure'
    
    def categorize_movie_by_duration(self, duration_minutes):
        """Categorize movie by duration"""
        if duration_minutes < 90:
            return 'Short'
        elif duration_minutes < 120:
            return 'Standard'
        elif duration_minutes < 150:
            return 'Long'
        else:
            return 'Extended'
    
    def extract_movie_features(self, movie_dict):
        """
        Comprehensive movie feature extraction
        """
        features = {}
        
        # Basic features
        features['movie_id'] = movie_dict.get('movie_id', np.nan)
        features['title'] = movie_dict.get('title', '')
        features['genre'] = movie_dict.get('genre', '')
        features['language'] = movie_dict.get('language', '')
        
        # Temporal features
        release_year = movie_dict.get('release_year', 2020)
        features['release_year'] = release_year
        features['movie_age_years'] = self.calculate_movie_age(release_year)
        features['is_recent'] = int(features['movie_age_years'] <= 3)
        features['is_classic'] = int(features['movie_age_years'] >= 20)
        
        # Quality features
        features['duration_minutes'] = movie_dict.get('duration_minutes', 120)
        features['budget_million'] = movie_dict.get('budget_million', 50)
        features['imdb_score'] = movie_dict.get('imdb_score', 6.0)
        features['popularity_score'] = movie_dict.get('popularity_score', 50)
        features['viewer_count'] = movie_dict.get('viewer_count', 100000)
        
        # Calculated quality score
        quality_score = self.calculate_quality_score(
            features['imdb_score'],
            features['viewer_count'],
            features['popularity_score']
        )
        features['quality_score'] = quality_score
        
        # Categorical features
        features['rating_category'] = self.categorize_movie_by_rating(features['imdb_score'])
        features['popularity_category'] = self.categorize_movie_by_popularity(features['popularity_score'])
        features['duration_category'] = self.categorize_movie_by_duration(features['duration_minutes'])
        
        # Budget efficiency
        features['budget_efficiency'] = features['imdb_score'] / (features['budget_million'] + 1)
        
        # Viewer engagement
        features['viewer_engagement'] = features['viewer_count'] / (features['duration_minutes'] + 1)
        
        return features


class UserPreferenceAnalyzer:
    """
    Analyze user preferences and rating patterns
    """
    
    def __init__(self):
        """Initialize the user preference analyzer"""
        pass
    
    def calculate_user_preference_vector(self, user_ratings_dict):
        """
        Calculate user preference vector based on ratings
        """
        preference_vector = {
            'avg_rating': np.mean(list(user_ratings_dict.values())),
            'rating_variance': np.var(list(user_ratings_dict.values())),
            'total_ratings': len(user_ratings_dict),
            'rating_distribution': {}
        }
        
        # Calculate rating distribution
        for rating in [1, 2, 3, 4, 5]:
            count = sum(1 for r in user_ratings_dict.values() if r == rating)
            preference_vector['rating_distribution'][rating] = count / len(user_ratings_dict)
        
        return preference_vector
    
    def calculate_genre_preference(self, user_movie_ratings, movie_genres):
        """
        Calculate user preference for each genre
        """
        genre_preferences = {}
        
        for movie_id, rating in user_movie_ratings.items():
            if movie_id in movie_genres:
                genre = movie_genres[movie_id]
                if genre not in genre_preferences:
                    genre_preferences[genre] = []
                genre_preferences[genre].append(rating)
        
        # Calculate average rating per genre
        genre_avg_ratings = {
            genre: np.mean(ratings)
            for genre, ratings in genre_preferences.items()
        }
        
        return genre_avg_ratings
    
    def calculate_language_preference(self, user_movie_ratings, movie_languages):
        """
        Calculate user preference for each language
        """
        language_preferences = {}
        
        for movie_id, rating in user_movie_ratings.items():
            if movie_id in movie_languages:
                language = movie_languages[movie_id]
                if language not in language_preferences:
                    language_preferences[language] = []
                language_preferences[language].append(rating)
        
        # Calculate average rating per language
        language_avg_ratings = {
            language: np.mean(ratings)
            for language, ratings in language_preferences.items()
        }
        
        return language_avg_ratings
    
    def identify_user_type(self, avg_rating, total_ratings, rating_variance):
        """
        Identify user type based on rating behavior
        """
        if total_ratings < 10:
            return 'Casual'
        elif avg_rating >= 4.0 and rating_variance < 0.5:
            return 'Selective'
        elif avg_rating <= 3.0 and rating_variance > 1.5:
            return 'Critical'
        elif total_ratings >= 50:
            return 'Power User'
        else:
            return 'Regular'


def generate_sample_movies(n_movies=500, random_state=42):
    """
    Generate sample movie dataset
    """
    processor = MovieDataProcessor()
    np.random.seed(random_state)
    
    movies = []
    
    for i in range(n_movies):
        movie_dict = {
            'movie_id': i + 1,
            'title': f'Movie_{i+1}',
            'genre': np.random.choice(processor.genres),
            'language': np.random.choice(processor.languages),
            'release_year': np.random.randint(2000, 2024),
            'duration_minutes': np.random.randint(80, 180),
            'budget_million': np.random.uniform(5, 300),
            'imdb_score': np.random.uniform(3.0, 9.5),
            'popularity_score': np.random.uniform(1, 100),
            'viewer_count': np.random.randint(1000, 1000000)
        }
        
        # Extract features
        features = processor.extract_movie_features(movie_dict)
        movie_dict.update(features)
        
        movies.append(movie_dict)
    
    return pd.DataFrame(movies)


def generate_sample_user_ratings(n_users=200, n_movies=500, sparsity=0.85, random_state=42):
    """
    Generate sample user rating dataset
    """
    np.random.seed(random_state)
    
    n_ratings = int(n_movies * n_users * (1 - sparsity))
    
    ratings_data = {
        'User_ID': np.random.randint(1, n_users + 1, n_ratings),
        'Movie_ID': np.random.randint(1, n_movies + 1, n_ratings),
        'Rating': np.random.choice([1, 2, 3, 4, 5], n_ratings, p=[0.05, 0.1, 0.2, 0.3, 0.35]),
        'Timestamp': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_ratings)]
    }
    
    ratings_df = pd.DataFrame(ratings_data)
    ratings_df = ratings_df.drop_duplicates(subset=['User_ID', 'Movie_ID'])
    
    return ratings_df


def generate_sample_watchlist(n_users=200, n_movies=500, sparsity=0.95, random_state=42):
    """
    Generate sample user watchlist dataset
    """
    np.random.seed(random_state)
    
    n_watchlist_items = int(n_movies * n_users * (1 - sparsity))
    
    watchlist_data = {
        'User_ID': np.random.randint(1, n_users + 1, n_watchlist_items),
        'Movie_ID': np.random.randint(1, n_movies + 1, n_watchlist_items),
        'Added_Date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_watchlist_items)],
        'Priority': np.random.choice(['High', 'Medium', 'Low'], n_watchlist_items)
    }
    
    watchlist_df = pd.DataFrame(watchlist_data)
    watchlist_df = watchlist_df.drop_duplicates(subset=['User_ID', 'Movie_ID'])
    
    return watchlist_df


def save_datasets(output_dir='/home/ubuntu'):
    """
    Generate and save all sample datasets
    """
    print("Generating sample datasets...")
    
    # Generate movies
    print("  Generating movies dataset...")
    movies_df = generate_sample_movies(n_movies=500)
    movies_path = f'{output_dir}/sample_movies.csv'
    movies_df.to_csv(movies_path, index=False)
    print(f"  ✓ Movies saved to {movies_path}")
    
    # Generate ratings
    print("  Generating ratings dataset...")
    ratings_df = generate_sample_user_ratings(n_users=200, n_movies=500, sparsity=0.85)
    ratings_path = f'{output_dir}/sample_ratings.csv'
    ratings_df.to_csv(ratings_path, index=False)
    print(f"  ✓ Ratings saved to {ratings_path}")
    
    # Generate watchlist
    print("  Generating watchlist dataset...")
    watchlist_df = generate_sample_watchlist(n_users=200, n_movies=500, sparsity=0.95)
    watchlist_path = f'{output_dir}/sample_watchlist.csv'
    watchlist_df.to_csv(watchlist_path, index=False)
    print(f"  ✓ Watchlist saved to {watchlist_path}")
    
    # Print statistics
    print("\nDataset Statistics:")
    print(f"  Movies: {len(movies_df)} records")
    print(f"  Ratings: {len(ratings_df)} records")
    print(f"  Watchlist: {len(watchlist_df)} records")
    print(f"  Unique Users: {ratings_df['User_ID'].nunique()}")
    print(f"  Sparsity: {1 - (len(ratings_df) / (len(movies_df) * ratings_df['User_ID'].nunique())):.2%}")
    
    return movies_df, ratings_df, watchlist_df


if __name__ == '__main__':
    movies_df, ratings_df, watchlist_df = save_datasets()
    
    print("\nMovie Dataset Preview:")
    print(movies_df.head())
    
    print("\nRating Dataset Preview:")
    print(ratings_df.head())
    
    print("\nWatchlist Dataset Preview:")
    print(watchlist_df.head())
    
    print("\nMovie Statistics:")
    print(movies_df.describe())
    
    print("\nGenre Distribution:")
    print(movies_df['genre'].value_counts())
    
    print("\nRating Category Distribution:")
    print(movies_df['rating_category'].value_counts())
