import os

from mutagen.mp3 import MP3
from pydub import AudioSegment


def calculate_total_length(directory):
    total_length = 0
    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            file_path = os.path.join(directory, filename)
            audio = MP3(file_path)
            duration = audio.info.length
            total_length += duration
            song = AudioSegment.from_mp3(file_path)
            print(song.frame_rate)
    return total_length


# Directory containing the WAV files
directory_path = "/home/lgrigoryan/datasets/arab_mcv/ar/clips/"

total_length = calculate_total_length(directory_path)
print("Total length of all MP3 files in the directory:", total_length, "seconds")
