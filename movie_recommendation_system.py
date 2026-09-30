"""
Personalized Movie Recommendation System Based on User Preferences and Rating Analysis
This system recommends movies using collaborative filtering and content-based approaches.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. GENERATE SYNTHETIC MOVIE AND USER RATING DATASET
# ============================================================================

def generate_movie_dataset(n_movies=500, n_users=200, sparsity=0.8, random_state=42):
    """
    Generate synthetic movie dataset with user ratings
    """
    np.random.seed(random_state)
    
    # Generate movies
    genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'Animation']
    languages = ['English', 'Hindi', 'Spanish', 'French', 'German', 'Japanese']
    
    movies = {
        'Movie_ID': range(1, n_movies + 1),
        'Title': [f'Movie_{i}' for i in range(1, n_movies + 1)],
        'Genre': np.random.choice(genres, n_movies),
        'Language': np.random.choice(languages, n_movies),
        'Release_Year': np.random.randint(2000, 2024, n_movies),
        'Duration_Minutes': np.random.randint(80, 180, n_movies),
        'Budget_Million': np.random.uniform(5, 300, n_movies),
        'IMDb_Score': np.random.uniform(3.0, 9.5, n_movies),
        'Popularity_Score': np.random.uniform(1, 100, n_movies),
        'Viewer_Count': np.random.randint(1000, 1000000, n_movies)
    }
    
    movies_df = pd.DataFrame(movies)
    
    # Generate user-movie ratings matrix
    n_ratings = int(n_movies * n_users * (1 - sparsity))
    
    ratings_data = {
        'User_ID': np.random.randint(1, n_users + 1, n_ratings),
        'Movie_ID': np.random.randint(1, n_movies + 1, n_ratings),
        'Rating': np.random.choice([1, 2, 3, 4, 5], n_ratings, p=[0.05, 0.1, 0.2, 0.3, 0.35])
    }
    
    ratings_df = pd.DataFrame(ratings_data)
    ratings_df = ratings_df.drop_duplicates(subset=['User_ID', 'Movie_ID'])
    
    return movies_df, ratings_df

# ============================================================================
# 2. DATA EXPLORATION AND ANALYSIS
# ============================================================================

def explore_movie_data(movies_df, ratings_df):
    """
    Perform exploratory data analysis on movie dataset
    """
    print("=" * 80)
    print("MOVIE RECOMMENDATION SYSTEM - DATASET OVERVIEW")
    print("=" * 80)
    
    print(f"\nTotal Movies: {len(movies_df)}")
    print(f"Total Users: {ratings_df['User_ID'].nunique()}")
    print(f"Total Ratings: {len(ratings_df)}")
    print(f"Sparsity: {1 - (len(ratings_df) / (len(movies_df) * ratings_df['User_ID'].nunique())):.2%}")
    
    print("\n" + "=" * 80)
    print("RATING STATISTICS")
    print("=" * 80)
    print(f"Average Rating: {ratings_df['Rating'].mean():.2f}")
    print(f"Median Rating: {ratings_df['Rating'].median():.2f}")
    print(f"Std Dev: {ratings_df['Rating'].std():.2f}")
    print(f"Min Rating: {ratings_df['Rating'].min()}")
    print(f"Max Rating: {ratings_df['Rating'].max()}")
    
    print("\n" + "=" * 80)
    print("MOVIE STATISTICS")
    print("=" * 80)
    print(f"Average IMDb Score: {movies_df['IMDb_Score'].mean():.2f}")
    print(f"Average Popularity: {movies_df['Popularity_Score'].mean():.2f}")
    print(f"Average Duration: {movies_df['Duration_Minutes'].mean():.0f} minutes")
    
    print("\n" + "=" * 80)
    print("GENRE DISTRIBUTION")
    print("=" * 80)
    print(movies_df['Genre'].value_counts())
    
    print("\n" + "=" * 80)
    print("LANGUAGE DISTRIBUTION")
    print("=" * 80)
    print(movies_df['Language'].value_counts())

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def create_rating_distribution_plot(ratings_df):
    """
    Create visualization of rating distribution
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Rating histogram
    rating_counts = ratings_df['Rating'].value_counts().sort_index()
    ax1.bar(rating_counts.index, rating_counts.values, color='steelblue', alpha=0.8, edgecolor='black')
    ax1.set_title('Distribution of User Ratings', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Rating')
    ax1.set_ylabel('Frequency')
    ax1.set_xticks([1, 2, 3, 4, 5])
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie chart
    colors = ['#ff6b6b', '#ffa500', '#ffd700', '#90ee90', '#00aa00']
    ax2.pie(rating_counts.values, labels=rating_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    ax2.set_title('Rating Distribution Percentage', fontweight='bold', fontsize=12)
    
    plt.suptitle('User Rating Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/rating_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Rating distribution plot saved")
    plt.close()

def create_genre_popularity_plot(movies_df):
    """
    Create visualization of genre popularity
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Genre count
    genre_counts = movies_df['Genre'].value_counts()
    ax1.barh(genre_counts.index, genre_counts.values, color='coral', alpha=0.8, edgecolor='black')
    ax1.set_title('Number of Movies by Genre', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Count')
    ax1.grid(axis='x', alpha=0.3)
    
    # Average IMDb score by genre
    genre_imdb = movies_df.groupby('Genre')['IMDb_Score'].mean().sort_values()
    ax2.barh(genre_imdb.index, genre_imdb.values, color='lightgreen', alpha=0.8, edgecolor='black')
    ax2.set_title('Average IMDb Score by Genre', fontweight='bold', fontsize=12)
    ax2.set_xlabel('Average IMDb Score')
    ax2.grid(axis='x', alpha=0.3)
    
    plt.suptitle('Genre Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/genre_popularity.png', dpi=300, bbox_inches='tight')
    print("✓ Genre popularity plot saved")
    plt.close()

def create_movie_quality_plot(movies_df):
    """
    Create visualization of movie quality metrics
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Movie Quality and Popularity Metrics', fontsize=14, fontweight='bold')
    
    # IMDb Score distribution
    axes[0, 0].hist(movies_df['IMDb_Score'], bins=30, color='steelblue', alpha=0.8, edgecolor='black')
    axes[0, 0].set_title('IMDb Score Distribution', fontweight='bold')
    axes[0, 0].set_xlabel('IMDb Score')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Popularity distribution
    axes[0, 1].hist(movies_df['Popularity_Score'], bins=30, color='coral', alpha=0.8, edgecolor='black')
    axes[0, 1].set_title('Popularity Score Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('Popularity Score')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Duration distribution
    axes[1, 0].hist(movies_df['Duration_Minutes'], bins=30, color='lightgreen', alpha=0.8, edgecolor='black')
    axes[1, 0].set_title('Movie Duration Distribution', fontweight='bold')
    axes[1, 0].set_xlabel('Duration (Minutes)')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Release year distribution
    axes[1, 1].hist(movies_df['Release_Year'], bins=20, color='orange', alpha=0.8, edgecolor='black')
    axes[1, 1].set_title('Release Year Distribution', fontweight='bold')
    axes[1, 1].set_xlabel('Release Year')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/movie_quality_metrics.png', dpi=300, bbox_inches='tight')
    print("✓ Movie quality metrics plot saved")
    plt.close()

def create_user_activity_plot(ratings_df):
    """
    Create visualization of user activity patterns
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Ratings per user
    user_ratings = ratings_df.groupby('User_ID').size()
    ax1.hist(user_ratings, bins=30, color='steelblue', alpha=0.8, edgecolor='black')
    ax1.set_title('Ratings per User Distribution', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Number of Ratings')
    ax1.set_ylabel('Number of Users')
    ax1.grid(axis='y', alpha=0.3)
    
    # Average rating by user
    user_avg_ratings = ratings_df.groupby('User_ID')['Rating'].mean()
    ax2.hist(user_avg_ratings, bins=30, color='coral', alpha=0.8, edgecolor='black')
    ax2.set_title('Average Rating per User Distribution', fontweight='bold', fontsize=12)
    ax2.set_xlabel('Average Rating')
    ax2.set_ylabel('Number of Users')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.suptitle('User Activity Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/user_activity.png', dpi=300, bbox_inches='tight')
    print("✓ User activity plot saved")
    plt.close()

def create_correlation_plot(movies_df):
    """
    Create correlation heatmap for movie features
    """
    plt.figure(figsize=(10, 8))
    
    numeric_cols = ['Release_Year', 'Duration_Minutes', 'Budget_Million', 'IMDb_Score', 'Popularity_Score', 'Viewer_Count']
    corr_matrix = movies_df[numeric_cols].corr()
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    
    plt.title('Correlation Matrix: Movie Features', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/movie_correlation.png', dpi=300, bbox_inches='tight')
    print("✓ Movie correlation plot saved")
    plt.close()

def create_recommendation_performance_plot(results):
    """
    Create bar chart comparing recommendation algorithm performance
    """
    algorithms = list(results.keys())
    mae_scores = [results[algo]['MAE'] for algo in algorithms]
    rmse_scores = [results[algo]['RMSE'] for algo in algorithms]
    precision_scores = [results[algo]['Precision'] for algo in algorithms]
    
    x = np.arange(len(algorithms))
    width = 0.25
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Error metrics
    ax1.bar(x - width, mae_scores, width, label='MAE', alpha=0.8, edgecolor='black')
    ax1.bar(x, rmse_scores, width, label='RMSE', alpha=0.8, edgecolor='black')
    ax1.set_title('Recommendation Error Metrics', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Error')
    ax1.set_xticks(x)
    ax1.set_xticklabels(algorithms, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Precision scores
    ax2.bar(algorithms, precision_scores, color='steelblue', alpha=0.8, edgecolor='black')
    ax2.set_title('Recommendation Precision Scores', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Precision')
    ax2.set_ylim([0, 1.1])
    ax2.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Recommendation Algorithm Performance', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/recommendation_performance.png', dpi=300, bbox_inches='tight')
    print("✓ Recommendation performance plot saved")
    plt.close()

def create_similarity_heatmap(similarity_matrix, title='User Similarity Matrix'):
    """
    Create similarity heatmap visualization
    """
    plt.figure(figsize=(10, 8))
    
    # Sample subset for visualization
    sample_size = min(20, similarity_matrix.shape[0])
    sample_matrix = similarity_matrix[:sample_size, :sample_size]
    
    sns.heatmap(sample_matrix, cmap='YlOrRd', square=True, linewidths=0.5,
                cbar_kws={"shrink": 0.8})
    
    plt.title(f'{title} (Sample)', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('User ID')
    plt.ylabel('User ID')
    plt.tight_layout()
    plt.savefig(f'/home/ubuntu/{title.lower().replace(" ", "_")}.png', dpi=300, bbox_inches='tight')
    print(f"✓ {title} plot saved")
    plt.close()

# ============================================================================
# 4. RECOMMENDATION ALGORITHMS
# ============================================================================

class MovieRecommender:
    """
    Comprehensive movie recommendation system using multiple algorithms
    """
    
    def __init__(self, movies_df, ratings_df):
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        self.create_rating_matrix()
        
    def create_rating_matrix(self):
        """Create user-movie rating matrix"""
        self.rating_matrix = self.ratings_df.pivot_table(
            index='User_ID',
            columns='Movie_ID',
            values='Rating',
            fill_value=0
        )
        
    def collaborative_filtering(self, user_id, n_recommendations=5):
        """
        User-based collaborative filtering recommendation
        """
        # Calculate user similarity using cosine similarity
        user_similarity = cosine_similarity(self.rating_matrix)
        user_idx = user_id - 1
        
        # Get similar users
        similar_users = user_similarity[user_idx].argsort()[::-1][1:11]
        
        # Get movies rated by similar users but not by target user
        target_user_movies = set(np.where(self.rating_matrix.iloc[user_idx].values != 0)[0])
        recommendations = {}
        
        for sim_user_idx in similar_users:
            sim_user_movies = set(np.where(self.rating_matrix.iloc[sim_user_idx].values != 0)[0])
            new_movies = sim_user_movies - target_user_movies
            
            for movie_idx in new_movies:
                rating = self.rating_matrix.iloc[sim_user_idx, movie_idx]
                similarity = user_similarity[user_idx, sim_user_idx]
                
                if movie_idx not in recommendations:
                    recommendations[movie_idx] = []
                recommendations[movie_idx].append(rating * similarity)
        
        # Score recommendations
        scored_recommendations = {
            movie_idx: np.mean(scores)
            for movie_idx, scores in recommendations.items()
        }
        
        # Return top N
        top_movies = sorted(scored_recommendations.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        return [movie_idx + 1 for movie_idx, _ in top_movies]
    
    def content_based_filtering(self, movie_id, n_recommendations=5):
        """
        Content-based recommendation using movie features
        """
        # Extract numeric features
        numeric_cols = ['Duration_Minutes', 'Budget_Million', 'IMDb_Score', 'Popularity_Score']
        features = self.movies_df[numeric_cols].values
        
        # Normalize features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)
        
        # Calculate similarity
        similarity = cosine_similarity(features_normalized)
        movie_idx = movie_id - 1
        
        # Get similar movies
        similar_movies = similarity[movie_idx].argsort()[::-1][1:n_recommendations+1]
        return [movie_idx + 1 for movie_idx in similar_movies]
    
    def hybrid_recommendation(self, user_id, movie_id, n_recommendations=5):
        """
        Hybrid recommendation combining collaborative and content-based
        """
        collab_recs = set(self.collaborative_filtering(user_id, n_recommendations))
        content_recs = set(self.content_based_filtering(movie_id, n_recommendations))
        
        # Combine recommendations
        hybrid_recs = list(collab_recs.union(content_recs))[:n_recommendations]
        return hybrid_recs
    
    def evaluate_recommendations(self, test_user_id):
        """
        Evaluate recommendation quality
        """
        # Get actual ratings for test user
        user_ratings = self.ratings_df[self.ratings_df['User_ID'] == test_user_id]
        
        if len(user_ratings) == 0:
            return None
        
        # Get recommendations
        recommendations = self.collaborative_filtering(test_user_id, n_recommendations=10)
        
        # Calculate metrics
        actual_ratings = user_ratings['Rating'].values
        predicted_ratings = [self.rating_matrix.loc[test_user_id, movie_id] 
                            if movie_id in self.rating_matrix.columns 
                            else 3.0 for movie_id in recommendations]
        
        mae = mean_absolute_error(actual_ratings[:len(predicted_ratings)], predicted_ratings)
        rmse = np.sqrt(mean_squared_error(actual_ratings[:len(predicted_ratings)], predicted_ratings))
        
        # Calculate precision (recommended movies with rating >= 4)
        precision = sum(1 for r in predicted_ratings if r >= 4) / len(predicted_ratings) if predicted_ratings else 0
        
        return {
            'MAE': mae,
            'RMSE': rmse,
            'Precision': precision
        }

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    print("\n" + "=" * 80)
    print("PERSONALIZED MOVIE RECOMMENDATION SYSTEM")
    print("=" * 80)
    
    # Generate dataset
    print("\n[Step 1] Generating Movie and User Rating Dataset...")
    movies_df, ratings_df = generate_movie_dataset(n_movies=500, n_users=200, sparsity=0.85)
    print(f"✓ Dataset generated with {len(movies_df)} movies and {ratings_df['User_ID'].nunique()} users")
    
    # Explore data
    print("\n[Step 2] Exploring Movie Dataset...")
    explore_movie_data(movies_df, ratings_df)
    
    # Generate visualizations
    print("\n[Step 3] Generating Visualizations...")
    print("Creating rating distribution plot...")
    create_rating_distribution_plot(ratings_df)
    
    print("Creating genre popularity plot...")
    create_genre_popularity_plot(movies_df)
    
    print("Creating movie quality metrics plot...")
    create_movie_quality_plot(movies_df)
    
    print("Creating user activity plot...")
    create_user_activity_plot(ratings_df)
    
    print("Creating movie correlation plot...")
    create_correlation_plot(movies_df)
    
    # Initialize recommender
    print("\n[Step 4] Training Recommendation Algorithms...")
    recommender = MovieRecommender(movies_df, ratings_df)
    
    # Evaluate algorithms
    print("\n[Step 5] Evaluating Recommendation Algorithms...")
    results = {}
    
    for algo_name in ['Collaborative Filtering', 'Content-Based Filtering', 'Hybrid Approach']:
        scores = []
        for user_id in range(1, min(21, ratings_df['User_ID'].nunique() + 1)):
            eval_result = recommender.evaluate_recommendations(user_id)
            if eval_result:
                scores.append(eval_result)
        
        if scores:
            avg_mae = np.mean([s['MAE'] for s in scores])
            avg_rmse = np.mean([s['RMSE'] for s in scores])
            avg_precision = np.mean([s['Precision'] for s in scores])
            
            results[algo_name] = {
                'MAE': avg_mae,
                'RMSE': avg_rmse,
                'Precision': avg_precision
            }
            
            print(f"\n{algo_name}:")
            print(f"  MAE: {avg_mae:.4f}")
            print(f"  RMSE: {avg_rmse:.4f}")
            print(f"  Precision: {avg_precision:.4f}")
    
    print("\nCreating recommendation performance plot...")
    create_recommendation_performance_plot(results)
    
    # Create similarity heatmap
    print("Creating user similarity heatmap...")
    user_similarity = cosine_similarity(recommender.rating_matrix)
    create_similarity_heatmap(user_similarity, 'User Similarity Matrix')
    
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nGenerated Visualizations:")
    print("  1. rating_distribution.png")
    print("  2. genre_popularity.png")
    print("  3. movie_quality_metrics.png")
    print("  4. user_activity.png")
    print("  5. movie_correlation.png")
    print("  6. recommendation_performance.png")
    print("  7. user_similarity_matrix.png")
    
    return movies_df, ratings_df, recommender, results

if __name__ == "__main__":
    movies_df, ratings_df, recommender, results = main()
