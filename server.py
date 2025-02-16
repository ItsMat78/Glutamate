from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import torch.nn.functional as F

app = Flask(__name__)
CORS(app)

# Load model and tokenizer
model_path = "./sentiment_model"
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


def generate_suggestions(dominant_sentiment, sentiment_values):
    print(f"Generating suggestions for: {dominant_sentiment}")
    print(f"Sentiment values: {sentiment_values}")
    suggestions = []
    positive_diff = sentiment_values['Positive'] - sentiment_values['Negative']
    
    if dominant_sentiment == "Negative":
        if abs(positive_diff) > 20:
            suggestions.append("This sounds quite critical. Consider using more positive language.")
            suggestions.append("Try adding constructive feedback along with the criticism.")
        else:
            suggestions.append("The tone is leaning negative. Maybe soften strong words.")
        
        suggestions.append("Use 'I' statements to make it less confrontational (e.g., 'I suggest...').")
        suggestions.append("Include positive aspects to balance the feedback.")
        
    elif dominant_sentiment == "Positive":
        if sentiment_values['Positive'] > 70:
            suggestions.append("Great positivity! Consider adding specific examples to reinforce it.")
        else:
            suggestions.append("The tone is good! Maybe emphasize key positive points.")
        
        suggestions.append("Use enthusiastic words like 'excellent' or 'wonderful' to boost positivity.")
        suggestions.append("Add relevant emojis to enhance the positive tone 😊")
        
    else:  # Neutral
        if sentiment_values['Neutral'] > 70:
            suggestions.append("This is very neutral. Add some emotional context.")
            suggestions.append("Consider including both positive and constructive elements.")
        else:
            suggestions.append("The tone is balanced. Add specific details to engage readers.")
        
        suggestions.append("Use descriptive language to convey clearer sentiment.")
        suggestions.append("Include both strengths and areas for improvement.")
    
    print(f"Generated suggestions: {suggestions}")
    return suggestions


def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        output = model(**inputs)

    logits = output.logits
    probabilities = F.softmax(logits, dim=1)

    negative_percent = probabilities[0][0].item() * 100
    positive_percent = probabilities[0][1].item() * 100

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

    sentiment_values = {
        "Positive": positive_percent,
        "Negative": negative_percent,
        "Neutral": neutral_percent
    }
    
    dominant = max(
        sentiment_values,
        key=lambda k: sentiment_values[k]
    )
    
    suggestions = generate_suggestions(dominant, sentiment_values)

    return {
        "Positive": round(positive_percent, 2),
        "Negative": round(negative_percent, 2),
        "Neutral": round(neutral_percent, 2),
        "suggestions": suggestions
    }


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        sentiment = predict_sentiment(text)
        return jsonify(sentiment)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)