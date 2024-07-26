import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from io import BytesIO
import requests
import sqlite3
import os
import random

file_path = '../music-info.csv'

df = pd.read_csv(file_path)

conn = sqlite3.connect('songs.sqlite3')
c = conn.cursor()

# c.execute('''
# DROP TABLE IF EXISTS songs
# ''')
# conn.commit()

# c.execute('''
# CREATE TABLE songs(
#   songname VARCHAR(40) NOT NULL,
#   artist VARCHAR(40) NOT NULL,
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   audio_path TEXT NOT NULL
# );
# ''')
# conn.commit()

data = []
for n in range(500):
  songname = (df.loc[n + 7000, "name"])
  artist = (df.loc[n + 7000, "artist"])
  mp3_url = df.loc[n + 7000, "spotify_preview_url"]
  response = requests.get(mp3_url)
  mp3_data = BytesIO(response.content)
  mp3_audio = AudioSegment.from_file(mp3_data, format='mp3')
  mp3_audio = mp3_audio.set_channels(1)
  audio_filename = '{}-{}.mp3'.format(artist.replace('/', ''), songname.replace('/', ''))
  audio_directory = 'songs'
  audio_path = os.path.join(audio_directory, audio_filename)
  mp3_audio.export(audio_path)

  data.append((songname, artist, audio_path))

c.executemany(
  "INSERT INTO songs (songname, artist, audio_path) VALUES (?, ?, ?)", 
  data
)

conn.commit()
conn.close()
