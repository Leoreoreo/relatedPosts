from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from relatedPosts import relevant_search, read_existed_search, decode_dic, search_for_existed_search

app = Flask(__name__)
CORS(app)

@app.route("/")
def serve():
    return "lol"


@app.route("/KeywordSearch/", methods=["POST"])
def process_input():
    keyword = request.json.get('userInput')
    pid = request.json.get('selectedNumber')

    # Check for similar searches
    similar_searches = search_for_existed_search(pid, keyword)
    
    if similar_searches:
        return jsonify({'similarSearches': similar_searches})
    else:
        # No similar searches found, proceed with relevant search
        relevant_search(pid, keyword)
        
        dic = read_existed_search(pid, keyword)
        processed_output = decode_dic(dic, pid)
        return jsonify({'output': processed_output})

@app.route("/RelevantSearch/", methods=["POST"])
def search_anyway():
    keyword = request.json.get('userInput')
    pid = request.json.get('selectedNumber')
    relevant_search(pid, keyword)
    dic = read_existed_search(pid, keyword)
    processed_output = decode_dic(dic, pid)
    return jsonify({'output': processed_output})

@app.route("/ViewExistingSearch/", methods=["POST"])
def view_existing_search():
    # Handle request to view an existing search
    pid = request.json.get('selectedNumber')
    keyword = request.json.get('userInput')

    # Fetch existing search data
    dic = read_existed_search(pid, keyword)
    processed_output = decode_dic(dic, pid)
    return jsonify({'output': processed_output})

if __name__ == '__main__':
    app.run()
