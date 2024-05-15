import os
from pathlib import Path

import soundfile as sf
from datasets import load_from_disk

from sdp.processors.base_processor import BaseParallelProcessor, DataEntry


class CreateInitialManifestHuggingFace(BaseParallelProcessor):
    """Processor to create initial manifest for HuggingFace dataset.

    Extracts raw HuggingFace dataset and creates an initial manifest
    using the transcripts provided in the raw data.

    Args:
        dataset_name (str): the name of the dataset. E.g., "fka/awesome-chatgpt-prompts"
        raw_data_dir (str): the path to the directory containing the raw data archive file.
            Needs to be manually downloaded from https://commonvoice.mozilla.org/.
        extract_archive_dir (str): directory where the extracted data will be saved.
        resampled_audio_dir (str): directory where the resampled audio will be saved.
        data_split (str): "train", "dev" or "test".
        language_id (str): the ID of the language of the data. E.g., "en", "es", "it", etc.
        already_extracted (bool): if True, we will not try to extract the raw data.
            Defaults to False.
        target_samplerate (int): sample rate (Hz) to use for resampling.
            Defaults to 16000.
        target_nchannels (int): number of channels to create during resampling process.
            Defaults to 1.

    Returns:
        This processor generates an initial manifest file with the following fields::

            {
                "audio_filepath": <path to the audio file>,
                "duration": <duration of the audio in seconds>,
                "text": <transcription (with capitalization and punctuation)>,
            }
    """

    def __init__(
        self,
        raw_dataset_dir: str,
        dataset_dir: str,
        data_split: str,
        target_samplerate: int = 16000,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.raw_dataset_dir = raw_dataset_dir
        self.dataset_dir = dataset_dir
        self.data_split = data_split
        self.target_samplerate = target_samplerate

    def prepare(self):
        """Extracting data (unless already done)."""
        self.audios_dir = os.path.join(self.dataset_dir, "audios")
        os.makedirs(self.dataset_dir, exist_ok=True)
        os.makedirs(self.audios_dir, exist_ok=True)

    def read_manifest(self):
        self.dataset = load_from_disk(dataset_path=self.raw_dataset_dir)
        return range(0, len(self.dataset[self.data_split]))

    def process_dataset_entry(self, data_id):
        sample_data = self.dataset[self.data_split][data_id]
        sample_audio = sample_data["audio"]["array"]
        audio_filepath = os.path.join(self.audios_dir, f"{data_id}.wav")
        sf.write(
            audio_filepath,
            sample_audio,
            self.target_samplerate,
        )
        duration = len(sample_audio) / self.target_samplerate
        text = sample_data["text"]

        return [
            DataEntry(
                data={
                    "audio_filepath": os.path.join("audios", f"{data_id}.wav"),
                    "duration": duration,
                    "text": text,
                }
            )
        ]
