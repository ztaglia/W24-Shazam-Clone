from helper import create_constellation_stft, create_hashes
from pydub import AudioSegment
import librosa
import sqlite3
from tqdm import tqdm

def score_hashes_against_database(hashes, database):
    matches_per_song = {}
    for hash, (sample_time, _) in tqdm(hashes.items(), desc="Matching hashes", unit="hash"):
        if hash in database:
            matching_occurrences = database[hash]
            for source_time, song_index in matching_occurrences:
                if song_index not in matches_per_song:
                    matches_per_song[song_index] = []
                matches_per_song[song_index].append((hash, sample_time, source_time))

            
    scores = {}
    for song_index, matches in matches_per_song.items():
        song_scores_by_offset = {}
        for hash, sample_time, source_time in matches:
            delta = source_time - sample_time
            if delta not in song_scores_by_offset:
                song_scores_by_offset[delta] = 0
            song_scores_by_offset[delta] += 1
        max = (0, 0)
        for offset, score in song_scores_by_offset.items():
            if score > max[1]:
                max = (offset, score)
        
        scores[song_index] = max

    scores = list(sorted(scores.items(), key=lambda x: x[1][1], reverse=True)) 
    
    return scores

database = {}
with sqlite3.connect('songs.sqlite3') as conn:
    cur = conn.cursor()

    # Change the limit to the number of songs you'd like to extract from your db!
    cur.execute("SELECT hash_val, time_val, song_id FROM hashes WHERE song_id BETWEEN 20 AND 35")

    for hash, source_time, song_index in cur.fetchall():
        if hash not in database:
            database[hash] = []
        database[hash].append((source_time, song_index))
    print(len(database))

audio = AudioSegment.from_file("songs/Clint Eastwood.m4a", format="mp4")
audio.export("songs/clint-eastwood-vm.mp3", format="mp3", bitrate="192k")

Fs, song = librosa.load("songs/clint-eastwood-vm.mp3", sr=None)
constellation = create_constellation_stft(song, Fs)
hashes = create_hashes(constellation, None)

scores = score_hashes_against_database(hashes, database)[:5]

with sqlite3.connect('songs.sqlite3') as conn:
    cur = conn.cursor()

    for song_id, score in scores:
        cur.execute("SELECT songname FROM songs WHERE id = ?", (song_id,))
        print(f"{cur.fetchone()[0]}: Score of {score[1]} at {score[0]}")
