import sys
import logging
import uuid
from flask import Flask, request, jsonify

from flask_cors import CORS
from Database.database import Database
# from Database.utils import twitter, facebook
import datetime
import base64
import threading
import os
import queue

log_file_path = "logfile.log"
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# img_writing_path = os.path.join('Imgs\\')
# img_return_path = os.path.join('..', 'Backend', 'Imgs\\')
# img_path = os.path.join('Imgs\\')
img_path = 'Imgs/'
from pathlib import Path
p = Path(__file__).parent / 'Imgs'
img_path =str(p.absolute())
# print(img_return_path)
# current_path = os.getcwd()
# parent_folder_path = os.path.abspath(os.path.join(current_path, os.pardir))
# sys.path.append(parent_folder_path)

app = Flask(__name__, static_folder="Imgs")

lock = threading.Lock()


# ---------modified-----------
@app.route('/privacy_sandbox/get_all_users', methods=['GET'])
def getAllUsers():
    user_id = request.args.get('userId')
    print(user_id)
    try:
        with lock:
            db = Database()

            # db.clean_temp_table()

            all_users = db.get_all_users(persona_id=user_id)  # first_name, last_name, age, city
            all_users_list = []

            # ---------------ip:chaoran-------------------ip_location：time_zone
            # ip=[{ "ip": "45.139.10.108", "ip_location": "US - New
            # York" },{ "ip": "45.139.10.109", "ip_location": "US - OKC" }]
            ip = ["45.139.10.108", "US - New York"]

            # need location history -------- need新表
            if user_id is None:
                # put it into response
                for i in range(len(all_users)):
                    user_dict = {'userId': all_users[i][0],
                                 'firstName': all_users[i][1],
                                 'lastName': all_users[i][2],
                                 'name': all_users[i][1] + " " + all_users[i][2],
                                 'age': all_users[i][3],
                                 'birthday': all_users[i][4],
                                 'race': all_users[i][5],
                                 'gender': all_users[i][6],
                                 'street': all_users[i][7],
                                 'city': all_users[i][8],
                                 'state': all_users[i][9],
                                 'zipCode': all_users[i][10],
                                 'job': all_users[i][11],
                                 'income': all_users[i][12],
                                 'parentalStatus': all_users[i][13],
                                 'maritalStatus': all_users[i][14],
                                 'spokenLanguage': all_users[i][15],
                                 'educationBackground': all_users[i][16],
                                 'profileImgUrl': all_users[i][17],
                                 'profile': all_users[i][18],
                                 'onlineBehavior': all_users[i][19],

                                 'schedule': [],
                                 #
                                 'device': all_users[i][20],
                                 'browser': all_users[i][21],

                                 # 现在返回的是temp表里的
                                 # 'browsingHistoryList': db.return_browsing_history(all_users[i][0]),
                                 # 'twitterPostsList': db.return_twitter_post(all_users[i][0]),
                                 # 'facebookPostsList': db.return_facebook_post(all_users[i][0]),
                                 'browsingHistoryList': [],
                                 'twitterPostsList': [],
                                 'facebookPostsList': [],

                                 'ip': ip[0],
                                 'ipLocation': ip[1],

                                 }
                    all_users_list.append(user_dict)
                    db.close_connection()
            else:
                # print(all_users)
                user_dict = {'userId': all_users[0][0],
                             'firstName': all_users[0][1],
                             'lastName': all_users[0][2],
                             'name': all_users[0][1] + " " + all_users[0][2],
                             'age': all_users[0][3],
                             'birthday': all_users[0][4],
                             'race': all_users[0][5],
                             'gender': all_users[0][6],
                             'street': all_users[0][7],
                             'city': all_users[0][8],
                             'state': all_users[0][9],
                             'zipCode': all_users[0][10],
                             'job': all_users[0][11],
                             'income': all_users[0][12],
                             'parentalStatus': all_users[0][13],
                             'maritalStatus': all_users[0][14],
                             'spokenLanguage': all_users[0][15],
                             'educationBackground': all_users[0][16],
                             'profileImgUrl': all_users[0][17],
                             'profile': all_users[0][18],
                             'onlineBehavior': all_users[0][19],

                             'schedule': db.return_schedule(all_users[0][0]),

                             'device': all_users[0][20],
                             'browser': all_users[0][21],

                             # 现在返回的是temp表里的
                             'browsingHistoryList': db.return_browsing_history(all_users[0][0]),
                             'twitterPostsList': db.return_twitter_post(all_users[0][0]),
                             'facebookPostsList': db.return_facebook_post(all_users[0][0]),
                             # 'browsingHistoryList': db.return_browsing_history(all_users[0][0]),
                             # 'twitterPostsList': [],
                             # 'facebookPostsList': [],
                             'ip': ip[0],
                             'ipLocation': ip[1],

                             }
                print("---------------")
                print(user_dict['schedule'])
                # print(user_dict['browsingHistoryList'])
                # print(user_dict['twitterPostsList'])
                # print(user_dict['facebookPostsList'])
                print(user_dict['profileImgUrl'])
                print("---------------")
                all_users_list.append(user_dict)
                db.close_connection()
            # put it into response

        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': all_users_list
        }
        # print(response)
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to get all users."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/create_user', methods=['POST'])
def createUser():
    data = request.json
    guidance = data.get('profile')

    try:

        db = Database()  # Create a new Database object within the thread
        db.gen_generator()
        # db.clean_temp_table()
        res1 = db.fill_information(guidance=guidance)
        # print(res1)

        db.close_connection()

        user_dict = {'userId': res1[0],
                     'firstName': res1[1],
                     'lastName': res1[2],
                     'age': res1[3],
                     'birthday': res1[4],
                     'race': res1[5],
                     'gender': res1[6],
                     'street': res1[7],
                     'city': res1[8],
                     'state': res1[9],
                     'zipCode': res1[10],
                     'job': res1[11],
                     'income': res1[12],
                     'parentalStatus': res1[13],
                     'maritalStatus': res1[14],
                     'spokenLanguage': res1[15],
                     'educationBackground': res1[16],
                     'profileImgUrl': res1[17],
                     'profile': res1[18],
                     'onlineBehavior': res1[19],
                     }

        response = {
            'code': 200,
            'success': True,
            'data': user_dict
        }

        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to create users."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/generate_profile', methods=['POST'])
