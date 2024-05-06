import os
import re
from typing import Dict, List

import webvtt

from sdp.logging import logger
from sdp.processors.base_processor import BaseParallelProcessor, DataEntry


class FilterVttText(BaseParallelProcessor):
    def __init__(
        self,
        regex_params: Dict,
        input_filepath_key: str = "vtt_filepath",
        output_filtered_vtt_dir: str = "filtered_vtt_filepath",
        output_filepath_key: str = "filtered_vtt_filepath",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_filepath_key = input_filepath_key
        self.output_filepath_key = output_filepath_key
        self.output_filtered_vtt_dir = output_filtered_vtt_dir
        self.regex_params = regex_params

    def prepare(self):
        os.makedirs(self.output_filtered_vtt_dir, exist_ok=True)

    def process_dataset_entry(self, data_entry):
        vtt = webvtt.read(data_entry[self.input_filepath_key])

        for caption in vtt:
            caption.text = re.sub(
                pattern=self.regex_params["pattern"],
                repl=self.regex_params["repl"],
                string=caption.text,
                count=self.regex_params.get("count", 0),
            )

        basename = os.path.basename(data_entry[self.input_filepath_key])
        filtered_vtt_filepath = os.path.join(self.output_filtered_vtt_dir, basename)

        vtt.save(filtered_vtt_filepath)
        data_entry[self.output_filepath_key] = filtered_vtt_filepath

        return [DataEntry(data=data_entry)]
