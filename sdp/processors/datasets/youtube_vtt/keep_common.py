import json
import os
from pathlib import Path

import pandas as pd

from sdp.processors.base_processor import BaseProcessor
from sdp.utils.common import load_manifest


class KeepCommon(BaseProcessor):
    def __init__(
        self,
        input_manifest_key1: str,
        input_manifest_key2: str,
        input_manifest_file2: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_manifest_file2 = input_manifest_file2
        self.input_manifest_key1 = input_manifest_key1
        self.input_manifest_key2 = input_manifest_key2

    def process(self):
        m1 = pd.DataFrame.from_records(load_manifest(Path(self.input_manifest_file)))
        m2 = pd.DataFrame.from_records(load_manifest(Path(self.input_manifest_file2)))

        index1 = m1[self.input_manifest_key1]
        index2 = m2[self.input_manifest_key2]
        mask = index1.isin(index2)
        m3 = m1[mask.values]

        print(index1.index.size)
        print(index2.index.size)
        print(m3.index.size)

        with open(self.output_manifest_file, "wt", encoding="utf8") as fout:
            for _, line in m3.iterrows():
                fout.write(json.dumps(dict(line), ensure_ascii=False) + "\n")
