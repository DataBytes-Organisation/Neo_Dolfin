from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import logging
import pickle

# Define the flask app
app = Flask(__name__)
CORS(app)

# set up logging
logger = logging.getLogger('werkzeug') # grabs underlying WSGI logger

# Load the anomaly detection model
path_to_model = './model.pkl'
model = pickle.load(open(path_to_model, 'rb'), encoding='utf-8')

def index():
    return "Anomaly Detection API"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    np_data = np.array(data)
    prediction = model.predict(np_data)

    return jsonify(prediction.tolist())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
