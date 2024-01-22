import json
import openai

def read_target_strings(person_id):
    file_path = f"./persona{person_id}.json"

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)['data']

        BrosingHistoryTitles    = [_['title'] for _ in data['browsingHistoryList']]
        PostsContents           = [_['content'] for _ in data['facebookPostsList']]
        ScheduleAddrs           = [_['address'] for _ in data['schedule']]
        ProfileInfo             = [_ for _ in data.values() if isinstance(_, str)]
        return [BrosingHistoryTitles, PostsContents, ScheduleAddrs, ProfileInfo]

def direct_match(key_word, string_list):
    filtered_list = [
        string for string in string_list if all(
            word.lower() in string.lower().split() for word in key_word.split()
        )
    ]
    return filtered_list


def determine_relationship(key_word, sentence):

    prompt = f"Key word: {key_word}\n Sentence: {sentence} \nIs the key word related to the sentence? Please simply answer y for yes and n for no."
    response = openai.Completion.create(
        engine="text-davinci-003",  # Choose an appropriate engine
        prompt=prompt,
        temperature=0.5,
        max_tokens=100
    )

    # Extract the generated text from the response
    

    return response

def get_related_posts(person_id, key_word):
    tar_str = read_target_strings(person_id)
    print("------------------------------------------------")
    print("Direct Matches:")
    for lst in tar_str:
        match_strings = direct_match(key_word, lst)
        print(match_strings)
    print("------------------------------------------------")
    print("Related Matches:")
    for lst in tar_str:
        for string in lst:
            print(determine_relationship(key_word, string))
        # related_strings = direct_match(key_word, lst)
        # print(related_strings)



get_related_posts(2, 'schedule')