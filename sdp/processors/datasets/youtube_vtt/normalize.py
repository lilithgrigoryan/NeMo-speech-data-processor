from nemo_text_processing.text_normalization.normalize import Normalizer

from sdp.processors.base_processor import BaseParallelProcessor, DataEntry


class NormalizeNumbers(BaseParallelProcessor):
    def __init__(
        self,
        input_text_key,
        output_text_key,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_text_key = input_text_key
        self.output_text_key = output_text_key

    def prepare(self):
        self.normalizer = Normalizer(input_case="lower_cased", lang="ar")

    def process_dataset_entry(self, data_entry):
        data_entry[self.output_text_key] = self.normalizer.normalize(
            data_entry[self.input_text_key]
        )

        return [DataEntry(data=data_entry)]
