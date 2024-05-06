import os
import wave

import librosa


def get_wav_duration(file_path):
    with wave.open(file_path, "rb") as wav_file:
        # Get the duration of the WAV file in seconds
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
        return duration


def calculate_total_length(directory):
    total_length = 0
    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            file_path = os.path.join(directory, filename)
            duration = get_wav_duration(file_path)
            total_length += duration
    return total_length


# Directory containing the WAV files
directory_path = "/home/lgrigoryan/datasets/arab/audios"

total_length = calculate_total_length(directory_path)
print("Total length of all WAV files in the directory:", total_length, "seconds")
