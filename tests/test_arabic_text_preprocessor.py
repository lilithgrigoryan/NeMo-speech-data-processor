# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
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

import pytest

from sdp.processors.datasets.youtube_vtt import ArabicTextPreprocessor

test_params_list = []

test_params_list.extend(
    [
        (
            {
                "input_text_key": "text",
                "output_text_key": "text",
                "remove_extra_spaces": True,
                "remove_empty_lines": True,
                "remove_diacritics": True,
            },
            {"text": "بَسْمَلَة"},
            {"text": "بسملة"},
        ),
        (
            {
                "input_text_key": "text",
                "output_text_key": "text",
                "remove_extra_spaces": True,
                "remove_empty_lines": True,
                "remove_punctuation": True,
            },
            {"text": "تمتلئ الحياة بالمفاجآت، فلنجعل كل لحظة تستحق العيش."},
            {"text": "تمتلئ الحياة بالمفاجآت فلنجعل كل لحظة تستحق العيش"},
        ),
        (
            {
                "input_text_key": "text",
                "output_text_key": "text",
                "remove_extra_spaces": True,
                "remove_empty_lines": True,
                "remove_tatweel": True,
            },
            {"text": "قــراءة"},
            {"text": "قراءة"},
        ),
        (
            {
                "input_text_key": "text",
                "output_text_key": "text",
                "remove_extra_spaces": True,
                "remove_empty_lines": True,
                "normalize": True,
            },
            {"text": "\uFEF7 \uFEF9 \uFEF5 \uFEFB"},
            {"text": "\u0644\u0627 \u0644\u0627 \u0644\u0627 \u0644\u0627"},
        ),
        (
            {
                "input_text_key": "text",
                "output_text_key": "text",
                "remove_extra_spaces": True,
                "remove_empty_lines": True,
                "normalize": True,
            },
            {"text": "أمل إنسان آدم"},
            {"text": "امل انسان ادم"},
        ),
        (
            {
                "input_text_key": "text",
                "output_text_key": "text",
                "remove_extra_spaces": True,
                "remove_empty_lines": True,
                "normalize": True,
            },
            {"text": "كتابة"},
            {"text": "كتابه"},
        ),
    ]
)


@pytest.mark.parametrize(
    "class_kwargs,test_input,expected_output", test_params_list, ids=str
)
def test_normalize_text(class_kwargs, test_input, expected_output):
    processor = ArabicTextPreprocessor(**class_kwargs, output_manifest_file=None)
    processor.prepare()

    print(test_input)
    output = processor.process_dataset_entry(test_input)[0].data

    assert output == expected_output