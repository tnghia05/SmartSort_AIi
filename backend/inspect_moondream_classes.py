"""Utility script to inspect class distribution of moondream/waste_detection dataset."""
from collections import Counter

from datasets import load_dataset


def main():
    print("Downloading dataset metadata (moondream/waste_detection)...")
    dataset = load_dataset("moondream/waste_detection")

    labels_counter = Counter()
    for split in ("train", "test"):
        print(f"Processing split: {split}")
        for record in dataset[split]:
            labels_counter.update(record["labels"])

    print("\nClasses found:", len(labels_counter))
    for label, count in labels_counter.most_common():
        print(f"{label:20} {count}")


if __name__ == "__main__":
    main()

