import os

import pandas as pd

dataset_root_dir = "/home/lgrigoryan/datasets/arab_mcv/ar"
dev_dataset_path = os.path.join(dataset_root_dir, "dev.tsv")
test_dataset_path = os.path.join(dataset_root_dir, "test.tsv")
train_dataset_path = os.path.join(dataset_root_dir, "train.tsv")
validated_dataset_path = os.path.join(dataset_root_dir, "validated.tsv")


dev_csv = pd.read_csv(dev_dataset_path, sep="\t", low_memory=False)
test_csv = pd.read_csv(test_dataset_path, sep="\t", low_memory=False)
train_csv = pd.read_csv(train_dataset_path, sep="\t", low_memory=False)
validated_csv = pd.read_csv(validated_dataset_path, sep="\t", low_memory=False)

dev_sentence_ids = set(dev_csv["sentence_id"])
test_sentence_ids = set(test_csv["sentence_id"])
validated_sentence_ids = set(validated_csv["sentence_id"])

print(len(validated_sentence_ids))
validated_sentence_ids.difference_update(dev_sentence_ids)
validated_sentence_ids.difference_update(test_sentence_ids)
print(len(validated_sentence_ids))

print(validated_sentence_ids.intersection(dev_sentence_ids))

print(len(validated_csv))
validated_csv = validated_csv[
    validated_csv["sentence_id"].isin(validated_sentence_ids)
]
print(len(validated_csv))

validated_csv.to_csv(
    os.path.join(dataset_root_dir, "train_from_validated.tsv"), sep="\t"
)
