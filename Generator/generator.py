import os
import re
from datetime import datetime, timedelta
from random import randint, uniform, sample
import random
import emoji

import base64
import time
import requests

import openai
from langchain import LLMChain, PromptTemplate, FewShotPromptTemplate
from langchain.chat_models import ChatOpenAI

from Generator import config
from Generator import few_shot_examples
from Generator import prompts


os.environ['OPENAI_API_KEY'] = config.OPENAI_API_KEY
llm = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    temperature=0.9,  # this param controls the randomness of the generation results
)


def remove_emojis(text):
    cleaned_text = ""
    for character in text:
        if not emoji.is_emoji(character):
            cleaned_text += character
    return cleaned_text


class Generator:
    def __init__(self, persona_id=0):
        self.guidance = None

        self.persona_profile = None
        self.attributes = None  # all attributes dictionary

        self.location_history = None

        self.profile_img_url = None
        self.profile_img = None

        self.search_history_kw = None
        self.search_history_url = None  # kw->urls
        self.browsing_history = None  # url->urls
        self.final_browsing_history = None  # list (str,str,str)

        self.device_browser = None
        self.ip = None
        self.schedule = None
        self.persona_id = persona_id

        openai.api_key = config.OPENAI_API_KEY


    def get_persona_id(self):
        return self.persona_id


    def add_guidance(self, guidance):
        '''
        Add the guidance to the prompts for LLM generation.

        Input
            String: A description in natural language to guide the prompts.
        '''
        self.guidance = guidance


    def get_persona_profile(self, guidance) -> str:
        '''
        Generate the persona description from LLM

        Return	
            string: persona description
        '''
        print(f"Guidance is: {guidance}")
        prompt_template = PromptTemplate(
            input_variables=['profile', 'guidance', 'age'],
            template=prompts.profile
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)
        persona_profile = chain.run(profile=prompts.profile_slots, guidance=guidance, age=randint(18,70))

        self.persona_profile = persona_profile

        return self.persona_profile


    def get_persona_short_profile(self, age, race, gender, job) -> str:
        short_profile = f"A {age}-year-old {race} {gender} {job}"
        return short_profile


    def get_attributes(self, profile: str) -> dict:
        '''
        Generate the persona's attributes from the persona description

        Input
            str: the profile of the persona

        Return
            dict: the attributes of the persona
        '''
        prompt_template = PromptTemplate(
            input_variables=['persona'],
            template=prompts.attributes
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)
        result = chain.run(profile)
        result = eval("{" + result + "}")
        self.attributes = result

        return self.attributes


    def get_persona_profile_from_attributes(self, attributes: dict) -> str:
        '''
        Reconstruct the persona description from the persona's attributes

        Input
            dict: the profile of the persona

        Return
            str: the attributes of the persona
        '''
        prompt_template = PromptTemplate(
            input_variables=['profile', 'attributes'],
            template=prompts.reconstruct_profile
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)
        result = chain.run(profile=prompts.profile_slots, attributes=attributes)

        self.attributes = attributes
        self.persona_profile = result

        return result
    

    def get_location_from_schedule(self, profile: str, event: list):
        examples = few_shot_examples.schedule_location
        
        example_prompt = PromptTemplate(
            input_variables=['profile', "event", "location"],
            template=prompts.schedule_location
        )

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="",
            suffix=prompts.schedule_location_suffix,
            input_variables=['profile', "event"],
            example_separator="\n\n"
        )
        chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        results = chain.run(profile=profile, event=event)
        # results = eval(results)

        FLAG = True
        location_stack = []

        while FLAG:
            try:
                valid_location = re.findall(r'\[(.*?)\]', results[1:])

                tmp_location_stack = "[" + "],[".join(valid_location) + "]"
                tmp_location_stack = eval(tmp_location_stack)

                location_stack.extend(tmp_location_stack)

                if len(location_stack)>=len(event):
                    FLAG = False
                else:
                    results = chain.run(profile=profile, event=event)
            except Exception as e:
                # print(results)
                print(f"[LOCATION DICT GEN]: {e}")

        return location_stack



    def get_location_history(self, profile: str, start_date: str, end_date: str) -> list:
        '''
        Generate the persona's schedule. Default is a weekly schedule.

        Input
            str: the profile of the persona,
            str: the start date of the schedule,
            str: the end date of the schedule

        Return
            list: the persona's schedule
        '''
        # examples = few_shot_examples.location_history
        examples = few_shot_examples.schedule
        
        example_prompt = PromptTemplate(
            input_variables=['profile', "schedule"],
            template=prompts.schedule
        )

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="",
            suffix=prompts.schedule_suffix,
            input_variables=['profile', "start_date", "end_date"],
            example_separator="\n\n"
        )
        llm_schedule = ChatOpenAI(
            model_name='gpt-3.5-turbo',
            temperature=0.01,  # this param controls the randomness of the generation results
        )
        chain = LLMChain(llm=llm_schedule, prompt=few_shot_prompt)
        results = chain.run(profile=profile, 
                            start_date=start_date, 
                            end_date=end_date)
        
        FLAG = True
        history_stack = []
        format = "%Y-%m-%d %H:%M:%S"

        end_date_datetime = datetime.strptime(end_date, format)
        while FLAG:
            try:
                results = results.replace('\n', '').replace('    ','')
                valid_history = re.findall(r'{[^}]+}', results)

                tmp_history_stack = "[" + ",".join(valid_history) + "]"
                tmp_history_stack = eval(tmp_history_stack)

                history_stack.extend(tmp_history_stack)


                cnt_end_date = datetime.strptime(history_stack[-1]["end_time"], format)

                if cnt_end_date>=end_date_datetime:
                    FLAG = False
                else:
                    results = chain.run(profile=profile, 
                            start_date=history_stack[-1]["end_time"], 
                            end_date=end_date)
            except Exception as e:
                # print(results)
                print(f"[SCHEDULE GEN]: {e}")

        events = []
        for item in history_stack:
            events.append(item["event"])

        # print(history_stack)
        
        events = list(set(events))
        # print(events)

        location = self.get_location_from_schedule(profile, events)
        # print(location)
        location_dict = {item[0]: item[1:] for item in location}

        # print(location_dict)

        history_stack_with_location = []
        for item in history_stack:
            tmp1 = location_dict[item["event"]]
            tmp2 = [item["start_time"], item["end_time"], item["event"] + " - "+ tmp1[0]] 
            tmp2.extend(tmp1[1:])
            history_stack_with_location.append(tmp2)
        
        return history_stack_with_location


    def get_profile_img(self, short_profile):
        '''
        Generate the persona's attributes from the persona description

        Input
            str: the profile of the persona

        Return
            dict: the attributes of the persona
        '''
        response = openai.Image.create(
            prompt=f"""A realistic human alive head portrait image for {short_profile}.""",
            n=1,
            size="256x256",
            response_format="url",
        )
        self.profile_img_url = response['data'][0]['url']
        print(response['data'][0]["url"])

        self.profile_img = base64.b64encode(requests.get(self.profile_img_url).content)

        # base64 -> jpg, just for test, the database should save the base64 string
        # imgdata = base64.b64decode(self.profile_img)
        # filename = 'profile.jpg'
        # with open(filename, 'wb') as f:
        #     f.write(imgdata)

        return {"base64_json":self.profile_img, "url":self.profile_img_url}


    def get_device_browser(self, profile):
        '''
        Generate the persona's device and browser based on the persona description

        Input
            str: the profile of the persona

        Return
            string: the first name of the persona
        '''

        prompt_template = PromptTemplate(
            input_variables=['browser_devices', 'persona'],
            template=prompts.browser_device
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)
        result = chain.run(persona=profile, browser_devices=prompts.user_agents.keys())

        FLAG = True
        while FLAG:
            print(result)
            try:
                if result in prompts.user_agents.keys():
                    FLAG = False
            except Exception as e:
                print("retry b d..")
                print(e)
                result = chain.run(persona=profile, browser_devices=prompts.user_agents.keys())
        self.device_browser = [result, prompts.user_agents[result]]
        return [result, prompts.user_agents[result]]




    def gen_keywords_search_history(self, profile, kw_num):
        '''

        input:
        '''
        examples = few_shot_examples.keywords_search_history
        example_formatter_template = """\
        You are acting as this person: {profile} You searched {keywords_search_terms} in the browser."""

        example_prompt = PromptTemplate(
            input_variables=['profile', 'keywords_search_terms'],
            template=example_formatter_template
        )

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="""When you act as following people, you searched following keywords in the browser.""",
            suffix="""
                Now you are acting as a person: {persona}\n
                Return {kw_num} keywords or sentences you will browse. \
                They should be in lower-case and be separated in commas without index.
            """,
            input_variables=["persona", "kw_num"],
            example_separator="\n\n"
        )

        chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        self.search_history_kw = chain.run(persona=profile, kw_num=kw_num)
        self.search_history_url = []
        # search_url_title = []
        for kw in self.search_history_kw.split(", "):
            # search_url_title.append(kw + " - Google Search")
            self.search_history_url.append('https://www.google.com/search?q=' + kw.replace(" ", "+"))


    def gen_browsing_history(self, profile):
        # [TODO]: the browsing history can be generated based on not only search keywords but other URLs.
        # There can be another function self.gen_other_urls()

        if self.search_history_kw is None:
            self.gen_keywords_search_history(profile,kw_num=5)

        examples = few_shot_examples.browsing_history

        example_formatter_template = "You start browsing {src} and then visit the following website: {cluster}."

        example_prompt = PromptTemplate(
            input_variables=['src', 'cluster'],
            template=example_formatter_template
        )

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="",
            suffix="""
                Now you are acting as a person: {persona}\n
                You start browsing {src}. Return {url_num} website url you may visit. \
                They should be separated in commas without index.
            """,
            input_variables=["persona", "src", "url_num"],
            example_separator="\n\n"
        )

        chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        self.browsing_history = []
        for src in self.search_history_url:
            self.browsing_history.append(src)

            cluster = chain.run(persona=self.persona_profile, src=src,
                                url_num=randint(1, 10))  # maybe we can consider a new way to generate it?
            self.browsing_history.extend(cluster.split(", "))


    def get_url_title(self, url=''):

        examples = few_shot_examples.url_title

        example_formatter_template = """\
        From the given URL {url}, the website title generated is {title}. The following JSON format represents the same:
        {{{{
            "title": <title>, 
        }}}}
        Please do not provide additional context or information.
        """

        example_prompt = PromptTemplate(
            input_variables=['url', 'title'],
            template=example_formatter_template
        )

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="",
            suffix="Generate the website title based on its URL {url}.",
            input_variables=["url"],
            example_separator="\n\n"
        )

        # add RE to parse the title
        # return the entire JSON and then 

        chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        result = chain.run(url=url)
        result = eval(result)
        # print(result["title"])
        return result["title"]
        # return


    def get_time_samples(self, start_date, end_date, num_samples):
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        time_diff = end_datetime - start_datetime
        intervals = [uniform(0, time_diff.total_seconds()) for _ in range(num_samples)]
        intervals.sort()

        time_samples = []
        for i in range(num_samples):
            sample_datetime = start_datetime + timedelta(seconds=intervals[i])
            timestamp = int((sample_datetime - datetime(1601, 1, 1)) / timedelta(microseconds=1))

            time_samples.append(timestamp)

        return time_samples


    def compose_data(self, start_date, end_date, browsing_history, num_samples):
        latest_time_visit = self.get_time_samples(start_date, end_date, num_samples)

        final_url = []
        final_keywords = []
        search_idx = 0
        search_kw_list = self.search_history_kw.split(", ")

        return_browser_history = []

        for i, url, timestamp in zip(range(len(browsing_history)), browsing_history, latest_time_visit):
            if i == 0:
                timestamp_start = timestamp
            else:
                timestamp_start = latest_time_visit[i - 1]

            visit = 1

            if len(re.findall('www.google.com/search', url)) == 0:
                visit = randint(1, 5)
            else:
                kw = search_kw_list[search_idx]
                final_keywords.append([2, i + 1, kw, kw])
                search_idx += 1

            if url[-1] == ".":
                url = url[:-1]

            title = self.get_url_title(url)
            final_url.append([i + 1, url, title, visit, 0, timestamp, 0])

            return_browser_history.append((timestamp, title, url))

        self.final_browsing_history = return_browser_history

    def get_final_browsing_history(self, profile, start_date, end_date,
                                   num_samples):
        if self.browsing_history is None:
            self.gen_browsing_history(profile)
        self.compose_data(start_date, end_date, self.browsing_history, num_samples=num_samples)
        return self.final_browsing_history



