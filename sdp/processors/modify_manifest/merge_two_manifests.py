import json
import os
from pathlib import Path

import pandas as pd

from sdp.processors.base_processor import BaseProcessor
from sdp.utils.common import load_manifest


class MergeTwoManifests(BaseProcessor):
    def __init__(
        self,
        id_key1: str,
        input_manifest_file2: str,
        id_key2: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_manifest_file2 = input_manifest_file2
        self.id_key1 = id_key1
        self.id_key2 = id_key2

    def process(self):
        get_key = lambda x: os.path.split(x)[1].split(".")[0]

        m1 = pd.DataFrame.from_records(load_manifest(Path(self.input_manifest_file)))
        m1["key"] = m1[self.id_key1].apply(lambda x: get_key(x))
        m2 = pd.DataFrame.from_records(load_manifest(Path(self.input_manifest_file2)))
        m2["key"] = m2[self.id_key2].apply(lambda x: get_key(x))

        m3 = m1.merge(m2, on="key")

        with open(self.output_manifest_file, "wt", encoding="utf8") as fout:
            print(self.output_manifest_file)
            for _, line in m3.iterrows():
                fout.write(json.dumps(dict(line), ensure_ascii=False) + "\n")
