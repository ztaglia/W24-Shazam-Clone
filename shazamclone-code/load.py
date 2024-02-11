import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from io import BytesIO
import requests
import sqlite3
import os

# TODO: Load song file paths (not the files themselves! store those in a directory within shazamclone-code) 
#       and their respective song titles and artist names into songs.db

file_path = None

df = pd.read_csv(file_path)

conn = sqlite3.connect('songs.db')
c = conn.cursor()

for n in range(1):
  songname = # TODO
  artist = # TODO
  mp3_url = # TODO

  # TODO

  # CHANGE FORMAT FROM STEREO TO MONO!

  data = [(songname, artist, wav_audio_path)]

c.executemany(
  "INSERT INTO songs (songname, artist, audio_path) VALUES (?, ?, ?)", 
  data
)

conn.commit()
conn.close()