import json, os
import spacy
from collections import Counter
from string import punctuation
from sklearn.neighbors import LocalOutlierFactor
import en_core_web_sm

DATA_PATH = './Backend/personas_new/age'

ALL_PERSONA_KWS = None
# pid_20 = '4b81a719-4d63-4a0d-92be-5087c71a40b0_'
# pid_45 = '4b81a719-4d63-4a0d-92be-5087c71a40b0_a120fce9-2511-422b-9c80-cb739e59ef6a'
# pid_80 = '4b81a719-4d63-4a0d-92be-5087c71a40b0_199bea01-2cba-4381-9980-fad5a40da13e'

# nlp = spacy.load("en_core_web_sm")
nlp = en_core_web_sm.load()

def extract_persona_info(model):
    res = []
    for file_name in os.listdir(DATA_PATH):
        cur = {}
        if not file_name.endswith('.json'): continue
        with open(os.path.join(DATA_PATH, file_name), 'r') as file:
            data = json.load(file)['data']
            pid = file_name.split('.')[0]
            cur['pid'] = pid
            cur['first_name'] = data['first_name']
            cur['last_name'] = data['last_name']
            cur['age'] = data['age'] 
            cur['profile'] = data['profile']
            cur['keywords'] = extract_outliers(pid, 6, model)
            res.append(cur)
    return res

def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']
    doc = nlp(text.lower())
    for token in doc:
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            result.append(token.text)
    return result
def extractKeywords():
    res = {}
    for file_name in os.listdir(DATA_PATH):
        if not file_name.endswith('.json'): continue
        with open(os.path.join(DATA_PATH, file_name), 'r') as file:
            data = json.load(file)['data']
            pid = file_name.split('.')[0]
            res[pid] = {}
            ignore = {data["first_name"].lower(), data["last_name"].lower()}
            for bh in data['browsing_history']:
                keywords = get_hotwords(bh['title'])
                for kw in keywords:
                    if kw.lower() in ignore: continue
                    if kw in res[pid]:
                        res[pid][kw]['browsing_history'].add(bh['id'])
                    else:
                        res[pid][kw] = {'browsing_history': {bh['id']}, 'schedule': set(), 'facebookPostsList': set()}
            for sch in data['schedule']:
                keywords = get_hotwords(sch['event'])
                for kw in keywords:
                    if kw.lower() in ignore: continue
                    if kw in res[pid]:
                        res[pid][kw]['schedule'].add(sch['id'])
                    else:
                        res[pid][kw] = {'browsing_history': set(), 'schedule': {sch['id']}, 'facebookPostsList': set()}
    # print(res)
    return res

ALL_PERSONA_KWS = extractKeywords()

def get_common_keywords(all_keywords):
    common_keywords = None

    for persona in all_keywords:
        keywords = set(all_keywords[persona].keys())
        if common_keywords is None:
            common_keywords = keywords
        else:
            common_keywords = common_keywords.intersection(keywords)
    # print(f"common kws: {len(common_keywords)}")
    return common_keywords

def get_distinct_keywords(all_keywords, common_keywords, person_id_lst):
    res = {}
    for pid in person_id_lst:
        res[pid] = set(all_keywords[pid].keys()) - common_keywords
    return res

def get_vec_word_dic(distinct_keywords, model):
    vec_word_dic = {}       # {pid1: {vec1: word1, ...}, ...}
    ignored_words = set()
    for pid, words in distinct_keywords.items():
        vec_word_dic[pid] = {}
        for word in words:
            try:
                vec_word_dic[pid][tuple(model[word])] = word
            except KeyError:
                ignored_words.add(word)
        # print(f'encode {len(vec_word_dic[pid])} words for {pid}')
    # print(f'{len(ignored_words)} words ignored: {ignored_words}')
    return vec_word_dic, ignored_words

def get_outliers(vec_word_dic, pid):

    all_vectors = list(vec_word_dic[pid].keys())
    length = len(all_vectors)     # all_vectors[0:length] are vectors of target pid
    for id, word_dic in vec_word_dic.items():
        if id != pid:
            all_vectors += list(word_dic.keys())

    # Fit LocalOutlierFactor model
    lof_model = LocalOutlierFactor(n_neighbors=60, contamination=0.3)
    lof_model.fit(all_vectors)

    # Predict outliers
    outlier_labels = lof_model.fit_predict(all_vectors)

    outlier_vectors_set = [word for idx, word in enumerate(all_vectors[0:length]) if outlier_labels[idx] == -1]
    # print(len(outlier_vectors_set), 'outliers found')

    return [vec_word_dic[pid][vec] for vec in outlier_vectors_set]

def extract_top_n_kw(outliers, pid, n):
    return sorted(outliers, key=lambda x : -sum([len(ids) for _, ids in ALL_PERSONA_KWS[pid][x].items()]))[:n]

def extract_outliers(pid, max_kw_num, model):
    common_keywords = get_common_keywords(ALL_PERSONA_KWS)
    distinct_keywords = get_distinct_keywords(ALL_PERSONA_KWS, common_keywords, ALL_PERSONA_KWS.keys())
    # distinct_keywords = get_distinct_keywords(all_persona_keywords, set(), all_persona_keywords.keys())
    vec_word_dic, ignored_words = get_vec_word_dic(distinct_keywords, model)
    outliers = get_outliers(vec_word_dic, pid)
    if len(outliers) > max_kw_num:
        outliers = extract_top_n_kw(outliers, pid, max_kw_num)
    return outliers

def get_kw_info(pid, keyword):
  dic = ALL_PERSONA_KWS[pid][keyword]
  file_path = f"{DATA_PATH}/{pid}.json"
  res = {'browsing_history': {},
         'schedule': {},
         }

  with open(file_path, 'r') as json_file:
    data = json.load(json_file)['data']

    for bh in data['browsing_history']:
      if bh['id'] in dic['browsing_history']:
        date = bh['time'][:10]
        if date in res['browsing_history']:
          res['browsing_history'][date].append([bh['id'], bh['time'][11:-3], bh['title'], bh['url']])
        else:
          res['browsing_history'][date] = [[bh['id'], bh['time'][11:-3], bh['title'], bh['url']]]

    # for pc in data['facebookPostsList']:
    #   if pc['id'] in dic['facebookPostsList']:
    #     res.append(['facebookPostsList', pc['id'], pc['content']])

    for sch in data['schedule']:
      if sch['id'] in dic['schedule']:
        date = sch['start_time'][:10]
        if date in res['schedule']:
          res['schedule'][date].append([sch['id'], sch['start_time'][11:-3] + '-' + sch['end_time'][11:-3], sch['event'], sch['address']])
        else:
          res['schedule'][date] = [[sch['id'], sch['start_time'][11:-3] + '-' + sch['end_time'][11:-3], sch['event'], sch['address']]]

  return res