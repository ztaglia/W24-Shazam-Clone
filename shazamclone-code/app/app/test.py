from helper import create_constellation_stft, create_hashes
from pydub import AudioSegment
import librosa
import sqlite3
from tqdm import tqdm
import pyaudio
import wave

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

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Start recording...")

frames = []
seconds = 3
for i in range(0, int(RATE / CHUNK * seconds)):
    data = stream.read(CHUNK)
    frames.append(data)

print("recording stopped")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open("output.wav", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

database = {}
with sqlite3.connect('songs.sqlite3') as conn:
    cur = conn.cursor()

    # Change the limit to the number of songs you'd like to extract from your db!
    cur.execute("SELECT hash_val, time_val, song_id FROM hashes WHERE song_id BETWEEN 200 AND 300")

    for hash, source_time, song_index in cur.fetchall():
        if hash not in database:
            database[hash] = []
        database[hash].append((source_time, song_index))

# audio = AudioSegment.from_file("songs/Clint Eastwood.m4a", format="mp4")
# audio.export("songs/clint-eastwood-vm.mp3", format="mp3", bitrate="192k")

Fs, song = librosa.load("output.wav", sr=None)
constellation = create_constellation_stft(song, Fs)
hashes = create_hashes(constellation, None)

scores = score_hashes_against_database(hashes, database)[:5]

with sqlite3.connect('songs.sqlite3') as conn:
    cur = conn.cursor()

    for song_id, score in scores:
        cur.execute("SELECT songname FROM songs WHERE id = ?", (song_id,))
        print(f"{cur.fetchone()[0]}: Score of {score[1]} at {score[0]}")
