from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv
load_dotenv()

# ---------- Playlist URI's ----------
rr = 'spotify:playlist:37i9dQZEVXbeXrGsbZu97Y'
dw = 'spotify:playlist:37i9dQZEVXcGnBTJV7dHN7'
dm1 = 'spotify:playlist:37i9dQZF1E36Bn1AIzrRAZ'


# ---------- Scrape info from playlists ----------
def scraper(playlist):
    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials())

    # response returns JSON-text. First element is the list of items.
    response = spotify.playlist_items(
        playlist_id=playlist, fields='items[0].track')['items']

    result = []
    for item in response:
        if item['track'] == None:
            continue
        else:
            album_artist = item['track']['album']['artists'][0]['name']

            # If multiple artists on track: artists seperated by comma
            if len(item['track']['artists']) > 1:
                artists = []
                for a in item['track']['artists']:
                    artists.append(a['name'])
                artists = ", ".join(artists)
            else:
                artists = album_artist

            title = item['track']['name']
            sp_uri = item['track']['uri']
            playlist_id = 1 if (playlist == rr) else (
                2 if playlist == dw else 3)
            result.append([album_artist, artists, title, sp_uri, playlist_id])

    return result


# ---------- Playlist-data to database ----------
def save_to_db(data):
    try:
        with connect(
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASS"),
            host=os.getenv("MYSQL_HOST"),
            port=os.getenv("MYSQL_PORT"),
            database=os.getenv("MYSQL_DATABASE")
        ) as connection:
            ins_query = """
            INSERT INTO tracks
            (album_artist, artists, title, sp_uri, playlist_id)
            VALUES (%s, %s, %s, %s, %s)
            """

            with connection.cursor() as cursor:
                cursor.executemany(ins_query, data)
                connection.commit()

    except Error as e:
        print(e)


if __name__ == "__main__":
    save_to_db(scraper(rr))
    save_to_db(scraper(dw))
