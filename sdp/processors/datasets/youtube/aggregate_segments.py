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

from pydub import AudioSegment

from sdp.processors.base_processor import BaseParallelProcessor
from sdp.processors.datasets.youtube.utils import (
    AggregatedSegment,
    RawSegment,
    get_audio_segment,
)

class AggregateSegments(BaseParallelProcessor):
    def __init__(
        self,
        source_audio_key: str = "audio_filepath",
        splited_audio_key: str = "audio_filepath",
        max_duration: float = 40.0,
        crop_audio_segments: bool = True,
        output_segments_audio_dir: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_duration = max_duration
        self.source_audio_key = source_audio_key
        self.splited_audio_key = splited_audio_key
        self.crop_audio_segments = crop_audio_segments
        self.output_segments_audio_dir = output_segments_audio_dir

    def prepare(self):
        if self.crop_audio_segments and self.output_segments_audio_dir:
            os.makedirs(os.path.join(self.output_segments_audio_dir), exist_ok=True)

    def process_dataset_entry(self, data_entry: dict):
        sample_id = data_entry['sample_id']
        segments = data_entry['segments']
        agg_segments = []

        if len(segments) == 0:
            return agg_segments

        first_segment = RawSegment(**segments[0])
        agg_segment = AggregatedSegment(
            segment=first_segment,
            segment_id=1,
            sample_id=sample_id,
            output_audio_dir=self.output_segments_audio_dir,
            audio_lang=data_entry['audio_lang'],
            text_lang=data_entry['text_lang'],
            source_audio=data_entry[self.source_audio_key],
        )

        for segment in segments[1:]:
            segment = RawSegment(**segment)

            if (
                not agg_segment.duration_match
                or agg_segment.duration >= self.max_duration
                or segment.end_time - agg_segment.start_time >= self.max_duration
            ):
                agg_segments.append(agg_segment.to_dataentry())
                agg_segment = AggregatedSegment(
                    segment=segment,
                    segment_id=len(agg_segments) + 1,
                    sample_id=sample_id,
                    audio_lang=data_entry['audio_lang'],
                    text_lang=data_entry['text_lang'],
                    source_audio=data_entry[self.source_audio_key],
                    output_audio_dir=self.output_segments_audio_dir,
                )
            else:
                agg_segment.aggregate(segment)
        else:
            agg_segments.append(agg_segment.to_dataentry())

        if self.crop_audio_segments:
            audio = AudioSegment.from_wav(data_entry[self.source_audio_key])
            for agg_segment in agg_segments:
                get_audio_segment(
                    audio=audio,
                    start_time=agg_segment.data['start_time'],
                    end_time=agg_segment.data['end_time'],
                    output_audio_filepath=agg_segment.data[self.splited_audio_key],
                )
        return agg_segments
