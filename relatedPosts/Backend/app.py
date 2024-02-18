from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from relatedPosts import relevant_search, read_existed_search, decode_dic_to_list, search_for_existed_search

app = Flask(__name__)
CORS(app)

@app.route("/")
def serve():
    return "lol"


@app.route("/KeywordSearch/", methods=["POST"])
def process_input():
    keyword = request.json.get('userInput')
    pid = request.json.get('selectedNumber')

    similar_searches = search_for_existed_search(pid, keyword)
    
    if similar_searches:
        return jsonify({'similarSearches': similar_searches})
    
    relevant_search(pid, keyword)
    dic = read_existed_search(pid, keyword)
    processed_output = decode_dic_to_list(dic, pid)
    return jsonify({'output': processed_output})

@app.route("/RelevantSearch/", methods=["POST"])
def search_anyway():
    keyword = request.json.get('userInput')
    pid = request.json.get('selectedNumber')
    relevant_search(pid, keyword)
    dic = read_existed_search(pid, keyword)
    processed_output = decode_dic_to_list(dic, pid)
    return jsonify({'output': processed_output})

@app.route("/ViewExistingSearch/", methods=["POST"])
def view_existing_search():
    pid = request.json.get('selectedNumber')
    keyword = request.json.get('userInput')
    dic = read_existed_search(pid, keyword)
    processed_output = decode_dic_to_list(dic, pid)
    return jsonify({'output': processed_output})

@app.route("/RelationGraph/", methods=["POST"])
def view_RelationGraph():
    pid = request.json.get('selectedNumber')
    graph_data = {
        "nodes": [
            {"id": 1, "name": "Node 1"},
            {"id": 2, "name": "Node 2"},
            {"id": 3, "name": "Node 3"}
        ],
        "links": [
            {"source": 1, "target": 2},
            {"source": 2, "target": 3}
        ]
    }
    return jsonify({'output': graph_data})

if __name__ == '__main__':
    app.run()
