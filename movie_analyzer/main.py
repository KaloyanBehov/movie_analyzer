import pandas as pd
import logging
from typing import List, Dict
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MovieAnalyzer:
    def __init__(self, metadata_path: str, ratings_path: str, credits_path: str, keywords_path: str, links_path: str):
        self.metadata_path = metadata_path
        self.ratings_path = ratings_path
        self.credits_path = credits_path
        self.keywords_path = keywords_path
        self.links_path = links_path

        self.links_df = None
        self.keywords_df = None
        self.credits_df = None
        self.ratings_df = None
        self.metadata_df = None

    def load_data(self) -> None:

        try:
            self.metadata_df = pd.read_csv(self.metadata_path, low_memory=False)
            self.ratings_df = pd.read_csv(self.ratings_path)
            self.credits_df = pd.read_csv(self.credits_path)
            self.keywords_df = pd.read_csv(self.keywords_path)
            self.links_df = pd.read_csv(self.links_path)
            logger.info("All data loaded successfully")
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            raise
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty CSV file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def unique_movies_count(self) -> int:

        return self.metadata_df['id'].nunique()

    def average_rating(self) -> float:

        return self.ratings_df['rating'].mean()

    def top_rated_movies(self, n: int = 5) -> List[Dict]:

        avg_ratings = self.ratings_df.groupby('movieId')['rating'].mean().reset_index()

        self.metadata_df['id'] = pd.to_numeric(self.metadata_df['id'], errors='coerce')

        top_movies = avg_ratings.merge(self.metadata_df[['id', 'title']], left_on='movieId', right_on='id', how='inner')

        return top_movies.nlargest(n, 'rating')[['title', 'rating']].to_dict('records')

    def movies_per_year(self) -> Dict[int, int]:
        self.metadata_df['release_date'] = pd.to_datetime(self.metadata_df['release_date'], errors='coerce')
        self.metadata_df['release_year'] = self.metadata_df['release_date'].dt.year
        return self.metadata_df['release_year'].value_counts().sort_index().to_dict()

    def movies_per_genre(self) -> Dict[str, int]:
        def parse_genres(genres_str):
            try:
                genres_list = eval(genres_str)
                return [genre['name'] for genre in genres_list]
            except (SyntaxError, TypeError, KeyError):
                return []

        genres = self.metadata_df['genres'].apply(parse_genres).explode()
        return genres.value_counts().to_dict()

    def top_keywords(self, n: int = 10) -> List[Dict]:
        return self.keywords_df['name'].value_counts().nlargest(n).reset_index().rename(
            columns={'index': 'keyword', 'name': 'count'}).to_dict('records')

    def save_to_json(self, output_path: str) -> None:
        try:
            self.metadata_df.to_json(output_path, orient='records')
            logger.info(f"Data saved successfully to {output_path}")
        except Exception as e:
            logger.error(f"Error saving data to JSON: {str(e)}")
            raise


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.join(script_dir, '..', 'data', 'movies_metadata.csv')
    ratings_path = os.path.join(script_dir, '..', 'data', 'ratings_small.csv')
    credits_path = os.path.join(script_dir, '..', 'data', 'credits.csv')
    keywords_path = os.path.join(script_dir, '..', 'data', 'keywords.csv')
    links_path = os.path.join(script_dir, '..', 'data', 'links.csv')

    analyzer = MovieAnalyzer(metadata_path, ratings_path, credits_path, keywords_path, links_path)

    try:
        analyzer.load_data()

        print(f"Number of unique movies: {analyzer.unique_movies_count()}")
        print(f"Average rating: {analyzer.average_rating():.2f}")

        print("\nTop 5 highest rated movies:")
        for movie in analyzer.top_rated_movies():
            print(f"{movie['title']} - {movie['rating']:.2f}")

        print("\nMovies released each year:")
        for year, count in analyzer.movies_per_year().items():
            print(f"{year}: {count}")

        print("\nMovies in each genre:")
        for genre, count in analyzer.movies_per_genre().items():
            print(f"{genre}: {count}")
        json_output_path = os.path.join(script_dir, 'movies_metadata.json')
        analyzer.save_to_json(json_output_path)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
