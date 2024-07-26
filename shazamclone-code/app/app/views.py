from app import app

from flask import render_template, request, jsonify

import sqlite3

import librosa

from app import helper

import traceback

import wave

import subprocess

import os

@app.route('/')
def index():
    return render_template('public/home.html')

def is_wav(filename):
    try:
        with wave.open(filename, 'r') as file:
            return True
    except wave.Error as e:
        print("Not a WAV file:", e)
    return False

def convert_to_wav(input_file_path, output_file_path):
    command = ["ffmpeg", "-i", input_file_path, output_file_path]
    subprocess.run(command, check=True)

@app.route('/test', methods=["GET", "POST"])
def test():
    try:
        audio = request.files['audio']
        filename = 'uploaded_audio.webm'
        audio.save(filename)

        if os.path.exists("converted_audio.wav"):
            os.remove("converted_audio.wav")

        convert_to_wav('uploaded_audio.webm', 'converted_audio.wav')  

        database = {}
        with sqlite3.connect('songs.sqlite3') as conn:
            cur = conn.cursor()

            # Change the limit to the number of songs you'd like to extract from your db!
            cur.execute("SELECT hash_val, time_val, song_id FROM hashes WHERE song_id BETWEEN 2700 AND 3000")

            for hash, source_time, song_index in cur.fetchall():
                if hash not in database:
                    database[hash] = []
                database[hash].append((source_time, song_index))

        Fs, song = librosa.load("converted_audio.wav", sr=None)
        constellation = helper.create_constellation_stft(song, Fs)
        hashes = helper.create_hashes(constellation, None)

        scores = helper.score_hashes_against_database(hashes, database)[:5]

        print(scores)

        results = []
        with sqlite3.connect('songs.sqlite3') as conn:
            cur = conn.cursor()

            for song_id, score in scores:
                cur.execute("SELECT songname FROM songs WHERE id = ?", (song_id,))
                result = f"{cur.fetchone()[0]}"
                results.append(result)

        print(results)
        return jsonify(results)
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {str(e)}")

        return jsonify({"error": "An error occurred during processing"}), 500

@app.route('/jukebox')
def jukebox():
    try:
        songs = []
        with sqlite3.connect('songs.sqlite3') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, songname, artist FROM songs WHERE id BETWEEN 2700 AND 3000")
            songs = cur.fetchall()

        return render_template("public/jukebox.html", songs=songs)
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {str(e)}")
        return render_template("public/jukebox.html", songs=[])

@app.route('/about')
def about():
    return render_template("public/about.html")