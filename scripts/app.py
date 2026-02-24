from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd

# Initialize the Flask app
app = Flask(__name__)

# Load the trained model
model = joblib.load('fraud_detection_model.pkl')

# Home route to render the form
@app.route('/')
def index():
    return render_template('index.html')

# Prediction API endpoint
@app.route('/predict', methods=['POST'])
def predict():
    # Get JSON data from request
    data = request.get_json()

    # Convert JSON data to DataFrame
    input_data = pd.DataFrame([data])

    # Make prediction
    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)[0]

    # Interpret prediction result
    result = {
        'prediction': 'Fraudulent Transaction' if prediction[0] == 1 else 'Non-Fraudulent Transaction',
        'probability_of_non_fraud': round(probability[0], 2),
        'probability_of_fraud': round(probability[1], 2)
    }

    return jsonify(result)  # Return JSON response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  
    app.run(host='0.0.0.0', port=port)