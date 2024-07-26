from tqdm import tqdm
from app import helper
import sqlite3
import librosa

conn = sqlite3.connect('songs.sqlite3')
cursor = conn.cursor()

# Retrieve song data from the database
cursor.execute("SELECT id, audio_path FROM songs")
song_data = cursor.fetchall()

cursor.execute('''
DROP TABLE IF EXISTS hashes
''')

# Recreate hash table in case you'd like a do-over
cursor.execute('''
CREATE TABLE IF NOT EXISTS hashes(
    hash_val INTEGER,
    time_val INTEGER,
    song_id INTEGER
);
''')
conn.commit()

# Close the connection to the database
conn.close()

# Process each song file
for id, audio_path in tqdm(sorted(song_data)):

    # Read the audio file
    Fs, audio = librosa.load(audio_path)
    
    # Process the audio file and create hashes
    constellation = helper.create_constellation_stft(audio, Fs)
    hashes = helper.create_hashes(constellation, id)

    # Store hashes in SQL database
    with sqlite3.connect('songs.sqlite3') as conn_hashes:
        cur_hashes = conn_hashes.cursor()
        for hash_value, (time, song_id) in hashes.items():
            cur_hashes.execute(
                "INSERT INTO hashes VALUES (?, ?, ?)", 
                (hash_value, time, song_id,)
            )