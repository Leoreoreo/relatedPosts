from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from relatedPosts import relevant_search

app = Flask(__name__)
CORS(app)

@app.route("/")
def serve():
    return "lol"


@app.route("/KeywordSearch/", methods=["POST"])
def process_input():
    keyword = request.json.get('userInput')
    pid = request.json.get('selectedNumber')

    relevant_search(pid, keyword)
    processed_output = f"pid: {pid}, keyword: {keyword}, status: DONE"

    return jsonify({'output': processed_output})

@app.route("/home/")
def home():
    return 'lol'

if __name__ == '__main__':
    app.run()
