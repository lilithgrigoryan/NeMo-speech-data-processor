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
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from sdp.processors.base_processor import BaseProcessor


class CreateInitialManifestFromAljazeera(BaseProcessor):
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
        **kwargs,
    ):
        super().__init__(**kwargs)

    def get_page_text(self, url):
        texts = []
        response = requests.get(url)
        if response.status_code == 200:
            page_soup = BeautifulSoup(response.content, "html.parser")
            content_div = page_soup.find(class_="wysiwyg wysiwyg--all-content css-1vkfgk0")  # content div

            if content_div:
                for p in content_div.find_all("p"):
                    texts.append(p.getText())

            return texts
        else:
            print("Failed to get page with status: ", response.status_code)

    def remove_pc(self, text):
        print(text)
        return re.sub(r"['?!:;\-.,؟،؛\u06D4]", "", text)

    def process(self):
        news_url = "https://aljazeera.net/rss"
        response = requests.get(news_url)

        texts = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")

            for item in items:
                texts.extend(self.get_page_text(item.link.text))
        else:
            raise RuntimeError(f"Failed to load page: {news_url} with  status code {response.status_code}.")

        Path(self.output_manifest_file).parent.mkdir(exist_ok=True, parents=True)
        with Path(self.output_manifest_file).open("w") as f:
            for text in texts:
                data_entry = {"text_pc": text, "text": self.remove_pc(text)}
                f.write(json.dumps(data_entry, ensure_ascii=False) + "\n")