# -------------rewrite browser history -------------


    def _time_convert(self, input_time:str):
        # Convert the input time string to a datetime object
        datetime_obj = datetime.strptime(input_time, "%Y-%m-%d %H:%M:%S")

        epoch_start = datetime(1601,1,1)
        time_diff = datetime_obj - epoch_start
        time_in_seconds = int(time_diff.total_seconds())

        # Convert seconds to WebKit timestamp by multiplying with 10^6
        webkit_timestamp = time_in_seconds * 1000000
        return webkit_timestamp



    def generate_browser_history_branch(self, datetime, title, url, num):    
        prompt_template = PromptTemplate(
            input_variables=['title', 'url', 'num', 'datetime'],
            template=prompts.browser_history_branch
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)

        while True:
            try:
                browser_history_branch = chain.run(title=title, url=url, num=num, datetime=datetime)
                # valid_history_branch = re.findall(r'\[(.*?)\]', browser_history_branch[1:])
                # if len(valid_history_branch) > 0:
                #     browser_history_branch = "[[" + "],[".join(valid_history_branch) + "]]"
                browser_history_branch = eval(browser_history_branch)
                break
            except Exception as e:
                print(f"[generate_browser_history_branch]: {e}")
                # if str(e).split(" ")[0] == "leading":
                print(browser_history_branch)
        
        return browser_history_branch


    def generate_browser_history(self, profile, start_date, end_date, num, schedule):
        if num == 0:
            return []
        examples = few_shot_examples.browsing_history_datetime
        example_formatter_template = """\
        Given this person's profile: {profile}\
        and the daily schedule: {schedule},\
        generate browser history: {browser_history}.
        """

        example_prompt = PromptTemplate(
            input_variables=['profile', "schedule", "browser_history"],
            template=example_formatter_template
        )
        
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="",
            suffix=prompts.browser_history,
            input_variables=['profile', "schedule", "num", "start_date", "end_date"],
            example_separator="\n\n"
        )

        chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        browser_history = chain.run(profile=profile, num=num, start_date=start_date, end_date=end_date,
                         schedule=str(schedule[:]))
        
        FLAG = True
        browser_history_stack = []

        while FLAG:
            try:
                valid_history = re.findall(r'\[(.*?)\]', browser_history[1:])
                if len(valid_history) > 0:
                    tmp_history_stack = "[[" + "],[".join(valid_history) + "]]"
                    browser_history_stack.extend(eval(tmp_history_stack))
                    if len(browser_history_stack) >= num:
                        FLAG = False
                    else:
                        start_date = browser_history_stack[-1][0]
                        browser_history = chain.run(profile=profile, num=num - len(browser_history_stack), start_date=start_date, end_date=end_date,
                         schedule=str(schedule[:]))
                else:
                    browser_history = chain.run(profile=profile, num=num - len(browser_history_stack), start_date=start_date, end_date=end_date,
                         schedule=str(schedule[:]))

            except Exception as e:
                print(f"[POST GEN]: {e}")
                browser_history = chain.run(profile=profile, num=num - len(browser_history_stack), start_date=start_date, end_date=end_date,
                         schedule=str(schedule[:]))
                
        # print(browser_history_stack)
        # print()

        # sample_root = []

        # for item in browser_history_stack:
        #     if "google search" in item[1].lower():
        #         sample_root.append(item)
        #     else:
        #         if randint(0,10)/10 > 0.7:
        #             sample_root.append(item)

        # print(sample_root,"\n")
        # branch = []
        # for item in sample_root:
        #     if "google search" in item[1].lower():
        #         tmp = self.generate_browser_history_branch(datetime = item[0], title = item[1], url = item[2], num=randint(3,5))
        #     else:
        #         tmp = self.generate_browser_history_branch(datetime = item[0], title = item[1], url = item[2], num=randint(1,3))
        #     branch.extend(tmp)
        
        # # sample_branch = sample(branch, int(num*0.05))
        # # print(sample_branch,"\n")
        # # leaves = []
        # # for item in sample_branch:
        # #     # print(item)
        # #     tmp = self.generate_browser_history_branch(datetime = item[0], title = item[1], url = item[2], num=randint(1,3))
        # #     # print(tmp,"\n")
        # #     leaves.extend(tmp)

        # browser_history_stack.extend(branch)
        # browser_history_stack_copy = []
        # for i in browser_history_stack:
        #     browser_history_stack_copy.append(self._time_convert(i[0]), i[1], i[2])
        # # browser_history_stack.extend(leaves)

        # browser_history_stack_copy = sample(browser_history_stack_copy, num)
        # browser_history_stack_copy.sort(key=lambda x: x[0])

        return browser_history_stack



