from sentence_transformers import SentenceTransformer, util
import json
import os

model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
THRESHOLD = 0.3
PERSONAS_PATH = './personas'
RELATIONGRAPH_PATH = './relationGraph'

def SentenceTransformer_match(person_id, key_word):
  file_path = f"{PERSONAS_PATH}/persona{person_id}.json"
  query_embedding = model.encode(key_word)
  result = {
      'browsingHistoryList' : [],
      'facebookPostsList'   : [],
      'schedule'            : [],
      'info'                : []
  }

  with open(file_path, 'r') as json_file:
    data = json.load(json_file)['data']

    for bh in data['browsingHistoryList']:
      passage_embedding = model.encode(bh['title'])
      if util.dot_score(query_embedding, passage_embedding) > THRESHOLD:
        result['browsingHistoryList'].append(bh['id'])

    for pc in data['facebookPostsList']:
      passage_embedding = model.encode(pc['content'])
      if util.dot_score(query_embedding, passage_embedding) > THRESHOLD:
        result['facebookPostsList'].append(pc['id'])

    for sch in data['schedule']:
      passage_embedding = model.encode(sch['address'])
      if util.dot_score(query_embedding, passage_embedding) > THRESHOLD:
        result['schedule'].append(sch['id'])

    for info in data.keys():
      if isinstance(data[info], str):
        passage_embedding = model.encode(data[info])
        if util.dot_score(query_embedding, passage_embedding) > THRESHOLD:
          result['info'].append(info)

  file_path = f"{RELATIONGRAPH_PATH}/{person_id}_{key_word}.json"
  with open(file_path, 'w') as json_file:
      json.dump(result, json_file)
      print(f"---------------Saved as {person_id}_{key_word}.json------------------")
  return result

import os

def extract_pid_and_keyword(filename):
  parts = filename.split('_')
  if len(parts) == 2:
    pid, keyword = parts
    return pid, keyword.split('.')[0]
  return None, None

def search_files(directory):
  matching_files = []
  for filename in os.listdir(directory):
    if filename.endswith(".json"):
      pid, keyword = extract_pid_and_keyword(filename)
      if pid is not None and keyword is not None:
        matching_files.append({
            "pid": pid,
            "keyword": keyword
        })
  return matching_files

def search_for_existed_search(person_id, key_word):
  matching_files_info = search_files(RELATIONGRAPH_PATH)
  query_embedding = model.encode(key_word)
  res = []
  for file_info in matching_files_info:
    pid = int(file_info["pid"])
    keyword = file_info["keyword"]
    passage_embedding = model.encode(keyword)
    if pid == person_id and util.dot_score(query_embedding, passage_embedding) > THRESHOLD:
      res.append([pid, keyword])
  print(res)
  return res

def read_existed_search(person_id, key_word):
  with open(f"{RELATIONGRAPH_PATH}/{person_id}_{key_word}.json", 'r') as file:
    data = json.load(file)
    return data
  
def relevant_search(person_id, key_word):
  print(f"searching person{person_id} for {key_word}:")
  
  return SentenceTransformer_match(person_id, key_word)

def decode_dic_to_list(dic, person_id):
  file_path = f"{PERSONAS_PATH}/persona{person_id}.json"
  res = []
  with open(file_path, 'r') as json_file:
    data = json.load(json_file)['data']
  
    for bh in data['browsingHistoryList']:
      if bh['id'] in dic['browsingHistoryList']:
        res.append(['browsingHistoryList', bh['id'], bh['title']])

    for pc in data['facebookPostsList']:
      if pc['id'] in dic['facebookPostsList']:
        res.append(['facebookPostsList', pc['id'], pc['content']])

    for sch in data['schedule']:
      if sch['id'] in dic['schedule']:
        res.append(['schedule', sch['id'], sch['address']])

    for info in data.keys():
      if isinstance(data[info], str):
        if info in dic['info']:
          res.append(['profile', info, data[info]])
  return res

def create_sankey(person_id):
  data = {
    'nodes': [
          # default ads
          { 'id': 'ads1', 'name': 'Ad 1', 'column': 1 }, 
          { 'id': 'ads2', 'name': 'Ad 2', 'column': 1 },
          { 'id': 'ads3', 'name': 'Ad 3', 'column': 1 }, 
          { 'id': 'ads4', 'name': 'Ad 4', 'column': 1 },

    ],
    'links': []
  }

  # add attributes nodes
  persona_path = f"{PERSONAS_PATH}/persona1.json"
  with open(persona_path, 'r') as persona_file:
      persona_info = json.load(persona_file)['data']
      for attribute in persona_info.keys():
          if attribute == 'userId':
            continue
          data['nodes'].append({"id": f'attribute: {attribute}', "name": attribute, "column": 3})

  # add keywords and links
  for filename in os.listdir(RELATIONGRAPH_PATH):
    pid = filename.split("_")[0]
    keyword = filename.split("_")[1].split(".")[0]
    
    if pid == person_id:
        # add keywords
        kw_id = f'keyword: {keyword}'
        data['nodes'].append({"id": kw_id, "name": keyword, "column": 2})
        filepath = os.path.join(RELATIONGRAPH_PATH, filename)
        
        with open(filepath, "r") as file:
            filedata = json.load(file)
            if len(filedata['browsingHistoryList']) > 0:
                data['links'].append({'source': kw_id, 'target': 'attribute: browsingHistoryList', 'value': 1})
            if len(filedata['facebookPostsList']) > 0:
                data['links'].append({'source': kw_id, 'target': 'attribute: facebookPostsList', 'value': 1})
                data['links'].append({'source': kw_id, 'target': 'attribute: twitterPostsList', 'value': 1})
            if len(filedata['schedule']) > 0:
                data['links'].append({'source': kw_id, 'target': 'attribute: schedule', 'value': 1})
            for attr in filedata['info']:
                data['links'].append({'source': kw_id, 'target': f'attribute: {attr}', 'value': 1})

  return data

def get_sankey_data(person_id, keyword, attribute):
  persona_path = f"{PERSONAS_PATH}/persona{person_id}.json"
  relation_path = f"{RELATIONGRAPH_PATH}/{person_id}_{keyword}.json"
  if attribute == 'twitterPostsList':
    attribute = 'facebookPostsList' 
  attributes_as_list = {'browsingHistoryList', 'facebookPostsList', 'schedule'}
  res = []

  with open(persona_path, 'r') as persona_file:
    persona_info = json.load(persona_file)['data']

    if attribute in attributes_as_list:
      with open(relation_path, 'r') as relation_file:
        relation_data = json.load(relation_file)

        if attribute == 'browsingHistoryList':
          for bh in persona_info['browsingHistoryList']:
            if bh['id'] in relation_data['browsingHistoryList']:
              res.append(['browsingHistoryList', bh['id'], bh['title']])
        elif attribute == 'facebookPostsList':
          for pc in persona_info['facebookPostsList']:
            if pc['id'] in relation_data['facebookPostsList']:
              res.append(['facebookPostsList', pc['id'], pc['content']])
        elif attribute == 'schedule':
          for sch in persona_info['schedule']:
            if sch['id'] in relation_data['schedule']:
              res.append(['schedule', sch['id'], sch['address']])

    else:
        res.append(['profile', 'info', persona_info[attribute]])
  return res