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
            { 'id': 'ads3', 'name': 'Ad 3', 'column': 1 }, 
            { 'id': 'ads4', 'name': 'Ad 4', 'column': 1 },

            { 'id': 'keyword1', 'name': 'Keyword 1', 'column': 2 }, 
            { 'id': 'keyword2', 'name': 'Keyword 2', 'column': 2 },
            { 'id': 'keyword3', 'name': 'Keyword 3', 'column': 2 }, 
            { 'id': 'keyword4', 'name': 'Keyword 4', 'column': 2 },

            { 'id': 'attribute1', 'name': 'Attribute 1', 'column': 3 }, 
            { 'id': 'attribute2', 'name': 'Attribute 2', 'column': 3 },
            { 'id': 'attribute3', 'name': 'Attribute 3', 'column': 3 }, 
            { 'id': 'attribute4', 'name': 'Attribute 4', 'column': 3 },
            { 'id': 'attribute5', 'name': 'Attribute 5', 'column': 3 }, 
            { 'id': 'attribute6', 'name': 'Attribute 6', 'column': 3 },
        ],
        'links': [
            { 'source': 'ads1', 'target': 'keyword2', 'value': 1 }, 
            { 'source': 'ads1', 'target': 'keyword4', 'value': 1 },
            { 'source': 'ads2', 'target': 'keyword1', 'value': 1 }, 
            { 'source': 'ads2', 'target': 'keyword4', 'value': 1 },
            { 'source': 'ads3', 'target': 'keyword3', 'value': 1 }, 
            { 'source': 'ads4', 'target': 'keyword3', 'value': 1 },
            { 'source': 'keyword1', 'target': 'attribute1', 'value': 1 },
            { 'source': 'keyword1', 'target': 'attribute6', 'value': 1 },
            { 'source': 'keyword2', 'target': 'attribute2', 'value': 1 },
            { 'source': 'keyword2', 'target': 'attribute4', 'value': 1 },
            { 'source': 'keyword2', 'target': 'attribute6', 'value': 1 },
            { 'source': 'keyword3', 'target': 'attribute3', 'value': 1 },
            { 'source': 'keyword3', 'target': 'attribute2', 'value': 1 },
            { 'source': 'keyword4', 'target': 'attribute1', 'value': 1 },
            { 'source': 'keyword4', 'target': 'attribute2', 'value': 1 },
        ]
    }
    # graph_data = {
    #     "nodes": [
    #         {"id": "Ad 1", "column": 0},       # Column 1 (Ads)
    #         {"id": "Ad 2", "column": 0}, 

    #         {"id": "Keyword 1", "column": 1},  # Column 2 (Keywords)
    #         {"id": "Keyword 2", "column": 1},
    #         {"id": "Keyword 3", "column": 1},

    #         {"id": "Type 1", "column": 2},     # Column 3 (Types)
    #         {"id": "Type 2", "column": 2},
    #         {"id": "Type 3", "column": 2},

    #         {"id": "Data 1", "column": 3, "type": "Type 1"},     # Column 4 (Data)
    #         {"id": "Data 2", "column": 3, "type": "Type 1"},
    #         {"id": "Data 3", "column": 3, "type": "Type 2"},     
    #         {"id": "Data 4", "column": 3, "type": "Type 2"},
    #         {"id": "Data 5", "column": 3, "type": "Type 3"},     
    #         {"id": "Data 6", "column": 3, "type": "Type 3"},
    #     ],
    #     "links": [
    #         {"source": "Ad 1", "target": "Keyword 1"},   
    #         {"source": "Ad 1", "target": "Keyword 3"},
    #         {"source": "Ad 2", "target": "Keyword 1"},
    #         {"source": "Ad 2", "target": "Keyword 2"},

    #         {"source": "Keyword 1", "target": "Data 1"},  
    #         {"source": "Keyword 1", "target": "Data 2"},
    #         {"source": "Keyword 1", "target": "Data 4"},  
    #         {"source": "Keyword 2", "target": "Data 6"},
    #         {"source": "Keyword 2", "target": "Data 2"},  
    #         {"source": "Keyword 2", "target": "Data 1"},
    #         {"source": "Keyword 3", "target": "Data 1"},  
    #         {"source": "Keyword 3", "target": "Data 3"},
    #     ]
    # }


    return jsonify({'output': graph_data})

if __name__ == '__main__':
    app.run()
