import random
import joblib

# Placeholder for a real AI model, change
#remove the 
def load_model():
    """Mock function to load the AI model."""
    print("Loading AI model...")
    # Replace this with actual model loading logic
    loaded_model = joblib.load("random_forest_model.pkl")
    return loaded_model

model = load_model()

def analyze_text(text):
    """Analyze text using the AI model."""
    loaded_model = load_model()#print the prediction
    predict = loaded_model.predict([text])
    # Mock analysis (Replace with actual AI model inference)
    confidence = random.uniform(50, 100)  # Random confidence score for example
    if confidence > 70:
        is_misinformation = True
        message = "Misinformation detected."
    elif confidence < 50:
        is_misinformation = False
        message = "Text appears accurate."
    else:
        is_misinformation = "uncertain"
        message = "Uncertain. Please verify."
    
    return {
        "is_misinformation": is_misinformation,
        "confidence": round(confidence, 2),
        "message": message
    }

def save_feedback(text, user_verdict):
    """Save user feedback for uncertain cases."""
    with open("feedback.csv", "a") as f:
        f.write(f"{text},{user_verdict}\n")
    print("Feedback saved.")
