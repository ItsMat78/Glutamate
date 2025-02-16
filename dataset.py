# Import required libraries
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

import torch

# Check if GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")  # This will tell you if it's using GPU

# 🚀 Step 1: Load the dataset
print("Loading dataset...")
dataset = load_dataset("imdb")
dataset = dataset["train"].train_test_split(test_size=0.1, train_size=0.5)  # Only 20% of data


# 🚀 Step 2: Tokenize the text (convert words to numbers)
print("Tokenizing dataset...")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def tokenize_data(batch):
    return tokenizer(batch["text"], padding=True, truncation=True)

dataset = dataset.map(tokenize_data, batched=True)
dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"])

# 🚀 Step 3: Load Pre-trained BERT Model
print("Loading BERT model...")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
model.to(device)  # Move model to GPU

# 🚀 Step 4: Training Configuration
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    no_cuda=False  # Ensure CUDA (GPU) is used
)


# 🚀 Step 5: Train the Model
print("Starting training...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)

trainer.train()

# 🚀 Step 6: Save the Trained Model
print("Saving trained model...")
model.save_pretrained("./sentiment_model2")
tokenizer.save_pretrained("./sentiment_model2")

print("🎉 Training complete! Model saved in 'sentiment_model2' folder.")
