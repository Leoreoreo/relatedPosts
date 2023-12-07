# prompts
#[TODO]: tune the prompt
profile = """Return a realistic profile. \
This year is 2023.\
The income should be in dollar.
The home address must include street, city, and zip code. And it must be real.\
The street should be a real street.\
The city should be a real city in USA.\
The birthday should be in the MM/DD/YYYY format.\
The demographic of this person should represent the US population sample.\
The generated profile should match the following guidance: {guidance}.\


If there is no guidance for age, then the age is {age}. Otherwise, do not change age.\
Fit into the braces in the profile: {profile}.\


The format of the generated result should look like the following examples: 

Abigail Patel is a 32-year-old Asian American female living in 325 Main St, Newark, NJ 07102.\
She speaks English and her education background includes a bachelor's degree in Marketing. \
Abigail's date of birth is 05/26/1991. She is currently working as a marketing manager, with an annual income of $85,000.\
Abigail is married and has two children. \
She enjoys browsing social media and streaming movies on her mobile phone during her free time. \
When using her computer, she prefers using a wireless mouse and keyboard for easy navigation.\
On the internet, she likes to shop for clothes and read reviews before making a purchase.\


Return the profile in only one paragraph.
"""

profile_slots = """\
{First name} {Last name} is a {age ranging from 18 to 70 subject to continuous uniform distribution} {race} {gender} \
living in {real home address with street, city, state, and zip code}.\
{Pronoun} speaks {spoken language}.\
{Pronoun}'s education background is {education background}.
{Pronoun}'s date of birth is {date of birth}.\
{Pronoun} is a {job}, and the annual income is {income in dollar}.\
{marital status} {parental status}\
{detailed habit and perference when using the computer, mobile phone, and the Internet}.
"""

attributes = """
Given the profile: Abigail Patel is a 32-year-old Asian American female living in 325 Main St, Newark, NJ 07102.\
She speaks English and her education background includes a bachelor's degree in Marketing. \
Abigail's date of birth is 05/26/1991. She is currently working as a marketing manager, with an annual income of $85,000.\
Abigail is married and has two children. \
She enjoys browsing social media and streaming movies on her mobile phone during her free time. \
When using her computer, she prefers using a wireless mouse and keyboard for easy navigation.\
On the internet, she likes to shop for clothes and read reviews before making a purchase.\

Return the attributes in this format:\
"first_name": "Abigail",\
"last_name": "Patel",\
"age": "32",\
"gender": "female",\
"race": "Asian American",\
"street": "325 Main St",\
"city": "Newark",\
"state": "NJ",\
"zip_code": "07102",\
"spoken_language": "English",\
"education_background": "bachelor's degree in Marketing",\
"birthday": "05/26/1991",\
"job": "marketing manager",\
"income": "85000",\
"marital_status": "married",\
"parental_status": "has two children",\
"online_behavior": "She enjoys browsing social media and streaming movies on her mobile phone during her free time. When using her computer, she prefers using a wireless mouse and keyboard for easy navigation. On the internet, she likes to shop for clothes and read reviews before making a purchase."


Now given the profile: {persona}
Return the attributes in this format:\
"first_name": "",\
"last_name": "",\
"age": "",\
"gender": "",\
"race": "",\
"street": "",\
"city": "",\
"state": "",\
"zip_code": "",\
"spoken_language": "",\
"education_background": "",\
"birthday": "",\
"job": "",\
"income": "",\
"marital_status": "",\
"parental_status": "",\
"online_behavior": ""
"""

reconstruct_profile = """
The format of the profile follows this format:{profile}

Given the attributes of the profile:\
    "first_name": "Abigail",\
    "last_name": "Patel",\
    "age": "32",\
    "gender": "female",\
    "race": "Asian American",\
    "street": "325 Main St",\
    "city": "Newark",\
    "state": "NJ",\
    "zip_code": "07102",\
    "spoken_language": "English",\
    "education_background": "bachelor's degree in Marketing",\
    "birthday": "05/26/1991",\
    "job": "marketing manager",\
    "income": "85000",\
    "marital_status": "married",\
    "parental_status": "has two children",\
    "online_behavior": "She enjoys browsing social media and streaming movies on her mobile phone during her free time. When using her computer, she prefers using a wireless mouse and keyboard for easy navigation. On the internet, she likes to shop for clothes and read reviews before making a purchase."


Return the profile: Abigail Patel is a 32-year-old Asian American female living in 325 Main St, Newark, NJ 07102.\
She speaks English and her education background includes a bachelor's degree in Marketing. \
Abigail's date of birth is 05/26/1991. She is currently working as a marketing manager, with an annual income of $85,000.\
Abigail is married and has two children. \
She enjoys browsing social media and streaming movies on her mobile phone during her free time. \
When using her computer, she prefers using a wireless mouse and keyboard for easy navigation.\
On the internet, she likes to shop for clothes and read reviews before making a purchase.\


Now given the attributes of the profile:\
    {attributes}\


Return the profile:
"""

schedule = """\
    Provide ideas for this person to write schedule: {profile}. \
    Return a list of dict: {schedule}
"""

