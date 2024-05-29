import os

import pandas as pd

import pyarabic
import pyarabic.araby

import re

remove_puntuation = lambda text: re.sub(r"['?!:;\-.,؟،؛\u06D4]", "", text)
normalize = lambda text: remove_puntuation(pyarabic.araby.strip_diacritics(text))

dataset_split = "train"

dataset_root_dir = "/home/lgrigoryan/datasets/arab_mcv/ar"
dev_dataset_path = os.path.join(dataset_root_dir, "dev.tsv")
test_dataset_path = os.path.join(dataset_root_dir, "test.tsv")
train_dataset_path = os.path.join(dataset_root_dir, "train.tsv")
validated_dataset_path = os.path.join(dataset_root_dir, "validated.tsv")
other_dataset_path = os.path.join(dataset_root_dir, "other.tsv")
validated_sentences_path = os.path.join(dataset_root_dir, "validated_sentences.tsv")

dev_csv = pd.read_csv(dev_dataset_path, sep="\t", low_memory=False)
test_csv = pd.read_csv(test_dataset_path, sep="\t", low_memory=False)
train_csv = pd.read_csv(train_dataset_path, sep="\t", low_memory=False)
validated_csv = pd.read_csv(validated_dataset_path, sep="\t", low_memory=False)
other_csv = pd.read_csv(other_dataset_path, sep="\t", low_memory=False)
validated_sentences = pd.read_csv(validated_sentences_path, sep="\t", low_memory=False)

dev_sentence_ids = set(dev_csv["sentence_id"])
test_sentence_ids = set(test_csv["sentence_id"])
train_sentence_ids = set(train_csv["sentence_id"])
validated_sentence_ids = set(validated_csv["sentence_id"])
other_sentence_ids = set(other_csv["sentence_id"])

validated_sentences["cleaned_sentence"] = validated_sentences['sentence'].apply(normalize)
validated_sentences = validated_sentences.sort("cleaned_sentence")
aggregation_functions = {'sentence_id': ', '.join, 'sentence': 'first', 'sentence_domain': 'first', 'source': 'first', 'is_used': 'first', 'clips_count': sum}
validated_sentences_new = validated_sentences.groupby(validated_sentences['cleaned_sentence']).aggregate(aggregation_functions)
print(validated_sentences_new[:10])

validated_sentences_new.to_csv(
    os.path.join(dataset_root_dir, f"validated_overlap.tsv"), sep="\t"
)

# dev_csv["cleaned_sentence"] = dev_csv['sentence'].apply(normalize)
# test_csv["cleaned_sentence"] = test_csv['sentence'].apply(normalize)   
# train_csv["cleaned_sentence"] = train_csv['sentence'].apply(normalize)   
# validated_csv["cleaned_sentence"] = validated_csv['sentence'].apply(normalize)
# other_csv["cleaned_sentence"] = other_csv['sentence'].apply(normalize)

# train_dev_intersect = pd.merge(train_csv, dev_csv, on='cleaned_sentence', how='inner')
# train_dev_intersect.to_csv(
#     os.path.join(dataset_root_dir, f"train_dev_intersect.tsv"), sep="\t"
# )


# dev_sentence_texts = dict((idx, remove_puntuation(pyarabic.araby.strip_diacritics(validated_sentences.loc[validated_sentences["sentence_id"] == idx]["sentence"].item()))) for idx in dev_sentence_ids)
# test_sentence_texts = dict((idx, remove_puntuation(pyarabic.araby.strip_diacritics(validated_sentences.loc[validated_sentences["sentence_id"] == idx]["sentence"].item()))) for idx in test_sentence_ids)

# unique_val_sentence_ids = []
# print("here")
# dev_id_count = 0
# test_id_count = 0
# for val_sentence_id in validated_sentence_ids:
#     text = validated_sentences[validated_sentences["sentence_id"] == val_sentence_id]["sentence"].item()
#     text = remove_puntuation(pyarabic.araby.strip_diacritics(text))
#     if text in dev_sentence_texts.values() or text in test_sentence_texts.values():
#         dev_ids = []
#         if text in list(dev_sentence_texts.values()):
#             dev_ids = [list(dev_sentence_texts.keys())[list(dev_sentence_texts.values()).index(text)]]
#         test_ids = []
#         if text in list(test_sentence_texts.values()):
#             test_ids = [list(test_sentence_texts.keys())[list(test_sentence_texts.values()).index(text)]]
        
#         for dev_id in dev_ids:
#             if (dev_id != val_sentence_id):
#                 print("dev", validated_sentences[validated_sentences["sentence_id"] == dev_id]["sentence"].item())
#                 print("val", validated_sentences[validated_sentences["sentence_id"] == val_sentence_id]["sentence"].item())
#             # print("Sentence from validated:" + {str(validated_sentences[validated_sentences["sentence_id"] == val_sentence_id]["sentence"].item())} + ", from dev: " + {str(validated_sentences[validated_sentences["sentence_id"] == dev_id]["sentence"].item())})
            
#         for test_id in test_ids:
#             if (test_id != val_sentence_id):
#                 print("test", str(validated_sentences[validated_sentences["sentence_id"] == test_id]["sentence"].item()))
#                 print("vald", str(validated_sentences[validated_sentences["sentence_id"] == val_sentence_id]["sentence"].item()))
#             # print("Sentence from validated:" + {str(validated_sentences[validated_sentences["sentence_id"] == val_sentence_id]["sentence"].item())} +", from test: " + {str(validated_sentences[validated_sentences["sentence_id"] == test_id]["sentence"].item())})

#         dev_id_count += len(dev_ids)
#         test_id_count += len(test_ids)
#     else:
#         unique_val_sentence_ids.append(val_sentence_id)
        
# print(len(unique_val_sentence_ids))
# print(len(validated_csv))
# validated_csv = validated_csv[
#     validated_csv["sentence_id"].isin(unique_val_sentence_ids)
# ]
# print(len(validated_csv))

# validated_csv.to_csv(
#     os.path.join(dataset_root_dir, f"train_from_{dataset_split}_s.tsv"), sep="\t"
# )
