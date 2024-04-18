import json
import os
from pathlib import Path
from typing import Dict, List

import pandas as pd

from sdp.logging import logger
from sdp.processors.base_processor import BaseProcessor
from sdp.utils.common import load_manifest


class MergeTwoManifests(BaseProcessor):
    def __init__(
        self,
        input_manifest_file2: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_manifest_file2 = input_manifest_file2

    def process(self):
        m1 = pd.DataFrame.from_records(load_manifest(Path(self.input_manifest_file)))
        m1['key'] = m1['audio_filepath'].apply(lambda x: os.path.split(x)[1][:11]) # 42595
        
        m2 = pd.DataFrame.from_records(load_manifest(Path(self.input_manifest_file2)))
        m2['key'] = m2['audio_filepath'].apply(lambda x: os.path.split(x)[1][:11]) # 48075
        m3 = m1.merge(m2, on="key") #41079
        with open(self.output_manifest_file, "wt", encoding="utf8") as fout:
            for i, line in m3.iterrows():
                fout.write(json.dumps(dict(line), ensure_ascii=False) + "\n")


