from flask import Flask, request, jsonify, render_template

app = Flask(__name__)  # Initialize Flask app

# Route to render the main HTML page
@app.route('/')
def index():
    return render_template('index.html')  # Render 'index.html' from the 'templates' folder

# Route to handle text analysis
@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    try:
        # Get JSON data from the request
        data = request.get_json()
        text = data.get('text', '')  # Extract 'text' field from JSON
        
        if not text.strip():
            return jsonify({"error": "No text provided or text is empty"}), 400
        
        # Simple logic to simulate misinformation detection
        if "fake" in text.lower():
            result = {
                "misinformation": True,
                "message": "This text may contain misinformation."
            }
        else:
            result = {
                "misinformation": False,
                "message": "No misinformation detected."
            }
        
        return jsonify(result)  # Return JSON response
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # Enable debugging for development
