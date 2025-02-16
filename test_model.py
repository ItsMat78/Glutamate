from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import torch.nn.functional as F

# Load trained model and tokenizer
model_path = "./sentiment_model"
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Move model to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}  # Move inputs to GPU if available

    with torch.no_grad():
        output = model(**inputs)

    logits = output.logits
    probabilities = F.softmax(logits, dim=1)  # Convert logits to probabilities

    # Extract positive and negative percentages
    negative_percent = probabilities[0][0].item() * 100  # Assuming 1st label is Negative
    positive_percent = probabilities[0][1].item() * 100  # Assuming 2nd label is Positive

    # New way to estimate Neutral: Look at uncertainty between pos & neg
    difference = abs(positive_percent - negative_percent)
    
    if difference < 20:  # Both are close
        neutral_percent = 50 - (difference / 2)
    elif positive_percent < 40 and negative_percent < 40:  # Both are weak
        neutral_percent = 60 - (difference / 2)
    elif positive_percent > 80 or negative_percent > 80:  # One dominates
        neutral_percent = 5
    else:
        neutral_percent = 30 - (difference / 3)
    
    # Ensure values add up to 100%
    total = positive_percent + negative_percent + neutral_percent
    scale_factor = 100 / total
    positive_percent *= scale_factor
    negative_percent *= scale_factor
    neutral_percent *= scale_factor

    # Round values
    positive_percent = round(positive_percent, 2)
    negative_percent = round(negative_percent, 2)
    neutral_percent = round(neutral_percent, 2)

    # Generate a statement based on sentiment analysis
    if positive_percent > 75:
        statement = "This comment is very positive and enthusiastic!"
    elif positive_percent > 50:
        statement = "This comment is generally positive."
    elif negative_percent > 75:
        statement = "This comment is highly negative and critical."
    elif negative_percent > 50:
        statement = "This comment leans towards negativity."
    elif neutral_percent > 40:
        statement = "This comment is quite neutral and balanced."
    else:
        statement = "This comment has mixed emotions."

    return {
        "Positive": positive_percent,
        "Negative": negative_percent,
        "Neutral": neutral_percent,
        "Analysis": statement
    }

# Test with sample comments
test_comments = [
    "I love this video! The content is amazing.",
    "This is the worst thing I have ever seen.",
    "It was okay, nothing special.",
    "Meh, it's not great but not terrible either.",
    "This video changed my life! Best thing ever!"
]

for comment in test_comments:
    result = predict_sentiment(comment)
    print(f"\nComment: {comment}")
    print(f"Positive: {result['Positive']}% | Negative: {result['Negative']}% | Neutral: {result['Neutral']}%")
    print(f"Analysis: {result['Analysis']}")
