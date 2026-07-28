from datasets import load_dataset
import os

dataset = load_dataset(
    "rogue-security/prompt-injections-benchmark",
    token=os.getenv("HF_TOKEN")
)

# Create train/test split
dataset = dataset["test"]

dataset = dataset.train_test_split(
    test_size=0.2,
    seed=42
)

train_dataset = dataset["train"]
test_dataset = dataset["test"]