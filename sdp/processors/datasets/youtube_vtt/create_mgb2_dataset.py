# Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
from pathlib import Path

import soundfile as sf
from camel_tools.utils.charmap import CharMapper

from sdp.processors.base_processor import BaseParallelProcessor, DataEntry


class CreateMGB2Manifest(BaseParallelProcessor):
    def __init__(
        self,
        dataset_dir: str,
        split: str,
        output_audio_dir: str,
        is_buckwalter: bool = False,
        output_manifest_text_key: str = "text",
        output_manifest_audio_filepath_key: str = "audio_filepath",
        output_manifest_audio_duration: str = "duration",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dataset_dir = Path(dataset_dir)
        self.split = split

        self.is_buckwalter = is_buckwalter
        self.output_manifest_text_key = output_manifest_text_key
        self.output_manifest_audio_filepath_key = output_manifest_audio_filepath_key
        self.output_manifest_audio_duration = output_manifest_audio_duration
        self.output_audio_dir = output_audio_dir

        if self.is_buckwalter:
            self.bw2ar = CharMapper.builtin_mapper("bw2ar")

    def prepare(self):
        os.makedirs(self.output_audio_dir, exist_ok=True)

    def read_manifest(self):
        data_entries = {}
        segments_filepath = os.path.join(self.dataset_dir, self.split, "segments.non_overlap_speech")
        texts_filepath = os.path.join(self.dataset_dir, self.split, "text.non_overlap_speech")
        with open(segments_filepath) as segments_file:
            for segment_line in segments_file:
                segment_id, video_id, segment_start, segment_end = segment_line.split()
                data_entries[segment_id] = {
                    "segment_id": segment_id,
                    "video_id": video_id,
                    "segment_start": float(segment_start),
                    "segment_end": float(segment_end),
                }

        with open(texts_filepath) as texts_file:
            for text_line in texts_file:
                segment_id, text = text_line.split(" ", 1)
                text = text.strip()
                if self.is_buckwalter:
                    # some buckwalter encoded text can contain tags such as @@LAT@@some_word_in_roman_script
                    # will keep them as they are @@LAT@@some_word_in_roman_script -> some_word_in_roman_script
                    words = text.split(" ")
                    text = " ".join(
                        [
                            (
                                re.search(r"@@\w+@@(\w+)", word).group(1)
                                if re.fullmatch(r"@@\w+@@\w+", word)
                                else self.bw2ar(word)
                            )
                            for word in words
                        ]
                    )

                if segment_id in data_entries:
                    data_entries[segment_id]["text"] = text

        return data_entries.values()

    def process_dataset_entry(self, sample_info):
        dataset_audios_dir = os.path.join(self.dataset_dir, self.split, "wav")
        segment_id = sample_info["segment_id"]
        video_id = sample_info["video_id"]
        audio_path = os.path.join(dataset_audios_dir, video_id + ".wav")
        if not (os.path.exists(audio_path)):
            return []

        data, samplerate = sf.read(audio_path)
        start_ms = int(sample_info["segment_start"] * samplerate)
        end_ms = int(sample_info["segment_end"] * samplerate)
        sample_data = data[start_ms:end_ms]

        output_audio_path = os.path.join(self.output_audio_dir, f"{segment_id}.wav")
        sf.write(output_audio_path, sample_data, samplerate)

        data = {
            self.output_manifest_text_key: sample_info["text"],
            self.output_manifest_audio_filepath_key: output_audio_path,
            self.output_manifest_audio_duration: sample_info["segment_end"] - sample_info["segment_start"],
        }
        return [DataEntry(data=data)]
