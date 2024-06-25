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
from pathlib import Path

import pandas as pd
import soundfile as sf

from sdp.processors.base_processor import BaseParallelProcessor, DataEntry


class CreateDialectManifest(BaseParallelProcessor):
    def __init__(
        self,
        dataset_audios_dir: str,
        dialect: str,
        csv_filepaths: str,
        original_csv_path: str,
        output_audio_dir: str,
        output_manifest_text_key: str = "text",
        output_manifest_audio_filepath_key: str = "audio_filepath",
        output_manifest_audio_duration: str = "duration",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dataset_audios_dir = Path(dataset_audios_dir)
        self.csv_file_path = csv_filepaths
        self.original_csv_path = original_csv_path
        self.sialect = dialect

        self.output_manifest_text_key = output_manifest_text_key
        self.output_manifest_audio_filepath_key = output_manifest_audio_filepath_key
        self.output_manifest_audio_duration = output_manifest_audio_duration
        self.output_audio_dir = output_audio_dir

    def prepare(self):
        os.makedirs(self.output_audio_dir, exist_ok=True)

    def read_manifest(self):
        dialect_csv = pd.read_csv(self.csv_file_path)
        orig_csv = pd.read_csv(self.original_csv_path)

        return orig_csv[orig_csv["video_id"].isin(dialect_csv["video_id"])].to_dict("records")

    def process_dataset_entry(self, sample_info):
        video_id = sample_info["video_id"]
        audio_path = os.path.join(self.dataset_audios_dir, video_id + ".wav")

        if not (os.path.exists(audio_path)):
            return []

        data, samplerate = sf.read(audio_path)
        start_ms = int(sample_info["start"] * samplerate)
        end_ms = int(sample_info["end"] * samplerate)
        sample_data = data[start_ms:end_ms]

        output_audio_path = os.path.join(self.output_audio_dir, f"{video_id}_{start_ms/1000}_{end_ms/1000}.wav")
        sf.write(output_audio_path, sample_data, samplerate)

        data = {
            self.output_manifest_text_key: sample_info["text"],
            self.output_manifest_audio_filepath_key: output_audio_path,
            self.output_manifest_audio_duration: sample_info["end"] - sample_info["start"],
        }
        return [DataEntry(data=data)]
