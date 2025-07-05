"""
 ---------------------
| Developed by Ikmal |
 --------------------
         \ (•◡•) /
          \      /
            ——
            |  |
           _|  |_
"""

import time
import requests
import tweepy
import os
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Twitter API credentials
api_key = ""
api_secret = ""
bearer_token = ""
access_token = ""
access_token_secret = ""

client = tweepy.Client(
    bearer_token,
    api_key,
    api_secret,
    access_token,
    access_token_secret
)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Last.fm API key
lastfm_api_key = ""

# File to save previous stats
stats_file = "bi_stats.txt"

def fetch_artist_stats():
    url = f"https://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=B.I&api_key={lastfm_api_key}&format=json"
    response = requests.get(url, verify=False).json()
    artist = response.get("artist", {})
    listeners = int(artist.get("stats", {}).get("listeners", 0))
    playcount = int(artist.get("stats", {}).get("playcount", 0))
    return listeners, playcount

def fetch_album_stats():
    url = (
        f"https://ws.audioscrobbler.com/2.0/"
        f"?method=album.getinfo"
        f"&artist=B%2EI"
        f"&album=WONDERLAND"
        f"&api_key={lastfm_api_key}"
        f"&format=json"
    )
    response = requests.get(url, verify=False).json()
    album = response.get("album", {})
    listeners = int(album.get("listeners", 0))
    playcount = int(album.get("playcount", 0))
    return listeners, playcount

def load_previous_stats():
    if not os.path.exists(stats_file):
        return None
    with open(stats_file, "r") as f:
        lines = f.readlines()
        if len(lines) < 4:
            return None
        return tuple(map(int, lines))

def save_current_stats(artist_l, artist_p, album_l, album_p):
    with open(stats_file, "w") as f:
        f.write(f"{artist_l}\n{artist_p}\n{album_l}\n{album_p}\n")

def build_tweet(artist_dl, artist_dp, album_dl, album_dp, artist_l, artist_p):
    def fmt(n): return f"+{n}" if n > 0 else f"{n}"
    return (
        "📊 B.I Daily Stats\n\n"
        f"🌌 Artist: {fmt(artist_dl)} listeners | {fmt(artist_dp)} plays\n"
        f"💿 WONDERLAND: {fmt(album_dl)} listeners | {fmt(album_dp)} plays\n\n"
        f"Total B.I listeners: {artist_l}\n"
        f"Total B.I plays: {artist_p}\n\n"
        "#BI #WONDERLAND"
    )

def run_bot():
    while True:
        try:
            artist_l, artist_p = fetch_artist_stats()
            album_l, album_p = fetch_album_stats()

            prev = load_previous_stats()

            if prev:
                prev_artist_l, prev_artist_p, prev_album_l, prev_album_p = prev
                delta_artist_l = artist_l - prev_artist_l
                delta_artist_p = artist_p - prev_artist_p
                delta_album_l = album_l - prev_album_l
                delta_album_p = album_p - prev_album_p

                tweet = build_tweet(delta_artist_l, delta_artist_p, delta_album_l, delta_album_p, artist_l, artist_p)
            else:
                tweet = (
                    "📊 B.I Today's Stats\n\n"
                    f"🌌 Artist: {artist_l} listeners | {artist_p} plays\n"
                    f"💿 WONDERLAND: {album_l} listeners | {album_p} plays\n\n"
                    "#BI #WONDERLAND"
                )

            client.create_tweet(text=tweet)
            print(f"Tweet sent:\n{tweet}")

            save_current_stats(artist_l, artist_p, album_l, album_p)

        except Exception as e:
            print(f"[ERROR] {e}")

        # Wait 24 hours
        time.sleep(24 * 60 * 60)

if __name__ == "__main__":
    run_bot()
