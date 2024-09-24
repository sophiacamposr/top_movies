import requests
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# Access the TMDb API key from the .env file
tmdb_api_key = os.getenv('TMDB_API_KEY')

if not tmdb_api_key:
    print("Error: TMDb API key not found. Please add it to the .env file.")
else:
    print(f"API Key Loaded: {tmdb_api_key}")

def scrape_movies(url):
    print("Starting to scrape IMDb")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)

        print(f"Response Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"Failed to get the webpage: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape movie titles from IMDb
        movies_list = soup.find_all('h3', class_='ipc-title__text')
        print(f"Number of movies found: {len(movies_list)}")
        
        movies = []
        for item in movies_list[:25]:
            title = item.text.strip()
            clean_title = title.split('. ', 1)[-1]  # Clean title
            print(f"Movie found: {clean_title}")
            movies.append(clean_title)

        return movies
    except Exception as e:
        print(f"An error has occurred: {e}")
        return []

def search_movie_on_tmdb(movie, api_key):
    print(f"Searching for movie: {movie}")
    base_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie}"
    response = requests.get(base_url)
    
    print(f"Search status code for {movie}: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            print(f"Found {movie} on TMDb with ID {data['results'][0]['id']}")
            return data['results'][0]['id']  # Return the first matching movie's ID
        else:
            print(f"No results found for {movie}")
            return None
    else:
        print(f"Failed to search for {movie} (status code: {response.status_code})")
        return None

def get_movie_recommendations(movie_id, api_key):
    print(f"Getting recommendations for movie ID: {movie_id}")
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}"
    response = requests.get(base_url)
    
    print(f"Recommendation status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            recommendations = [rec['title'] for rec in data['results']]
            print(f"Recommendations: {recommendations}")
            return recommendations
        else:
            print("No recommendations found")
            return []
    else:
        print(f"Failed to get recommendations (status code: {response.status_code})")
        return []

def display_movies(movies):
    """Prints a numbered list of movies."""
    print("\nList of Top 25 Movies from IMDb:")
    for index, movie in enumerate(movies, start=1):
        print(f"{index}. {movie}")

def get_user_input(movies):
    """Allows the user to select a movie by number."""
    display_movies(movies)
    
    # Get valid input from user
    while True:
        try:
            user_choice = int(input("\nEnter the number of your favorite movie to get recommendations: "))
            if 1 <= user_choice <= len(movies):
                return movies[user_choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(movies)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("Starting the script")

    # Scrape IMDb Top 25 Movies
    imdb_url = "https://www.imdb.com/list/ls055592025/"
    top_25_movies = scrape_movies(imdb_url)

    if not top_25_movies:
        print("No movies found during scraping.")
        return

    # Ask the user for their favorite movie from the list
    favorite_movie = get_user_input(top_25_movies)
    print(f"\nYou selected: {favorite_movie}")

    # Search for the user's favorite movie on TMDb
    movie_id = search_movie_on_tmdb(favorite_movie, tmdb_api_key)
    
    if movie_id:
        # Get and display recommendations
        recommendations = get_movie_recommendations(movie_id, tmdb_api_key)
        print(f"\nRecommendations for {favorite_movie}: {', '.join(recommendations)}")
    else:
        print(f"Could not find {favorite_movie} on TMDb.")

if __name__ == "__main__":
    main()
