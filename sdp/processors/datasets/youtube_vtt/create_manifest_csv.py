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

from sdp.processors.base_processor import BaseParallelProcessor, DataEntry


class CreateInitialManifestByExtByCsv(BaseParallelProcessor):
    """
    Processor for creating an initial dataset manifest by saving filepaths that occur in csv file and have a common extension to the field specified in output_field.

    Args:
        raw_data_dir (str): The root directory of the files to be added to the initial manifest. This processor will recursively look for files with the extension 'extension' inside this directory.
        output_file_key (str): The key to store the paths to the files in the dataset.
        extension (str): The key to stecify extension of the files to use them in the dataset.
        **kwargs: Additional keyword arguments to be passed to the base class `BaseParallelProcessor`.

    """

    def __init__(
        self,
        dataset_dir: str,
        csv_file_path: str,
        csv_primary_key: str = "video_id",
        extension: str = "mp3",
        output_manifest_sample_id_key: str = "sample_id",
        output_manifest_result_path_key: str = "audio_filepath",
        save_sample_ids: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dataset_dir = Path(dataset_dir)
        self.csv_file_path = csv_file_path
        self.csv_primary_key = csv_primary_key

        self.extension = extension
        self.save_sample_ids = save_sample_ids

        self.output_manifest_sample_id_key = output_manifest_sample_id_key
        self.output_manifest_result_path_key = output_manifest_result_path_key

    def read_manifest(self):
        sample_ids = pd.read_csv(self.csv_file_path)[self.csv_primary_key]

        return sample_ids

    def process_dataset_entry(self, sample_id):
        result_path = os.path.join(self.dataset_dir, sample_id + "." + self.extension)

        if not (os.path.exists(result_path)):
            return []

        data = {
            self.output_manifest_sample_id_key: sample_id,
            self.output_manifest_result_path_key: result_path,
        }
        return [DataEntry(data=data)]