def generateProfile():
    data = request.json
    persona_id = int(data.get('userId'))
    attr_dict = {'first_name': data.get('firstName'),
                 'last_name': data.get('lastName'),
                 'age': data.get('age'),
                 'birthday': data.get('birthday'),
                 'race': data.get('race'),
                 'gender': data.get('gender'),
                 'street': data.get('street'),
                 'city': data.get('city'),
                 'state': data.get('state'),
                 'zip_code': data.get('zipCode'),
                 'job': data.get('job'),
                 'income': data.get('income'),
                 'parental_status': data.get('parentalStatus'),
                 'marital_status': data.get('maritalStatus'),
                 'spoken_language': data.get('spokenLanguage'),
                 'education_background': data.get('educationBackground'),
                 'online_behavior': data.get('onlineBehavior')}

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            new_profile = db.get_persona_profile_from_attributes(persona_id=persona_id, attributes=attr_dict)
            db.close_connection()
        profile_dict = {'profile': new_profile}
        response = {
            'code': 200,
            'success': True,
            'data': profile_dict
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to generate new profile."
        }
        return response


# ---------modified-----------
@app.route('/privacy_sandbox/generate_profile_picture', methods=['POST'])
def generateProfilePicture():
    data = request.json
    user_id = int(data.get('userId'))
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            new_profile_img = db.get_new_profile_img(persona_id=user_id)

            db.close_connection()
        img_dict = {'profilePicture': new_profile_img}
        response = {
            'code': 200,
            'success': True,
            'data': img_dict
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to generate new profile picture."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/get_browsing_history', methods=['POST'])
def getBrowsingHistoryList():
    data = request.json
    user_id = int(data.get('userId'))
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    count = data.get('count')
    print(start_date)
    print(end_date)
    if count is None:
        count = 5
    else:
        count = int(count)

    try:
        with lock:
            db = Database()
            db.gen_generator(False)

            total_location_history = db.get_brief_schedule(persona_id=user_id)
            print(total_location_history)
            num_expand = db.calculate_weeks(d1=total_location_history[-1][1], d2=end_date)
            print(num_expand)
            expanded_location_history = db.expand_schedule(original_schedule=total_location_history, num_expand=num_expand)
            print(expanded_location_history)
            location_history_in_range = db.get_location_history_in_time_range(start_time=start_date, end_time=end_date,
                                                                              total_location_history=expanded_location_history)
            print(location_history_in_range)
            num_day = db.calculate_days(start_date=start_date, end_date=end_date)
            location_history_day_list = db.convert_to_daily_schedule(schedule=location_history_in_range, num_day=num_day)
            print(num_day)
            random_day_list = db.generate_random_list(count=count, num_day=num_day)
            print(random_day_list)
            browsing_history_list = []
            for j in range(num_day):
                location_history = location_history_day_list[j]
                num_bh = random_day_list[j]
                browsing_history = db.fill_browsing_history(persona_id=user_id, bh_start_date=start_date,
                                                            bh_end_date=end_date,
                                                            num_bh=num_bh, schedule=location_history)
                for i in range(len(browsing_history)):
                    bh_dict = {'id': browsing_history[i][1], 'time': browsing_history[i][2],
                               'title': browsing_history[i][3], 'url': browsing_history[i][4]}
                    browsing_history_list.append(bh_dict)
            db.close_connection()
        # (persona_id, browsing_history_id, time, title, url)

        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': browsing_history_list
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to get browser history list."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/modify_ip', methods=['POST'])
def modifyIP():
    data = request.json
    user_id = data.get('userId')
    ip = data.get('ip')
    ip_location = data.get('ipLocation')
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.modify_ip(persona_id=user_id, ip=ip, ip_location=ip_location)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to modify ip."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/modify_device_browser', methods=['POST'])
def modifyDeviceBrowser():
    data = request.json
    user_id = data.get('userId')
    device = data.get('device')
    browser = data.get('browser')
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.modify_device_browser(persona_id=user_id, device=device, browser=browser)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to add device and browser."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/add_browsing_history', methods=['POST'])
def addBrowsingHistory():
    data = request.json
    user_id = data.get('userId')
    time = data.get('time')
    title = data.get('title')
    url = data.get('url')
    # db.fill_browsing_history(bh_start_date=start_date,bh_end_date=end_date,num_bh=count)
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.add_browsing_history(persona_id=user_id, time=time, title=title, url=url)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to add browser history list."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/delete_browsing_history', methods=['POST'])
def deleteBrowsingHistory():
    data = request.json
    id = data.get('id')
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.delete_browsing_history(browsing_history_id=id)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to delete browser history list."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/get_twitter_posts_list', methods=['POST'])
def getTwitterPostsList():
    data = request.json
    user_id = int(data.get('userId'))
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    count = data.get('count')

    if count is None:
        count = 5
    else:
        count = int(count)

    try:
        with lock:
            db = Database()
            db.gen_generator(False)

            total_location_history = db.get_brief_schedule(persona_id=user_id)
            num_expand = db.calculate_weeks(d1=total_location_history[-1][1], d2=end_date)
            expanded_location_history = db.expand_schedule(original_schedule=total_location_history, num_expand=num_expand)
            location_history_in_range = db.get_location_history_in_time_range(start_time=start_date, end_time=end_date,
                                                                              total_location_history=expanded_location_history)

            num_day = db.calculate_days(start_date=start_date, end_date=end_date)
            location_history_day_list = db.convert_to_daily_schedule(schedule=location_history_in_range,
                                                                     num_day=num_day)
            print(num_day)
            random_day_list = db.generate_random_list(count=count, num_day=num_day)
            print(random_day_list)
            twitter_posts_list = []
            for j in range(num_day):
                location_history = location_history_day_list[j]
                num_posts = random_day_list[j]
                twitter_posts = db.twitter(persona_id=user_id, location_history=location_history,
                                           lh_start_date=start_date,
                                           lh_end_date=end_date, num_posts=num_posts)

                for i in range(len(twitter_posts)):
                    t_dict = {'id': twitter_posts[i][0], 'time': twitter_posts[i][1][0],
                              'address': twitter_posts[i][1][2],
                              'content': twitter_posts[i][1][1], 'imgs': twitter_posts[i][1][7]}
                    twitter_posts_list.append(t_dict)

            db.close_connection()
        # [[time, content, address,  fake latitude, fake longitude, time_zone, locale, [img_url], [img_文件路径]].

        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': twitter_posts_list
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to get twitter posts list."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/add_twitter_posts_list', methods=['POST'])
def addTwitterPostsList():
    data = request.json
    persona_id = data.get('userId')
    time = data.get('time')
    # address = data.get('address')
    content = data.get('content')
    # latitude = data.get('latitude')
    # longitude = data.get('longitude')
    # time_zone = data.get('time_zone')
    # locale = data.get('locale')
    imgs = data.get('imgs')

    if imgs is None:
        imgs = []

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.add_post(platform="twitter", persona_id=persona_id, time=time, content=content, img_url=imgs)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to add twitter post."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/delete_twitter_posts_list', methods=['POST'])
def deleteTwitterPostsList():
    data = request.json
    post_id = data.get('id')
    platform = "twitter"
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.delete_post(platform=platform, post_id=post_id)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to delete twitter post."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/get_facebook_posts_list', methods=['POST'])
def getFacebookPostsList():
    data = request.json
    user_id = int(data.get('userId'))
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    count = data.get('count')

    if count is None:
        count = 5
    else:
        count = int(count)

    try:
        with lock:
            db = Database()
            db.gen_generator(False)

            total_location_history = db.get_brief_schedule(persona_id=user_id)
            num_expand = db.calculate_weeks(d1=total_location_history[-1][1], d2=end_date)
            expanded_location_history = db.expand_schedule(original_schedule=total_location_history, num_expand=num_expand)
            location_history_in_range = db.get_location_history_in_time_range(start_time=start_date, end_time=end_date,
                                                                              total_location_history=expanded_location_history)

            num_day = db.calculate_days(start_date=start_date, end_date=end_date)
            location_history_day_list = db.convert_to_daily_schedule(schedule=location_history_in_range,
                                                                     num_day=num_day)
            print(num_day)
            random_day_list = db.generate_random_list(count=count, num_day=num_day)
            print(random_day_list)
            facebook_posts_list = []
            for j in range(num_day):
                location_history = location_history_day_list[j]
                num_posts = random_day_list[j]
                facebook_posts = db.facebook(persona_id=user_id, location_history=location_history,
                                             lh_start_date=start_date,
                                             lh_end_date=end_date, num_posts=num_posts)
                for i in range(len(facebook_posts)):
                    t_dict = {'id': facebook_posts[i][0], 'time': facebook_posts[i][1][0],
                              'address': facebook_posts[i][1][2],
                              'content': facebook_posts[i][1][1], 'imgs': facebook_posts[i][1][7]}
                    facebook_posts_list.append(t_dict)
            db.close_connection()
        # [[time, content, address,  fake latitude, fake longitude, time_zone, locale, [img_url], [img_文件路径]].

        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': facebook_posts_list
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to get facebook posts list."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/add_facebook_posts_list', methods=['POST'])
def addFacebookPostsList():
    data = request.json
    persona_id = data.get('userId')
    time = data.get('time')
    # address = data.get('address')
    content = data.get('content')
    # latitude = data.get('latitude')
    # longitude = data.get('longitude')
    # time_zone = data.get('time_zone')
    # locale = data.get('locale')
    imgs = data.get('imgs')

    if imgs is None:
        imgs = []

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.add_post(platform="facebook", persona_id=persona_id, time=time, content=content, img_url=imgs)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to add facebook post."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/delete_facebook_posts_list', methods=['POST'])
def deleteFacebookPostsList():
    data = request.json
    post_id = data.get('id')
    platform = "facebook"
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.delete_post(platform=platform, post_id=post_id)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to delete facebook post."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/upload_img', methods=['POST'])
def uploadImg():
    data = request.json
    imgBase64Url = data.get('imgBase64Url')

    imgBase64 = imgBase64Url.split(",")[-1]
    
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            return_path = db.savePicture(imgBase64, img_path=img_path)
            db.close_connection()
        response = {
            'code': 200,
            'success': True,
            'data': return_path
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to decode img."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/save_persona', methods=['POST'])
def savePersona():
    data = request.json
    # user_id = data.get('userId')

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.confirm_persona()
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to save persona."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/modify_twitter_posts_list', methods=['POST'])
def modifyTwitterPostsList():
    data = request.json
    post_id = data.get('id')
    time = data.get('time')
    content = data.get('content')
    imgs = data.get('imgs')
    platform = "twitter"

    if imgs is None:
        imgs = []
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.modify_post(platform=platform, post_id=post_id, time=time, content=content, img_url=imgs)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to modify twitter post."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/modify_facebook_posts_list', methods=['POST'])
def modifyFacebookPostsList():
    data = request.json
    post_id = data.get('id')
    time = data.get('time')
    content = data.get('content')
    imgs = data.get('imgs')
    platform = "facebook"

    if imgs is None:
        imgs = []
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.modify_post(platform=platform, post_id=post_id, time=time, content=content, img_url=imgs)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to modify facebook post."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/modify_browsing_history', methods=['POST'])
def modifyBrowsingHistory():
    data = request.json
    browsing_history_id = data.get('id')
    time = data.get('time')
    title = data.get('title')
    url = data.get('url')

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.modify_browsing_history(browsing_history_id=browsing_history_id, time=time, title=title, url=url)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to modify browsing history."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/generate_schedule', methods=['POST'])
def generateSchedule():
    data = request.json
    user_id = int(data.get('userId'))
    start_date = data.get('start')
    end_date = data.get('end')
    request_id = data.get('requestId')

    if start_date is None:
        print("yes")
        current_time = datetime.datetime.now()
        cur_formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        start_date = cur_formatted_time

        future_time = current_time + datetime.timedelta(days=7)
        fut_formatted_time = future_time.strftime("%Y-%m-%d %H:%M:%S")
        end_date = fut_formatted_time

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            schedule = db.get_location_history(persona_id=user_id, start_date=start_date, end_date=end_date)
            db.close_connection()
        # (persona_id, browsing_history_id, time, title, url)
        schedule_list = []

        # put it into response
        for i in range(len(schedule)):
            schedule_dict = {'id': schedule[i][0], 'start': schedule[i][1],
                             'end': schedule[i][2], 'address': schedule[i][3]}
            schedule_list.append(schedule_dict)

        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': schedule_list
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to generate schedule."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/add_schedule', methods=['POST'])
def addSchedule():
    data = request.json
    user_id = data.get('userId')
    start_date = data.get('start')
    end_date = data.get('end')
    address = data.get('address')

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            schedule_id = db.add_location_history(persona_id=user_id, start_date=start_date, end_date=end_date,
                                                  address=address)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': schedule_id
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to add schedule."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/delete_schedule', methods=['POST'])
def deleteSchedule():
    data = request.json
    schedule_id = data.get('id')
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.delete_location_history(schedule_id=schedule_id)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to delete schedule."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/modify_schedule', methods=['POST'])
def modifySchedule():
    data = request.json
    schedule_id = data.get('id')
    start_date = data.get('start')
    end_date = data.get('end')
    address = data.get('address')

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.modify_location_history(schedule_id=schedule_id, start_date=start_date, end_date=end_date,
                                       address=address)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to modify schedule."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/cancel_generate', methods=['POST'])
def cancelGenerate():
    response = {
        'code': 200,
        'success': True,
        'data': ""
    }
    return jsonify(response)


@app.route('/privacy_sandbox/generate_ip', methods=['POST'])
def generateIp():
    data = request.json
    user_id = data.get('userId')
    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            ip_location_list = db.get_ip(persona_id=user_id)
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': {'ip': ip_location_list[0],
                     'ipLocation': ip_location_list[1]
                     }
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to get ip and ip location."
        }
        return jsonify(response)


# ---------modified-----------
@app.route('/privacy_sandbox/generate_device_browser', methods=['POST'])
def generateDeviceBrowser():
    data = request.json
    user_id = data.get('userId')

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            browser_device = db.get_device_browser(persona_id=user_id)
            db.close_connection()
        # Prepare a success response with the retrieved data
        bd_dict = {
            'browser': browser_device[0],
            'device': browser_device[1]
        }
        response = {
            'code': 200,
            'success': True,
            'data': bd_dict
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to generate device and browser."
        }
        return jsonify(response)


@app.route('/privacy_sandbox/clear_table', methods=['POST'])
def clearData():
    data = request.json
    # user_id = data.get('userId')

    try:
        with lock:
            db = Database()
            db.gen_generator(False)
            db.clean_temp_table()
            db.close_connection()
        # Prepare a success response with the retrieved data
        response = {
            'code': 200,
            'success': True,
            'data': ""
        }
        return jsonify(response)

    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to clean temp table."
        }
        return jsonify(response)


CORS(app, resources=r'/*')
if __name__ == '__main__':
    app.run()
