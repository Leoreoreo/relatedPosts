from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def serve():
    return "lol"

current_keyword = None

@app.route("/KeywordSearch/")
def process_input():
    user_input = request.json.get('userInput')
    # Process the user input (you can replace this logic with your own)
    processed_output = f"You entered: {user_input}"
    return jsonify({'output': processed_output})

@app.route("/home/")
def home():
    return 'lol'

if __name__ == '__main__':
    app.run()
