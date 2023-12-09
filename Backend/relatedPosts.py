import sys
import logging
import uuid
from flask import Flask, request, jsonify

from flask_cors import CORS
from Database.database import Database

from Generator.generator import Generator

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
lock = threading.Lock()

def related_posts():
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
    except Exception as e:
        db.close_connection()
        print(repr(e))
        logging.exception("An error occurred:")
        response = {
            'code': 200,
            'success': False,
            'data': "Failed to get facebook posts list."
        }

