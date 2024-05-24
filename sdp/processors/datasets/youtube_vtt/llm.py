import json
from pathlib import Path

from sdp.logging import logger
from sdp.processors.base_processor import BaseProcessor, DataEntry
from sdp.utils.common import load_manifest


class ApplyLlama3(BaseProcessor):
    """
    Processor to prompt llm model from HuggingFace.

    Args:
        input_example_manifest (str): Assistent example manifest file.
        example_query_key (str): Field name that contains examples queries.
        example_response_key (str): Field name that contains examples ground truth responses.
        pretrained_model (str): Pretrained model name.
        input_text_key (str): Field name that contains input text.
        message (str): LLM command text.
        torch_dtype (str): Tensor data type. Default to "float16" (as llama3 is trained so).
        output_text_key (str): Key to save result.
    """

    def __init__(
        self,
        input_example_manifest: str,
        example_query_key: str = "text",
        example_response_key: str = "text_pc",
        pretrained_model: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        input_text_key: str = "text",
        message: str = "Add missing punctuation marks. Don't change the words of the text. Keep the text as it is.",
        torch_dtype: str = "float16",
        output_text_key: str = "text_pc",
        **kwargs,
    ):
        super().__init__(**kwargs)
        try:
            import torch
            import transformers
        except:
            raise ImportError("Need to install transformers: pip install accelerate transformers")

        logger.warning("This is an example processor, for demonstration only. Do not use it for production purposes.")
        self.pretrained_model = pretrained_model
        self.example_query_key = example_query_key
        self.example_response_key = example_response_key
        self.input_example_manifest = input_example_manifest
        self.input_text_key = input_text_key
        self.output_text_key = output_text_key
        self.message = message
        if torch_dtype == "float32":
            self.torch_dtype = torch.float32
        elif torch_dtype == "float16":
            self.torch_dtype = torch.float16
        else:
            raise NotImplementedError(torch_dtype + " is not implemented!")

        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.pretrained_model,
            model_kwargs={"torch_dtype": self.torch_dtype},
            device="cuda",
        )

        self.messages = [{"role": "system", "content": self.message}]
        example_manifest = load_manifest(Path(self.input_example_manifest))
        for data_entry in example_manifest:
            self.messages.append({"role": "user", "content": data_entry[self.example_query_key]})
            self.messages.append({"role": "assistant", "content": data_entry[self.example_response_key]})

    def process(self):
        data_entries = load_manifest(Path(self.input_manifest_file))

        with Path(self.output_manifest_file).open("w") as f:
            for data_entry in data_entries:
                messages = self.messages.copy()
                messages.append({"role": "user", "content": data_entry[self.input_text_key]})

                prompt = self.pipeline.tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )

                terminators = [
                    self.pipeline.tokenizer.eos_token_id,
                    self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
                ]

                outputs = self.pipeline(
                    prompt,
                    max_new_tokens=2 * len(data_entry[self.input_text_key]),
                    eos_token_id=terminators,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )

                data_entry[self.output_text_key] = outputs[0]["generated_text"][len(prompt) :]
                f.write(json.dumps(data_entry, ensure_ascii=False) + "\n")