# --------------------------------------------------



    def get_post(self, num: int, start_date, end_date, schedule: list, short_profile):
        print("num of posts:")
        print(num)
        if num == 0:
            return []
        examples = few_shot_examples.posts
        example_formatter_template = """Provide idea for this person to write tweet based on the profile and location history: {profile}. \
        {location_history}\
        Return a list of lists: {posts}"""

        example_prompt = PromptTemplate(
            input_variables=['profile', "posts", "location_history"],
            template=example_formatter_template
        )

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="",
            suffix=prompts.posts,
            input_variables=['profile', "num", "start_date", "end_date", "schedule"],
            example_separator="\n\n"
        )
        # [[time, address, fake latitude, fake longitude, time zone, locale]]

        chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        post = chain.run(profile=self.persona_profile, num=num, start_date=start_date, end_date=end_date,
                         schedule=str(schedule[:]))
        FLAG = True
        post_stack = []

        while FLAG:
            try:
                valid_post = re.findall(r'\{(.*?)\}', post[1:])
                if len(valid_post) > 0:
                    tmp_post_stack = "[{" + "},{".join(valid_post) + "}]"
                    # tmp_post_stack = remove_emojis(tmp_post_stack)
                    post_stack.extend(eval(tmp_post_stack))
                    if len(post_stack) >= num:
                        FLAG = False
                    else:
                        start_date = post_stack[-1]['time']
                        post = chain.run(profile=self.persona_profile, num=num - len(post_stack), start_date=start_date,
                                         end_date=end_date,
                                         schedule=str(schedule[:]))
                else:
                    # print(post)
                    post = chain.run(profile=self.persona_profile, num=num - len(post_stack), start_date=start_date,
                                     end_date=end_date,
                                     schedule=str(schedule[:]))

            except Exception as e:
                # print(post)
                print(f"[POST GEN]: {e}")
                break


        post_with_img = []
        for p in post_stack:
            post_url_list = []
            post_img_list = []
            num = randint(0, 2)
            if num > 0:  # time, address, content
                imgs = self.get_live_img(moment=p["time"], post=p["content"], address=p["address"], short_profile=short_profile, num=num)
                for i in range(num):
                    post_url_list.append(imgs[i]['url'])
                    base64_img = base64.b64encode(requests.get(imgs[i]['url']).content)
                    post_img_list.append(base64_img)
            post_with_img.append(
                [p["time"], p["content"], p["address"], p["latitude"], p["longitude"], p["timezone"], p["locale"], post_url_list, post_img_list]) 

        # [[time, content, address, fake latitude, fake longitude, time_zone, locale, [img_url], [img_文件路径]].
        #[TODO]: make it as a json
        return post_with_img

    def get_live_img(self, post, moment, address, short_profile, num):
        prompt = f"A realistic life environment object image: {post} at {moment} in {address} for this person: {short_profile}."

        response = openai.Image.create(
            prompt=prompt,
            n=num,
            size="512x512",
            response_format="url",
        )
        live_img_urls = response['data']

        return live_img_urls
    

    # functional programming validation
    # def validate(gen fun, bool) 



