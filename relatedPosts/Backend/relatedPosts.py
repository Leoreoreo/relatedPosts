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

def decode_dic_to_dic(dic, person_id):
  file_path = f"{PERSONAS_PATH}/persona{person_id}.json"
  res = {'browsingHistoryList': []}
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