schedule_suffix = """\
You are acting as a game event designer.
Write daily event for this person: {profile}. \
Show me a reasonable schedule for this person from {start_date} to {end_date}.\
Events in the schedule should be more stochastic.\
The life in the period is similar to 2021.\
The person only works during workdays and will not work during weekend.\
You can generate fake but reasonable data that is related with the profile.\
The start time of one day is 00:00:00.\
Generate events from 00:00:00 to 23:59:59 for each day.\
Return a list of dict.\
Output following JSON format in plain text:
[{{{{\
    "start_time": <start moment of the event>,\
    "end_time": <start moment of the event>,\
    "event": <event>,\
}}}}]\
Never provide additional context.
"""

schedule_location = """\
    Given the person's profile: {profile} and the event list {event},
    generate unique different address and latitude and longitude for every event
    Return a dict: {location}
"""

schedule_location_suffix = """\
Given the person's profile: {profile}, \
generate location for every event: {event}

The address of events should be as different as possible.
You can generate fake but reasonable data that is consistent with the profile and event.\
Output following list format in plain text:
[
    [<event>, <address>, <latitude>, <longitude>, <time zone>, <locale>],\
]\
Never provide additional context.
"""

browser_device = """
All the choices of browsers and devices: {browser_devices}. \
Strictly follow the dict key in the choices of browsers and devices.

Given the profile: Abigail Patel is a 32-year-old Asian American female living in 325 Main St, Newark, NJ 07102.\
She speaks English and her education background includes a bachelor's degree in Marketing. \
Abigail's date of birth is 05/26/1991. She is currently working as a marketing manager, with an annual income of $85,000.\
Abigail is married and has two children. \
She enjoys browsing social media and streaming movies on her mobile phone during her free time. \
When using her computer, she prefers using a wireless mouse and keyboard for easy navigation.\
On the internet, she likes to shop for clothes and read reviews before making a purchase.\

Infer the browser and device the person uses (If there is no person's preference in the profile, randomly return one of the browser and device): 
Chrome - Windows

Given the profile: Michael Johnson is a 45-year-old African American male living in 3732 Oakwood Avenue, Los Angeles, CA 90017. \
He speaks English and Spanish fluently and has a bachelor's degree in Computer Science. \
Michael's date of birth is 06/23/1978, and he works as a software developer, earning an annual income of $105,000. \
Michael is married without children and enjoys playing video games on his computer in his free time. \
He prefers using a mechanical keyboard and a wireless mouse while browsing the internet for tech gadgets and news related to the latest software updates. \
Additionally, Michael likes to stay active by hiking and running on Griffith Park's trails and staying up-to-date with his social media accounts. 

Infer the browser and device the person uses (If there is no person's preference in the profile, randomly return one of the browser and device): 
Safari - Mac

Now given the profile: {persona}
Infer the browser and device the person uses (If there is no person's preference in the profile, randomly return one of the browser and device):

"""

user_agents = {
"Chrome - Chrome OS": "Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
"Chrome - Mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
"Chrome - Windows": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
"Firefox - Mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0",
"Firefox - Windows": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0",
"Microsoft Edge (Chromium) - Windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.100.0",
"Microsoft Edge (Chromium) - Mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/604.1 Edg/114.0.100.0",
"Opera - Mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48",
"Opera - Windows": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48",
"Safari - Mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15"
}

posts = """
Provide idea for this person to share daily life based on the profile and location history: {profile}. \
This person's daily schedule is {schedule}.\

The schedule is in the format of [[start time, end time, address, latitude, longitude, time_zone, locale]].
In some of the sublist, some elements may have NULL value. You should skip those NULL values.

Show me only {num} reasonable description in total between {start_date} and {end_date} to provide ideas.\
The life in the given time period is similar to 2021 so you can generate the description based on your current data.\

You should only return the list to me without any explaining message.\
You don't need to use any real time data, just generate the reasonalble and consistent data.\
You don't need to generatie description that may be inappropriate, irrelevant, or offensive.\
You do not need to manipulate the data in a way that is specific to a given time period.\
The seconds in the time should not be 00, it should be the format like 15:23:12.\

Output following JSON format in plain text:
[{{{{\
    "time": <time in string format>,\
    "address": <address where this person share the life>,\
    "content": <content>,\
    "latitude": <fake latitude>,\
    "longitude": <fake longitude>,\
    "timezone": <time zone>,\
    "locale": <locale>\
}}}}]\
Never provide additional context.

"""

browser_history = """
Given the person's profile: {profile}, \
and the schedule: {schedule},\
generate {num} browser history entries from {start_date} to {end_date}.\

No browsing history between 00:00:00 and 07:00:00 or after 22:30:00!

The webpage title should reflect the content in the webpage url.
The webpage be reasonable and related with the the schedule.
The webpage should at least include {num} times 1/3 of google search in this format: '<search content> - Google Search'.
Don't add address of schedule into webpage title.

The datetime should be realistic and associate with the webpage content.
The datetime second should not be 0.
The datetime should be dispense in one day!

You can generate fake but reasonable data that is consistent with the profile and schedule.
Output following list format in plain text:[[<datetime>, <webpage titile>, <webpage url>],]
Never provide additional context.
"""

browser_history_branch = """\
Given this website: {title} and its url: {url}\
Generate {num} websites with the same root domain name but different paths \
that you can access in the next 5 minutes starting from at least 30 seconds after {datetime}. \
The datetime should not be the same as {datetime}.\
Output following list format in plain text:[["<datetime>", "<webpage titile>", "<webpage url>"],].\
Never provide additional context.
"""