import json
from datetime import datetime
import pytz

def time_convert(date_string, timezone):
    local_tz = pytz.timezone(timezone)
    date_object_with_tz = local_tz.localize(datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S"))

    date_object_utc = date_object_with_tz.astimezone(pytz.UTC)

    webkit_epoch = datetime(1601, 1, 1, tzinfo=pytz.UTC)
    webkit_timestamp = int((date_object_utc - webkit_epoch).total_seconds() * 1000000)

    return webkit_timestamp



def generate_random_profile(sex, age):
    salary = ["less than 40k", "more than 40k but less than 115k", "more than 115k"]
    race = ["Asian", "Hispanic or Latino", "African American", "White"]
    children = ["has child(ren)", "no child"]

    chosen_sex = sex
    chosen_age = age
    chosen_salary = random.choice(salary)
    chosen_race = random.choice(race)
    chosen_children = random.choice(children)

    profile = f"A {chosen_sex} of age {chosen_age}, earning {chosen_salary} annually, who is {chosen_race} and {chosen_children}."
    
    return profile


if __name__ == '__main__':

    # print(time_convert("2023-08-10 09:00:00", "America/New_York"))


    sex = ["male", "female"]
    age = ["18-24", "25-35", "36-45", "46-55", "56-65"]
    gen = Generator()

    userId = 8

    # while userId<=10:
    file_name = "persona" + str(userId)

    print(file_name,"\n")

    with open('./'+file_name+'.json', 'r') as file:
        persona = json.load(file)

    persona["data"]["profile"]
    gen.get_profile_img(gen.get_persona_short_profile(persona["data"]["age"], persona["data"]["race"], persona["data"]["gender"], persona["data"]["job"]))

    # persona = {
    #     "success": True, 
    #     "code": 200, 
    #     "data": {
    #         "userId": userId,
    #         "browsingHistoryList":[],
    #         "facebookPostsList": [],
    #         "twitterPostsList": [],
    #         "schedule": []
    #     }
    # }

    # # guidance = "a female whose age is between 46 and 55, has children, with annual salary less than 40k"
    # guidance = generate_random_profile(i,j)
    # profile = gen.get_persona_profile(guidance)
    # attribute = gen.get_attributes(profile)

    # persona["data"].update(attribute)
    # persona["data"].update({"profile": profile})

    # browser_device = gen.get_device_browser(profile)
    # persona["data"].update({"browser":browser_device[0], "device":browser_device[1]})

    # print(persona)

    # persona["data"]["schedule"] = []
    # persona["data"]["browsingHistoryList"] = []
    # id = 1000
    # browser_id = 1
    # date = 10

    # while date<=16:
    #     full_date = "2023-07-" + str(date)
    #     print(full_date)
    #     FLAG = True
    #     while FLAG:
    #         try:
    #             schedule = gen.get_location_history(persona["data"]["profile"], start_date=full_date+" 06:00:00", end_date=full_date+" 23:59:59")
    #             print(schedule)
    #             for item in schedule:
    #                 persona["data"]["schedule"].append({"id":id, "start":item[0], "end":item[1], "address": item[2]})
    #                 id += 1
    #             FLAG = False
    #         except Exception as e:
    #             print(e)

    #     FLAG = True
    #     while FLAG:
    #         try:
    #             browser_history = gen.generate_browser_history(persona["data"]["profile"], start_date=full_date+" 06:00:00", end_date=full_date+" 23:59:59", num=50, schedule=schedule)
    #             print(browser_history)
                
    #             for item in browser_history:
    #                 persona["data"]["browsingHistoryList"].append({"id":browser_id, 
    #                                                     "time":time_convert(item[0], schedule[0][5]),
    #                                                     "title":item[1],
    #                                                     "url":item[2]})   
    #                 browser_id += 1
    #             FLAG = False
    #             with open('./'+file_name+'.json', 'w') as file:
    #                 json.dump(persona, file)
    #         except Exception as e:
    #             print(e)
        
    
    #     date += 1

        # userId += 1
        


        

        
    
