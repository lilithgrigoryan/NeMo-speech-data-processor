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


from sdp.processors.base_processor import BaseParallelProcessor, DataEntry

class CheckIfSentenceIsFromQuran(BaseParallelProcessor):
    """
    Processor for validating bracket segments appear in right order.

    Args:
        raw_data_dir (str): The root directory of the files to be added to the initial manifest. This processor will recursively look for files with the extension 'extension' inside this directory.
        output_file_key (str): The key to store the paths to the files in the dataset.
        extension (str): The key to stecify extension of the files to use them in the dataset.
        **kwargs: Additional keyword arguments to be passed to the base class `BaseParallelProcessor`.

    """

    def __init__(
        self,
        input_text_key: str = "text",
        output_key: str = "is_valid",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_text_key = input_text_key
        self.output_key = output_key

    def process_dataset_entry(self, data_entry):
        text = data_entry[self.input_text_key]
        

        return [DataEntry(data=data_entry)]