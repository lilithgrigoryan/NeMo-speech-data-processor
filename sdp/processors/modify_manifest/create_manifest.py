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

import json
from pathlib import Path

import pandas

from sdp.processors.base_processor import (
    BaseParallelProcessor,
    BaseProcessor,
    DataEntry,
)


class CreateInitialManifestByExt(BaseParallelProcessor):
    """
    Processor for creating an initial dataset manifest by saving filepaths with a common extension to the field specified in output_field.

    Args:
        raw_data_dir (str): The root directory of the files to be added to the initial manifest. This processor will recursively look for files with the extension 'extension' inside this directory.
        output_field (str): The field to store the paths to the files in the dataset.
        extension (str): The field stecify extension of the files to use them in the dataset.
        **kwargs: Additional keyword arguments to be passed to the base class `BaseParallelProcessor`.

    """

    def __init__(
        self,
        raw_data_dir: str,
        output_field: str = "audio_filepath",
        extension: str = "mp3",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.raw_data_dir = Path(raw_data_dir)
        self.output_field = output_field
        self.extension = extension

    def read_manifest(self):
        input_files = [str(self.raw_data_dir / file) for file in self.raw_data_dir.rglob('*.' + self.extension)]
        return input_files

    def process_dataset_entry(self, data_entry):
        data = {self.output_field: data_entry}
        return [DataEntry(data=data)]


class CreateCombinedManifests(BaseParallelProcessor):
    def __init__(
        self,
        manifest_list: list[str],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.manifest_list = manifest_list

    def read_manifest(self):
        for file in self.manifest_list:
            with open(file, "rt", encoding="utf8") as fin:
                for line in fin:
                    yield json.loads(line)

    def process_dataset_entry(self, data_entry):
        return [DataEntry(data=data_entry)]


class ExcelToJsonConverter(BaseProcessor):
    def __init__(self, input_excel_file: str, column_keys: list = None, **kwargs):
        super().__init__(**kwargs)
        self.input_excel_file = input_excel_file
        self.column_keys = column_keys if column_keys is not None else []

    def process(self):
        df = pandas.read_excel(self.input_excel_file, header=0)

        if not self.column_keys:
            self.column_keys = list(df.columns)

        if len(self.column_keys) != len(df.columns):
            raise ValueError("The number of provided keys does not match the number of columns in the Excel file.")

        data_entries = []

        for _, row in df.iterrows():
            data_entry = {self.column_keys[i]: row.values[i] for i in range(len(self.column_keys))}
            data_entries.append(data_entry)

        with open(self.output_manifest_file, "wt", encoding='utf-8') as fout:
            for m in data_entries:
                fout.write(json.dumps(m, ensure_ascii=False) + "\n")
