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
        'nodes': [
            { 'id': 'ads1', 'name': 'Ad 1', 'column': 1 }, 
            { 'id': 'ads2', 'name': 'Ad 2', 'column': 1 },
            { 'id': 'keyword1', 'name': 'Keyword 1', 'column': 2 }, 
            { 'id': 'keyword2', 'name': 'Keyword 2', 'column': 2 },
            { 'id': 'attribute1', 'name': 'Attribute 1', 'column': 3 }, 
            { 'id': 'attribute2', 'name': 'Attribute 2', 'column': 3 },
            { 'id': 'data1', 'name': 'Data 1', 'column': 4 }, 
            { 'id': 'data2', 'name': 'Data 2', 'column': 4 }
        ],
        'links': [
            { 'source': 'ads1', 'target': 'keyword1', 'value': 1 }, 
            { 'source': 'ads2', 'target': 'keyword2', 'value': 1 },
            { 'source': 'keyword1', 'target': 'attribute1', 'value': 1 },
            { 'source': 'attribute1', 'target': 'data1', 'value': 1 },
            { 'source': 'attribute2', 'target': 'data1', 'value': 1 },
            { 'source': 'keyword2', 'target': 'attribute1', 'value': 1 },
            { 'source': 'keyword2', 'target': 'attribute2', 'value': 1 },
        ]
    }

    return jsonify({'output': graph_data})

if __name__ == '__main__':
    app.run()
