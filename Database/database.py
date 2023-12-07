import base64
import datetime
import sqlite3

import sys
import os
import uuid
from datetime import datetime, timedelta
import random

sys.path.append('..')
from Generator.generator import Generator
from Generator.network_manage import connect_to_vpn
import threading
import os

lock = threading.Lock()

# db_path = os.path.join('..', 'Backend', 'persona.db')
db_path = '../Backend/persona.db'

# img_path = os.path.join('..', 'Backend', 'Imgs\\') # real_img_path
img_path = '../Backend/Imgs/'
from pathlib import Path
p = Path(__file__).parent.parent / 'Backend' / 'Imgs'
img_path =str(p.absolute())


# store_img_path = os.path.join('Imgs/') # store_img_path
class Database:
    def __init__(self):

        self.database_file = './Backend/persona.db'

        if os.path.exists(self.database_file):
            print("The database file exists.")
            self.con = sqlite3.connect(self.database_file)
            self.cur = self.con.cursor()
        else:
            print("The database file does not exist. Creating files...")
            self.con = sqlite3.connect(self.database_file)
            self.cur = self.con.cursor()
            # create permanent tables
            self.cur.execute(
                "CREATE TABLE information(persona_id, first_name, last_name, age, birthday, race, gender, street, city, "
                "state, zip_code, job, income, parental_status, marital_status, spoken_language, "
                "education_background, profile_img_url, profile, online_behavior, device, browser, ip, ip_location);")  # 24
            # self.cur.execute("CREATE TABLE photo(persona_id, profile_img_url)")
            self.cur.execute("CREATE TABLE person_history(persona_id, browsing_history_id);")
            self.cur.execute("CREATE TABLE browsing_history(browsing_history_id, time, title, url);")
            # self.cur.execute("")
            # self.cur.execute("CREATE TABLE profile(persona_id, profile)")
            self.cur.execute("CREATE TABLE twitter_posts(persona_id, post_id);")
            self.cur.execute(
                "CREATE TABLE twitter_posts_info(post_id, time, address, content, latitude, longitude, time_zone, locale);")
            self.cur.execute("CREATE TABLE twitter_posts_img_url(post_id, img_url);")

            self.cur.execute("CREATE TABLE facebook_posts(persona_id, post_id);")
            self.cur.execute(
                "CREATE TABLE facebook_posts_info(post_id, time, address, content, latitude, longitude, time_zone, locale);")
            self.cur.execute("CREATE TABLE facebook_posts_img_url(post_id, img_url);")
            self.cur.execute(
                "CREATE TABLE person_schedule(persona_id, schedule_id)")
            self.cur.execute(
                "CREATE TABLE schedule(schedule_id, start_time, end_time, address, latitude, longitude, time_zone, locale)")
            # self.cur.execute(
            #     "CREATE TABLE brief_schedule(persona_id, schedule)")

            self.cur.execute(
                "CREATE TABLE temp_information(persona_id, first_name, last_name, age, birthday, race, gender, street, "
                "city,"
                "state, zip_code, job, income, parental_status, marital_status, spoken_language, "
                "education_background, profile_img_url, profile, online_behavior, device, browser, ip, ip_location);")
            # self.cur.execute("CREATE TABLE photo(persona_id, profile_img_url)")
            self.cur.execute("CREATE TABLE temp_person_history(persona_id, browsing_history_id);")
            self.cur.execute("CREATE TABLE temp_browsing_history(browsing_history_id, time, title, url);")
            # self.cur.execute("CREATE TABLE profile(persona_id, profile)")
            self.cur.execute("CREATE TABLE temp_twitter_posts(persona_id, post_id);")
            self.cur.execute(
                "CREATE TABLE temp_twitter_posts_info(post_id, time, address, content, latitude, longitude, time_zone, locale);")
            self.cur.execute("CREATE TABLE temp_twitter_posts_img_url(post_id, img_url);")

            self.cur.execute("CREATE TABLE temp_facebook_posts(persona_id, post_id);")
            self.cur.execute(
                "CREATE TABLE temp_facebook_posts_info(post_id, time, address, content, latitude, longitude, time_zone, locale);")
            self.cur.execute("CREATE TABLE temp_facebook_posts_img_url(post_id, img_url);")

            self.cur.execute(
                "CREATE TABLE temp_person_schedule(persona_id, schedule_id)")
            self.cur.execute(
                "CREATE TABLE temp_schedule(schedule_id, start_time, end_time, address, latitude, longitude, time_zone, locale)")
            # self.cur.execute(
            #     "CREATE TABLE temp_brief_schedule(persona_id, schedule)")
            # cursor.execute('SELECT * FROM your_table')
            #
            # # Fetch all the rows from the result set
            # rows = cursor.fetchall()
            #
            # # Transfer the rows into a list of lists
            # data = [list(row) for row in rows]

            self.cur.execute(
                "CREATE TABLE permanent_table(fetch_id, global_persona_id, facebook_post_id, twitter_post_id, browsing_history_id, schedule_id)")
            self.cur.execute(
                "INSERT INTO permanent_table(fetch_id, global_persona_id, facebook_post_id, twitter_post_id, browsing_history_id, schedule_id) VALUES (1,1,1,1,1,1);")
        self.con.commit()
        self.gen = None
        self.cur.execute("SELECT * FROM permanent_table LIMIT 1")
        self.fetch_id, self.global_persona_id, self.facebook_post_id, self.twitter_post_id, self.browsing_history_id, self.schedule_id = self.cur.fetchone()

        self.browsing_history = None
        self.twitter_posts = None
        self.facebook_posts = None

    def close_connection(self):
        self.con.close()

    # 先在临时table找，找不到再到permanent中找。找到之后放到临时。之后update到permanent。所有操作在表中操作。
    def get_global_id(self):
        cur_persona_id = self.global_persona_id
        self.global_persona_id = self.global_persona_id + 1
        self.cur.execute("UPDATE permanent_table SET global_persona_id = {global_persona_id} WHERE fetch_id = 1".format(
            global_persona_id=self.global_persona_id))
        self.con.commit()
        return cur_persona_id

    def get_facebook_post_id(self):
        cur_post_id = self.facebook_post_id
        self.facebook_post_id = self.facebook_post_id + 1
        self.cur.execute("UPDATE permanent_table SET facebook_post_id = {facebook_post_id} WHERE fetch_id = 1".format(
            facebook_post_id=self.facebook_post_id))
        self.con.commit()
        return cur_post_id

    def get_twitter_post_id(self):
        cur_post_id = self.twitter_post_id
        self.twitter_post_id = self.twitter_post_id + 1
        self.cur.execute("UPDATE permanent_table SET twitter_post_id = {twitter_post_id} WHERE fetch_id = 1".format(
            twitter_post_id=self.twitter_post_id))
        self.con.commit()
        return cur_post_id

    def get_browsing_history_id(self):
        cur_browsing_history_id = self.browsing_history_id
        self.browsing_history_id = self.browsing_history_id + 1
        self.cur.execute(
            "UPDATE permanent_table SET browsing_history_id = {browsing_history_id} WHERE fetch_id = 1".format(
                browsing_history_id=self.browsing_history_id))
        self.con.commit()
        return cur_browsing_history_id

    def get_schedule_id(self):
        cur_schedule_id = self.schedule_id
        self.schedule_id = self.schedule_id + 1
        self.cur.execute("UPDATE permanent_table SET schedule_id = {schedule_id} WHERE fetch_id = 1".format(
            schedule_id=self.schedule_id))
        self.con.commit()
        return cur_schedule_id

    def gen_generator(self, boolen=True):
        if boolen:
            self.gen = Generator(self.get_global_id())
        else:
            self.gen = Generator()

    def add_guidance(self, guidance):
        self.gen.add_guidance(guidance)

    def get_persona_profile(self, guidance):
        return self.gen.get_persona_profile(guidance)

    def get_persona_short_profile(self, age, race, gender, job):
        # self.cur.execute(f"SELECT age, race, gender, job from temp_information WHERE persona_id={persona_id}".format(persona_id=persona_id))
        # res = self.cur.fetchone()
        # age, race, gender, job = res[0], res[1], res[2], res[3]
        return self.gen.get_persona_short_profile(age, race, gender, job)

    def get_persona_profile_from_attributes(self, persona_id, attributes: dict):
        new_profile = self.gen.get_persona_profile_from_attributes(attributes=attributes)
        self.cur.execute("""
            UPDATE temp_information SET 
            first_name=?,
            last_name=?,
            age=?,
            birthday=?,
            race=?,
            gender=?,
            street=?,
            city=?,
            state=?,
            zip_code=?,
            job=?,
            income=?,
            parental_status=?,
            marital_status=?,
            spoken_language=?,
            education_background=?,
            profile=?,
            online_behavior=?
            WHERE persona_id=?
        """, (
            attributes["first_name"],
            attributes["last_name"],
            attributes["age"],
            attributes["birthday"],
            attributes["race"],
            attributes["gender"],
            attributes["street"],
            attributes["city"],
            attributes["state"],
            attributes["zip_code"],
            attributes["job"],
            attributes["income"],
            attributes["parental_status"],
            attributes["marital_status"],
            attributes["spoken_language"],
            attributes["education_background"],
            new_profile,
            attributes["online_behavior"],
            persona_id
        ))
        self.con.commit()
        return new_profile

    def get_profile_img(self, age, race, gender, job):
        # print("-------------------------------")
        short_profile = self.get_persona_short_profile(age, race, gender, job)
        # print(short_profile)
        profile_img = self.gen.get_profile_img(short_profile)
        # {"base64_json": self.profile_img, "url": self.profile_img_url}
        return profile_img

    def get_new_profile_img(self, persona_id):
        self.cur.execute(f"SELECT age, race, gender, job from temp_information WHERE persona_id={persona_id}".format(
            persona_id=persona_id))
        res = self.cur.fetchone()
        age, race, gender, job = res[0], res[1], res[2], res[3]
        new_profile_img = self.get_profile_img(age, race, gender, job)
        # {"base64_json": self.profile_img, "url": self.profile_img_url}
        print('=======================================')
        print(img_path)
        profile_img_store = self.savePicture(new_profile_img["base64_json"], img_path)
        print("profile_img_store: ", profile_img_store)
        query = "UPDATE temp_information SET profile_img_url = ? WHERE persona_id = ?"
        self.cur.execute(query, (profile_img_store, persona_id))
        self.con.commit()
        # return new_profile_img["url"] #this returns tmp link
        return profile_img_store

    def get_persona_id(self):
        return self.gen.get_persona_id()

    def get_final_browsing_history(self, profile, start_date='2023-05-16 10:00:00', end_date='2023-05-17 23:59:59',
                                   num_samples=10):
        return self.gen.get_final_browsing_history(profile, start_date, end_date, num_samples)

    def get_device_browser(self, persona_id):
        self.cur.execute("SELECT profile FROM temp_information WHERE persona_id=?", (persona_id,))
        profile = self.cur.fetchone()
        print("stop here")
        browser_device = self.gen.get_device_browser(profile)
        print("stop here")
        browser = browser_device[0]
        device = browser_device[1]
        self.cur.execute("UPDATE temp_information SET device=?, browser=? WHERE persona_id=?",
                         (device, browser, persona_id))
        self.con.commit()
        return browser_device

    # exclude device and browser
    def get_attributes(self, profile):
        return self.gen.get_attributes(profile)

    # ----------------------------check 到这----------------------------
    def get_location_history(self, persona_id, start_date='2023-05-16 10:00:00', end_date='2023-05-17 23:59:59'):
        print("Generating location history...")
        # clear all
        self.cur.execute(
            "DELETE FROM temp_schedule WHERE schedule_id IN (SELECT schedule_id FROM temp_person_schedule WHERE "
            "persona_id=?)", (persona_id,))
        self.cur.execute("DELETE FROM temp_person_schedule WHERE persona_id=?", (persona_id,))

        print("success")

        # get profile
        self.cur.execute(
            f"SELECT profile FROM temp_information WHERE persona_id={persona_id};".format(persona_id=persona_id))
        profile = self.cur.fetchone()
        schedule = self.gen.get_location_history(profile=profile, start_date=start_date, end_date=end_date)
        # '[[],[]]' -> [[],[]]
        # print(type(schedule))
        print(schedule)

        schedule_list = []
        for i in range(len(schedule)):
            schedule_id = self.get_schedule_id()
            start_time = schedule[i][0]
            end_time = schedule[i][1]
            address = schedule[i][2]
            latitude = schedule[i][3]
            longitude = schedule[i][4]
            time_zone = schedule[i][5]
            locale = schedule[i][6]
            self.cur.execute("INSERT INTO temp_person_schedule(persona_id, schedule_id) VALUES (?,?);",
                             (persona_id, schedule_id))
            self.cur.execute("INSERT INTO temp_schedule(schedule_id, start_time, end_time, address, latitude, "
                             "longitude, time_zone, locale) VALUES (?,?,?,?,?,?,?,?)",
                             (schedule_id, start_time, end_time, address, latitude, longitude, time_zone, locale))
            schedule_list.append([schedule_id, start_time, end_time, address])
        self.con.commit()
        return schedule_list

    def add_location_history(self, persona_id, start_date, end_date, address):
        schedule_id = self.get_schedule_id()
        self.cur.execute("INSERT INTO temp_person_schedule(persona_id, schedule_id) VALUES (?,?);",
                         (persona_id, schedule_id))
        # self.cur.execute("INSERT INTO temp_schedule(schedule_id, start_time, end_time, address, latitude, "
        #                  "longitude, time_zone, locale) VALUES (?,?,?,?,?,?,?,?)",
        #                  (schedule_id, start_time, end_time, address, latitude, longitude, time_zone, locale))
        self.cur.execute("INSERT INTO temp_schedule(schedule_id, start_time, end_time, address) VALUES (?,?,?,?)",
                         (schedule_id, start_date, end_date, address))
        self.con.commit()
        return schedule_id

    def delete_location_history(self, schedule_id):
        self.cur.execute("DELETE FROM temp_person_schedule WHERE schedule_id=?", (schedule_id,))
        self.cur.execute("DELETE FROM temp_schedule WHERE schedule_id=?", (schedule_id,))
        self.con.commit()

    def modify_location_history(self, schedule_id, start_date, end_date, address):
        self.cur.execute("UPDATE temp_schedule SET start_time=?, end_time=?, address=? WHERE schedule_id=?",
                         (start_date, end_date, address, schedule_id))
        self.con.commit()

    def get_post(self, num: int, start_date, end_date, schedule: list, short_profile):
        posts = self.gen.get_post(num, start_date, end_date, schedule, short_profile)
        return posts

    def savePicture(self, img, img_path):
        # real_path: use for storing in Imgs/
        # store_path: use for storing in table
        imgData = base64.b64decode(img)
        image_name = str(uuid.uuid4()) + ".jpg"

        real_path = img_path + image_name
        real_path = os.path.join(img_path, image_name)
        store_path = "http://127.0.0.1:5000/Imgs/" + image_name

        # store_path = "http://localhost:xxxx/Imgs/" + image_name
        print('real_path:', real_path)
        if not os.path.exists(img_path):
            print("No such path-in fill_information")
            os.makedirs(img_path)

        with open(real_path, "wb") as image_file:
            image_file.write(imgData)
        return store_path

    # add guidance before calling gen_persona()
    def fill_information(self, guidance):
        print("guidance in fill_infor:")
        print(guidance)
        # self.add_guidance(guidance)
        print("Generating persona profile...")
        persona_profile = self.get_persona_profile(guidance)
        print("Generating persona attributes...")
        attributes = self.get_attributes(persona_profile)
        print("Generating profile img...")

        persona_id = self.get_persona_id()

        persona_img = self.get_profile_img(age=attributes["age"], race=attributes["race"], gender=attributes["gender"],
                                           job=attributes["job"])

        # {"base64_json": self.profile_img, "url": self.profile_img_url}
        # -------------------------
        # use for storing
        persona_img_store = self.savePicture(persona_img["base64_json"], img_path)

        self.cur.execute("""INSERT INTO temp_information(persona_id, first_name, last_name, age, birthday,
        race, gender, street, city, state, zip_code, job, income, parental_status,
        marital_status, spoken_language, education_background, profile_img_url, profile, online_behavior) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""", (
            persona_id,
            attributes["first_name"],
            attributes["last_name"],
            attributes["age"],
            attributes["birthday"],
            attributes["race"],
            attributes["gender"],
            attributes["street"],
            attributes["city"],
            attributes["state"],
            attributes["zip_code"],
            attributes["job"],
            attributes["income"],
            attributes["parental_status"],
            attributes["marital_status"],
            attributes["spoken_language"],
            attributes["education_background"],
            persona_img_store,
            persona_profile,
            attributes["online_behavior"]
        ))
        self.con.commit()

        return [persona_id,
                attributes["first_name"],
                attributes["last_name"],
                attributes["age"],
                attributes["birthday"],
                attributes["race"],
                attributes["gender"],
                attributes["street"],
                attributes["city"],
                attributes["state"],
                attributes["zip_code"],
                attributes["job"],
                attributes["income"],
                attributes["parental_status"],
                attributes["marital_status"],
                attributes["spoken_language"],
                attributes["education_background"],
                persona_img["url"],
                persona_profile,
                attributes["online_behavior"]
                ]

    def fill_browsing_history(self, persona_id, bh_start_date='2023-05-16 10:00:00',
                              bh_end_date='2023-05-17 23:59:59',
                              num_bh=5, schedule=[]):
        print("Generating browsing history...")
        # delete the original bh
        # self.cur.execute("CREATE TABLE person_history(persona_id, browsing_history_id);")
        # self.cur.execute("CREATE TABLE browsing_history(browsing_history_id, time, title, url);")
        self.cur.execute(f"DELETE FROM temp_browsing_history WHERE browsing_history_id in (SELECT browsing_history_id "
                         f"FROM temp_person_history WHERE persona_id={persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM person_history WHERE persona_id={persona_id}".format(persona_id=persona_id))
        # get profile
        self.cur.execute(
            f"SELECT profile FROM temp_information WHERE persona_id={persona_id};".format(persona_id=persona_id))
        profile = self.cur.fetchone()
        final_browsing_history = self.gen.generate_browser_history(profile=profile, start_date=bh_start_date,
                                                                   end_date=bh_end_date,
                                                                   num=num_bh, schedule=schedule)
        self.browsing_history = final_browsing_history

        browsing_history = []
        for i in range(len(final_browsing_history)):
            browsing_history_id = self.get_browsing_history_id()
            self.cur.execute("""
                    INSERT INTO temp_person_history(persona_id, browsing_history_id) VALUES (?, ?);""",
                             (persona_id, browsing_history_id))

            self.cur.execute("""
                    INSERT INTO temp_browsing_history(browsing_history_id, time, title, url) VALUES
                        (?, ?, ?, ?);""", (browsing_history_id, final_browsing_history[i][0],
                                           final_browsing_history[i][1], final_browsing_history[i][2]))

            browsing_history.append([persona_id, browsing_history_id, final_browsing_history[i][0],
                                     final_browsing_history[i][1], final_browsing_history[i][2]])
        self.con.commit()

        return browsing_history

    # def retreiveTwitter(self, user):
    def twitter(self, persona_id, location_history, lh_start_date='2023-05-16 10:00:00',
                lh_end_date='2023-05-17 23:59:59',
                num_posts=3):
        print("Generating twitter posts...")
        self.cur.execute(f"DELETE FROM temp_twitter_posts_info WHERE post_id in (SELECT post_id "
                         f"FROM temp_twitter_posts WHERE persona_id={persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM temp_twitter_posts_img_url WHERE post_id in (SELECT post_id "
                         f"FROM temp_twitter_posts WHERE persona_id={persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM temp_twitter_posts WHERE persona_id={persona_id}".format(persona_id=persona_id))

        self.cur.execute(f"SELECT age, race, gender, job from temp_information WHERE persona_id={persona_id}".format(
            persona_id=persona_id))
        a_r_g_j = self.cur.fetchone()
        age, race, gender, job = a_r_g_j[0], a_r_g_j[1], a_r_g_j[2], a_r_g_j[3]
        short_profile = self.get_persona_short_profile(age, race, gender, job)

        twitter_posts = self.get_post(num=num_posts, start_date=lh_start_date, end_date=lh_end_date,
                                      schedule=location_history, short_profile=short_profile)

        self.twitter_posts = twitter_posts
        # [[time, content, address, fake latitude, fake longitude, time_zone, locale, [img_url], [img_文件路径]].
        twitter_posts_list = []
        for i in range(len(twitter_posts)):
            twitter_post_id = self.get_twitter_post_id()
            self.cur.execute("""
                        INSERT INTO temp_twitter_posts(persona_id, post_id) VALUES
                            (?, ?);
                        """, (persona_id, twitter_post_id))
            self.cur.execute("""
                        INSERT INTO temp_twitter_posts_info(post_id, time, address, content, latitude, longitude, time_zone, locale) VALUES
                            (?, ?, ?, ?, ?, ?, ?, ?);""",
                             (twitter_post_id, twitter_posts[i][0], twitter_posts[i][2], twitter_posts[i][1],
                              twitter_posts[i][3], twitter_posts[i][4], twitter_posts[i][5], twitter_posts[i][6]))

            for j in range(len(twitter_posts[i][8])):
                img_store = self.savePicture(twitter_posts[i][8][j], img_path)
                self.cur.execute("""
                        INSERT INTO temp_twitter_posts_img_url(post_id, img_url) VALUES
                            (?, ?);""", (twitter_post_id, img_store))
            twitter_posts_list.append([twitter_post_id, twitter_posts[i]])
        self.con.commit()
        return twitter_posts_list
        # [   [twitter_post_id, [time, address, content, fake latitude, fake longitude, time_zone, locale, [img] ]  ]]

    def facebook(self, persona_id, location_history, lh_start_date='2023-05-16 10:00:00',
                 lh_end_date='2023-05-17 23:59:59',
                 num_posts=3):
        print("Generating facebook posts...")
        self.cur.execute(f"DELETE FROM temp_facebook_posts_info WHERE post_id in (SELECT post_id "
                         f"FROM temp_facebook_posts WHERE persona_id={persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM temp_facebook_posts_img_url WHERE post_id in (SELECT post_id "
                         f"FROM temp_facebook_posts WHERE persona_id={persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM temp_facebook_posts WHERE persona_id={persona_id}".format(persona_id=persona_id))

        self.cur.execute(f"SELECT age, race, gender, job from temp_information WHERE persona_id={persona_id}".format(
            persona_id=persona_id))
        a_r_g_j = self.cur.fetchone()
        age, race, gender, job = a_r_g_j[0], a_r_g_j[1], a_r_g_j[2], a_r_g_j[3]
        short_profile = self.get_persona_short_profile(age, race, gender, job)

        facebook_posts = self.get_post(num=num_posts, start_date=lh_start_date, end_date=lh_end_date,
                                       schedule=location_history, short_profile=short_profile)

        self.facebook_posts = facebook_posts
        # [[time, content, address, fake latitude, fake longitude, time_zone, locale, [img_url], [img_文件路径]].
        facebook_posts_list = []
        for i in range(len(facebook_posts)):
            facebook_post_id = self.get_facebook_post_id()
            self.cur.execute("""
                        INSERT INTO temp_facebook_posts(persona_id, post_id) VALUES
                            (?, ?);
                        """, (persona_id, facebook_post_id))
            self.cur.execute("""
                        INSERT INTO temp_facebook_posts_info(post_id, time, address, content, latitude, longitude, time_zone, locale) VALUES
                            (?, ?, ?, ?, ?, ?, ?, ?);""",
                             (facebook_post_id, facebook_posts[i][0], facebook_posts[i][2], facebook_posts[i][1],
                              facebook_posts[i][3], facebook_posts[i][4], facebook_posts[i][5], facebook_posts[i][6]))

            for j in range(len(facebook_posts[i][8])):
                img_store = self.savePicture(facebook_posts[i][8][j], img_path)
                self.cur.execute("""
                        INSERT INTO temp_facebook_posts_img_url(post_id, img_url) VALUES
                            (?, ?);""", (facebook_post_id, img_store))
            facebook_posts_list.append([facebook_post_id, facebook_posts[i]])

        self.con.commit()
        return facebook_posts_list
        # [   [facebook_post_id, [time, address, content, fake latitude, fake longitude, time_zone, locale, [img] ]  ]]

    # def gen_persona_new(self, guidance="", bh_start_date='2023-05-16 10:00:00', bh_end_date='2023-05-17 23:59:59',
    #                     lh_start_date='2023-05-16 10:00:00', lh_end_date='2023-05-17 23:59:59',
    #                     num_bh=5, num_posts=3):
    #
    #     self.fill_information(guidance)
    #     self.fill_browsing_history(bh_start_date=bh_start_date, bh_end_date=bh_end_date, num_bh=num_bh)
    #     location_history = self.get_location_history(start_date=lh_start_date, end_date=lh_end_date)
    #     self.twitter(location_history=location_history, lh_start_date=lh_start_date, lh_end_date=lh_end_date,
    #                  num_posts=num_posts)
    #     self.facebook(location_history=location_history, lh_start_date=lh_start_date, lh_end_date=lh_end_date,
    #                   num_posts=num_posts)

    # store the data in temp table when the user click confirm
    def confirm_persona(self):
        '''
        Store the temporary data into the permanent table, then clean the temporary table
        '''

        self.cur.execute("SELECT * FROM temp_information;")
        res1 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO information VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);', res1)
        # self.cur.execute("DELETE FROM temp_information")

        self.cur.execute("SELECT * FROM temp_person_history;")
        res0 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO person_history VALUES (?,?);', res0)
        # self.cur.execute("DELETE FROM temp_browsing_history")

        self.cur.execute("SELECT * FROM temp_browsing_history;")
        res2 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO browsing_history VALUES (?,?,?,?);', res2)
        # self.cur.execute("DELETE FROM temp_browsing_history")

        self.cur.execute("SELECT * FROM temp_twitter_posts;")
        res3 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO twitter_posts VALUES (?,?);', res3)

        self.cur.execute("SELECT * FROM temp_twitter_posts_info;")
        res4 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO twitter_posts_info VALUES (?,?,?,?,?,?,?,?);', res4)

        self.cur.execute("SELECT * FROM temp_twitter_posts_img_url;")
        res5 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO twitter_posts_img_url VALUES (?,?);', res5)

        self.cur.execute("SELECT * FROM temp_facebook_posts;")
        res6 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO facebook_posts VALUES (?,?);', res6)

        self.cur.execute("SELECT * FROM temp_facebook_posts_info;")
        res7 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO facebook_posts_info VALUES (?,?,?,?,?,?,?,?);', res7)

        self.cur.execute("SELECT * FROM temp_facebook_posts_img_url;")
        res8 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO facebook_posts_img_url VALUES (?,?);', res8)

        self.cur.execute("SELECT * FROM temp_person_schedule;")
        res9 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO person_schedule VALUES (?,?);', res9)

        self.cur.execute("SELECT * FROM temp_schedule;")
        res10 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?);', res10)

        self.clean_temp_table()
        self.con.commit()

    def load_persona(self, persona_id):
        self.cur.execute(f"SELECT * FROM information WHERE persona_id = {persona_id};".format(persona_id=persona_id))
        res0 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_information VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);',
                             res0)
        self.cur.execute(f"DELETE FROM information WHERE persona_id = {persona_id};".format(persona_id=persona_id))

        # browsing history
        self.cur.execute(
            f"SELECT * FROM person_history WHERE persona_id = {persona_id};".format(persona_id=persona_id))
        res1 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_person_history VALUES (?,?);', res1)

        self.cur.execute(
            f"SELECT * FROM browsing_history WHERE browsing_history_id IN (SELECT browsing_history_id FROM person_history WHERE persona_id = {persona_id});".format(
                persona_id=persona_id))
        res2 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_browsing_history VALUES (?,?,?,?);', res2)

        self.cur.execute(
            f"DELETE FROM browsing_history WHERE browsing_history_id IN (SELECT browsing_history_id FROM person_history WHERE persona_id = {persona_id});".format(
                persona_id=persona_id))
        self.cur.execute(f"DELETE FROM person_history WHERE persona_id = {persona_id};".format(persona_id=persona_id))

        # twitter posts
        self.cur.execute(f"SELECT * FROM twitter_posts WHERE persona_id = {persona_id};".format(persona_id=persona_id))
        res3 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_twitter_posts VALUES (?,?);', res3)

        self.cur.execute("SELECT * FROM twitter_posts_info WHERE post_id IN (SELECT post_id from twitter_posts "
                         f"WHERE persona_id = {persona_id});".format(persona_id=persona_id))
        res4 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_twitter_posts_info VALUES (?,?,?,?,?,?,?,?);', res4)

        self.cur.execute("SELECT * FROM twitter_posts_img_url WHERE post_id IN (SELECT post_id from twitter_posts "
                         "WHERE persona_id = ?)", (persona_id,))

        res5 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_twitter_posts_img_url VALUES (?,?);', res5)

        self.cur.execute("DELETE FROM twitter_posts_info WHERE post_id IN (SELECT post_id from twitter_posts "
                         f"WHERE persona_id = {persona_id});".format(persona_id=persona_id))
        self.cur.execute("DELETE FROM twitter_posts_img_url WHERE post_id IN (SELECT post_id from twitter_posts "
                         f"WHERE persona_id = {persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM twitter_posts WHERE persona_id = {persona_id};".format(persona_id=persona_id))

        # facebook posts
        self.cur.execute(f"SELECT * FROM facebook_posts WHERE persona_id = {persona_id};".format(persona_id=persona_id))
        res6 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_facebook_posts VALUES (?,?);', res6)

        self.cur.execute("SELECT * FROM facebook_posts_info WHERE post_id IN (SELECT post_id from facebook_posts "
                         f"WHERE persona_id = {persona_id});".format(persona_id=persona_id))
        res7 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_facebook_posts_info VALUES (?,?,?,?,?,?,?,?);', res7)

        self.cur.execute("SELECT * FROM facebook_posts_img_url WHERE post_id IN (SELECT post_id from facebook_posts "
                         "WHERE persona_id = ?)", (persona_id,))

        res8 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_facebook_posts_img_url VALUES (?,?);', res8)

        self.cur.execute("DELETE FROM facebook_posts_info WHERE post_id IN (SELECT post_id from facebook_posts "
                         f"WHERE persona_id = {persona_id});".format(persona_id=persona_id))
        self.cur.execute("DELETE FROM facebook_posts_img_url WHERE post_id IN (SELECT post_id from facebook_posts "
                         f"WHERE persona_id = {persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM facebook_posts WHERE persona_id = {persona_id};".format(persona_id=persona_id))

        # schedule
        self.cur.execute(
            f"SELECT * FROM person_schedule WHERE persona_id = {persona_id};".format(persona_id=persona_id))
        res9 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_person_schedule VALUES (?,?);', res9)

        self.cur.execute("SELECT * FROM schedule WHERE schedule_id IN (SELECT schedule_id FROM person_schedule WHERE "
                         f"persona_id = {persona_id});".format(persona_id=persona_id))
        res10 = self.cur.fetchall()
        self.cur.executemany('INSERT INTO temp_schedule VALUES (?,?,?,?,?,?,?,?);', res10)

        self.cur.execute("DELETE FROM schedule WHERE schedule_id IN (SELECT schedule_id FROM person_schedule WHERE "
                         f"persona_id = {persona_id});".format(persona_id=persona_id))
        self.cur.execute(f"DELETE FROM person_schedule WHERE persona_id = {persona_id}".format(persona_id=persona_id))

        self.con.commit()

    # you should click confirm before loading another persona

    def get_all_users(self, persona_id):
        if persona_id is None:
            self.cur.execute("SELECT * FROM information;")
        else:
            persona_id = int(persona_id)
            self.load_persona(persona_id=persona_id)
            self.cur.execute(
                f"SELECT * FROM temp_information WHERE persona_id={persona_id};".format(persona_id=persona_id))
        res = self.cur.fetchall()
        return res

    # directly store the new profile in the temp table
    def edit_persona_profile(self, persona_id, profile):
        self.cur.execute(
            "UPDATE temp_information SET profile = {profile} where persona_id = {persona_id};".format(
                persona_id=persona_id, profile=profile))
        self.con.commit()

    def edit_profile_img_url(self, persona_id, profile_img_url):
        self.cur.execute(
            "UPDATE temp_information SET profile_img_url = {profile_img_url} where persona_id = {persona_id};".format(
                persona_id=persona_id,
                profile_img_url=profile_img_url))
        self.con.commit()

    def edit_persona_age(self, persona_id, age):
        self.cur.execute(
            "UPDATE temp_information SET age = {age} where persona_id = {persona_id};".format(persona_id=persona_id,
                                                                                              age=age))
        self.con.commit()

    def edit_persona_birthday(self, persona_id, birthday):
        self.cur.execute(
            "UPDATE temp_information SET birthday = {birthday} where persona_id = {persona_id};".format(
                persona_id=persona_id, birthday=birthday))
        self.con.commit()

    def edit_persona_ethic_origin(self, persona_id, race):
        self.cur.execute(
            "UPDATE temp_information SET race = {race} where persona_id = {persona_id};".format(persona_id=persona_id,
                                                                                                race=race))
        self.con.commit()

    def edit_persona_home_address_street(self, persona_id, street):
        self.cur.execute(
            "UPDATE temp_information SET street = {street} where persona_id = {persona_id};".format(
                persona_id=persona_id, street=street))
        self.con.commit()

    def edit_persona_home_address_city(self, persona_id, city):
        self.cur.execute(
            "UPDATE temp_information SET city = {city} where persona_id = {persona_id};".format(persona_id=persona_id,
                                                                                                city=city))
        self.con.commit()

    def edit_persona_home_address_state(self, persona_id, state):
        self.cur.execute(
            "UPDATE temp_information SET state = {state} where persona_id = {persona_id};".format(persona_id=persona_id,
                                                                                                  state=state))
        self.con.commit()

    def edit_persona_home_address_zip_code(self, persona_id, zip_code):
        self.cur.execute(
            "UPDATE temp_information SET zip_code = {zip_code} where persona_id = {persona_id};".format(
                persona_id=persona_id, zip_code=zip_code))
        self.con.commit()

    def edit_persona_job(self, persona_id, job):
        self.cur.execute(
            "UPDATE temp_information SET job = {job} where persona_id = {persona_id};".format(persona_id=persona_id,
                                                                                              job=job))
        self.con.commit()

    def edit_persona_income(self, persona_id, income):
        self.cur.execute(
            "UPDATE temp_information SET income = {income} where persona_id = {persona_id};".format(
                persona_id=persona_id, income=income))
        self.con.commit()

    def edit_persona_marital_status(self, persona_id, marital_status):
        self.cur.execute(
            "UPDATE temp_information SET marital_status = {marital_status} where persona_id = {persona_id};".format(
                persona_id=persona_id,
                marital_status=marital_status))
        self.con.commit()

    def edit_persona_parental_status(self, persona_id, parental_status):
        self.cur.execute(
            "UPDATE temp_information SET parental_status = {parental_status} where persona_id = {persona_id};".format(
                persona_id=persona_id,
                parental_status=parental_status))
        self.con.commit()

    def edit_persona_spoken_language(self, persona_id, spoken_language):
        self.cur.execute(
            "UPDATE temp_information SET spoken_language = {spoken_language} WHERE persona_id = {persona_id};".format(
                persona_id=persona_id,
                spoken_language=spoken_language))
        self.con.commit()

    def edit_persona_education_background(self, persona_id, education_background):
        self.cur.execute(
            "UPDATE temp_information SET education_background = {education_background} where persona_id = {persona_id};".format(
                persona_id=persona_id,
                education_background=education_background))
        self.con.commit()

    def edit_persona_online_behavior(self, persona_id, online_behavior):
        self.cur.execute(
            "UPDATE temp_information SET online_behavior = {online_behavior} where persona_id = {persona_id};".format(
                persona_id=persona_id,
                online_behavior=online_behavior))
        self.con.commit()

    def edit_persona_device(self, persona_id, device):
        self.cur.execute(
            "UPDATE temp_information SET device = {device} where persona_id = {persona_id};".format(
                persona_id=persona_id, device=device))
        self.con.commit()

    def edit_persona_browser(self, persona_id, browser):
        self.cur.execute(
            "UPDATE temp_information SET browser = {browser} where persona_id = {persona_id};".format(
                persona_id=persona_id, browser=browser))
        self.con.commit()

    def return_twitter_post(self, persona_id):
        twitter_posts_list = []

        self.cur.execute(
            f"SELECT post_id FROM temp_twitter_posts WHERE persona_id = {persona_id};".format(persona_id=persona_id))
        res1 = self.cur.fetchall()
        # print("res1")
        # print(res1)
        for post_id_tuple in res1:
            post_id = post_id_tuple[0]

            self.cur.execute(
                f"SELECT time, address, content FROM temp_twitter_posts_info WHERE post_id = {post_id};".format(
                    post_id=post_id))
            res2 = self.cur.fetchone()
            time = res2[0]
            address = res2[1]
            content = res2[2]

            self.cur.execute(
                f"SELECT img_url FROM temp_twitter_posts_img_url WHERE post_id = {post_id};".format(post_id=post_id))
            res3 = self.cur.fetchall()
            imgs = [img_url_tuple[0] for img_url_tuple in res3]

            t_dict = {'id': post_id, 'time': time, 'address': address, 'content': content, 'imgs': imgs}
            twitter_posts_list.append(t_dict)

        return twitter_posts_list

    def return_facebook_post(self, persona_id):
        facebook_posts_list = []

        self.cur.execute(
            f"SELECT post_id FROM temp_facebook_posts WHERE persona_id = {persona_id};".format(persona_id=persona_id))
        res1 = self.cur.fetchall()
        # print("res1")
        # print(res1)
        for post_id_tuple in res1:
            post_id = post_id_tuple[0]

            self.cur.execute(
                f"SELECT time, address, content FROM temp_facebook_posts_info WHERE post_id = {post_id};".format(
                    post_id=post_id))
            res2 = self.cur.fetchone()
            time = res2[0]
            address = res2[1]
            content = res2[2]

            self.cur.execute(
                f"SELECT img_url FROM temp_facebook_posts_img_url WHERE post_id = {post_id};".format(post_id=post_id))
            res3 = self.cur.fetchall()
            imgs = [img_url_tuple[0] for img_url_tuple in res3]

            f_dict = {'id': post_id, 'time': time, 'address': address, 'content': content, 'imgs': imgs}
            facebook_posts_list.append(f_dict)

        return facebook_posts_list

    def return_browsing_history(self, persona_id):
        browsing_history_list = []

        self.cur.execute(f"SELECT browsing_history_id FROM temp_person_history WHERE persona_id= {persona_id};".format(
            persona_id=persona_id))
        res1 = self.cur.fetchall()
        # print(res1)
        for browsing_history_id_tuple in res1:
            browsing_history_id = browsing_history_id_tuple[0]

            self.cur.execute(
                f"SELECT time, title, url FROM temp_browsing_history WHERE browsing_history_id ={browsing_history_id};".format(
                    browsing_history_id=browsing_history_id))
            res2 = self.cur.fetchone()
            # print(res2)
            time = res2[0]
            title = res2[1]
            url = res2[2]

            bh_dict = {'id': browsing_history_id, 'time': time, 'title': title, 'url': url}
            browsing_history_list.append(bh_dict)
        # print("browsing_history_list")
        # print(browsing_history_list)
        return browsing_history_list

    def return_schedule(self, persona_id):
        schedule_list = []

        self.cur.execute(f"SELECT schedule_id FROM temp_person_schedule WHERE persona_id = {persona_id};")
        res1 = self.cur.fetchall()

        for schedule_id_tuple in res1:
            schedule_id = schedule_id_tuple[0]

            self.cur.execute(f"SELECT start_time, end_time, address, latitude, longitude, time_zone, locale FROM "
                             f"temp_schedule WHERE schedule_id = {schedule_id};")
            res2 = self.cur.fetchone()

            start = res2[0]
            end = res2[1]
            address = res2[2]
            latitude = res2[3]
            longitude = res2[4]
            time_zone = res2[5]
            locale = res2[6]

            schedule_dict = {
                'id': schedule_id,
                'start': start,
                'end': end,
                'address': address,
                'latitude': latitude,
                'longitude': longitude,
                'timeZone': time_zone,
                'locale': locale
            }
            schedule_list.append(schedule_dict)

        # print(schedule_list)
        return schedule_list

    # regenerate schedule when user modify it
    def get_brief_schedule(self, persona_id):
        schedule_list = []

        self.cur.execute("SELECT schedule_id FROM temp_person_schedule WHERE persona_id= {persona_id};".format(
            persona_id=persona_id))
        res1 = self.cur.fetchall()
        for schedule_id_tuple in res1:
            schedule_id = schedule_id_tuple[0]

            self.cur.execute("SELECT start_time, end_time, address, latitude, longitude, time_zone, locale FROM "
                             f"temp_schedule WHERE schedule_id = {schedule_id}".format(
                schedule_id=schedule_id))
            res2 = self.cur.fetchone()
            schedule_list.append(list(res2))
        # Transfer the rows into a list of lists

        return schedule_list

    # def add_post(self, platform, persona_id, post_id, send_time, location, content, img_url: list):
    def add_post(self, platform, persona_id, time, content, img_url=[]):
        if platform == "twitter":
            post_id = self.get_twitter_post_id()
        else:
            post_id = self.get_facebook_post_id()
        table_name1 = "temp_" + platform + "_posts"
        table_name2 = "temp_" + platform + "_posts_info"
        table_name3 = "temp_" + platform + "_posts_img_url"
        self.cur.execute("""
                    INSERT INTO {table_name1} VALUES
                        ({persona_id}, {post_id});
                    """.format(table_name1=table_name1, persona_id=persona_id, post_id=post_id))
        self.cur.execute("""
            INSERT INTO {table_name2} (post_id, time, content)
            VALUES (?, ?, ?)
            """.format(table_name2=table_name2), (post_id, time, content))

        for i in range(len(img_url)):
            self.cur.execute("""
                INSERT INTO {table_name3} (post_id, img_url)
                VALUES (?, ?)
            """.format(table_name3=table_name3), (post_id, img_url[i]))

        self.con.commit()

    def delete_post(self, platform, post_id):
        table_name1 = "temp_" + platform + "_posts"
        table_name2 = "temp_" + platform + "_posts_info"
        table_name3 = "temp_" + platform + "_posts_img_url"
        self.cur.execute("""
                DELETE FROM {table_name1} WHERE post_id={post_id}
        """.format(table_name1=table_name1, post_id=post_id))

        self.cur.execute("""
                DELETE FROM {table_name2} WHERE post_id={post_id}
        """.format(table_name2=table_name2, post_id=post_id))

        self.cur.execute("""
                        DELETE FROM {table_name3} WHERE post_id={post_id}
                """.format(table_name3=table_name3, post_id=post_id))
        self.con.commit()

    def modify_post(self, platform, post_id, time, content, img_url=[]):
        table_name1 = "temp_" + platform + "_posts"
        table_name2 = "temp_" + platform + "_posts_info"
        table_name3 = "temp_" + platform + "_posts_img_url"

        self.cur.execute("UPDATE {table_name2} SET time=?, content=? WHERE post_id=?".format(table_name2=table_name2),
                         (time, content, post_id))

        # self.cur.execute("DELETE FROM {table_name3} WHERE post_id=?".format(table_name3=table_name3), post_id)
        self.cur.execute("DELETE FROM {table_name3} WHERE post_id=?".format(table_name3=table_name3), (post_id,))

        for i in range(len(img_url)):
            self.cur.execute(
                "INSERT INTO {table_name3} (post_id, img_url) VALUES (?, ?)".format(table_name3=table_name3),
                (post_id, img_url[i]))

        self.con.commit()

    def add_browsing_history(self, persona_id, time="", title="", url=""):
        browsing_history_id = self.get_browsing_history_id()

        # Insert into temp_person_history table
        self.cur.execute("INSERT INTO temp_person_history VALUES (?, ?);", (persona_id, browsing_history_id))

        # Insert into temp_browsing_history table
        self.cur.execute("INSERT INTO temp_browsing_history VALUES (?, ?, ?, ?);",
                         (browsing_history_id, time, title, url))

        self.con.commit()

    def delete_browsing_history(self, browsing_history_id):
        self.cur.execute(f"DELETE from temp_browsing_history WHERE browsing_history_id = {browsing_history_id}")
        self.cur.execute(f"DELETE from temp_person_history WHERE browsing_history_id = {browsing_history_id}")
        self.con.commit()

    def modify_browsing_history(self, browsing_history_id, time, title, url):
        self.cur.execute("UPDATE temp_browsing_history SET time=?, title=?, url=? WHERE browsing_history_id=?",
                         (time, title, url, browsing_history_id))
        self.con.commit()

    # def edit_browsing_history(self, persona_id, browsing_history_id, instruction, time="", title="", url=""):
    #     '''
    #
    #     :param mod_item:        add,
    #                             delete,
    #                             modified(time:1, title:2, url:3 nothing:0):
    #     :param url:
    #     :param title:
    #     :param time:
    #     :param persona_id: persona_id
    #     :param instruction:
    #
    #     (if you want to modify time, you need to set mod_item=1 and input title and url as label and input time to be the modified content)
    #
    #     '''
    #     if instruction == "add":
    #         self.cur.execute(
    #             "INSERT INTO temp_browsing_history VALUES ({persona_id}, {browsing_history_id}, {time}, {title}, {url};)".
    #             format(persona_id=persona_id, browsing_history_id=self.get_browsing_history_id(), time=time,
    #                    title=title,
    #                    url=url))
    #     elif instruction == "delete":
    #         self.cur.execute('''DELETE from temp_browsing_history WHERE persona_id={persona_id} AND
    #         browsing_history_id={browsing_history_id}";'''.format(persona_id=persona_id,
    #                                                               browsing_history_id=browsing_history_id))
    #     elif instruction == "modified":
    #         self.cur.execute('''UPDATE temp_browsing_history SET time = {time}, title = "{title}, url = "{url}
    #         WHERE persona_id={persona_id} AND browsing_history_id={browsing_history_id};'''.format(
    #             persona_id=persona_id, browsing_history_id=browsing_history_id, time=time, title=title, url=url))
    #     else:
    #         pass
    #     self.con.commit()
    def get_ip(self, persona_id):
        self.cur.execute(f"SELECT city from temp_information WHERE persona_id={persona_id}".format(
            persona_id=persona_id))
        res = self.cur.fetchone()
        # print(res)
        city = res[0]
        ip, ip_location = connect_to_vpn(city)
        # print(ip)
        # print(ip_location)
        self.cur.execute(
            "UPDATE temp_information SET ip = ?, ip_location = ? WHERE persona_id = ?",
            (ip, ip_location, persona_id))
        self.con.commit()
        return [ip, ip_location]

    def modify_ip(self, persona_id, ip, ip_location):
        self.cur.execute(
            "UPDATE temp_information SET ip = ?, ip_location = ? WHERE persona_id = ?",
            (ip, ip_location, persona_id))
        self.con.commit()

    def modify_device_browser(self, persona_id, device, browser):
        self.cur.execute(
            "UPDATE temp_information SET device = ?, browser = ? WHERE persona_id = ?",
            (device, browser, persona_id))
        self.con.commit()

    def get_location_history_in_time_range(self, start_time, end_time, total_location_history):
        original_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        original_end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        location_history = []
        for location_history_cut in total_location_history:
            new_start = datetime.strptime(location_history_cut[0], '%Y-%m-%d %H:%M:%S')
            new_end = datetime.strptime(location_history_cut[1], '%Y-%m-%d %H:%M:%S')

            if original_start <= new_start and original_end >= new_end:
                location_history.append(location_history_cut)

        return location_history

    # clean the data in temp table when the user click cancel
    def clean_temp_table(self):
        self.cur.execute("DELETE FROM temp_information;")
        self.cur.execute("DELETE FROM temp_person_history;")
        self.cur.execute("DELETE FROM temp_browsing_history;")

        self.cur.execute("DELETE FROM temp_twitter_posts;")
        self.cur.execute("DELETE FROM temp_twitter_posts_info;")
        self.cur.execute("DELETE FROM temp_twitter_posts_img_url;")

        self.cur.execute("DELETE FROM temp_facebook_posts;")
        self.cur.execute("DELETE FROM temp_facebook_posts_info;")
        self.cur.execute("DELETE FROM temp_facebook_posts_img_url;")

        self.cur.execute("DELETE FROM temp_person_schedule;")
        self.cur.execute("DELETE FROM temp_schedule;")

        self.con.commit()

    def convert_to_daily_schedule(self, schedule, num_day):
        daily_schedules = [[] for _ in range(num_day)]  # Create 7 empty lists for each day

        for event in schedule:
            start_time = event[0]  # Get the start time of the event
            day = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').date()  # Extract the day

            # Calculate the day index by subtracting the first day's index
            day_index = (day - datetime.strptime(schedule[0][0], '%Y-%m-%d %H:%M:%S').date()).days

            # Append the event to the corresponding day's schedule
            print("day_index: ",day_index)
            daily_schedules[day_index-1].append(event)

        return daily_schedules

    def generate_random_list(self, count, num_day):
        numbers = []
        remaining_sum = count
        for _ in range(num_day):
            # Generate a random number between 0 and the remaining sum
            number = random.randint(0, remaining_sum)
            numbers.append(number)
            remaining_sum -= number

        numbers.append(remaining_sum)  # Add the remaining sum as the last number
        return numbers

    def calculate_days(self, start_date, end_date):
        date_format = '%Y-%m-%d %H:%M:%S'
        start_datetime = datetime.strptime(start_date, date_format)
        end_datetime = datetime.strptime(end_date, date_format)

        duration = end_datetime - start_datetime
        days = duration.days

        return days

    def calculate_weeks(self, d1, d2):
        # d1 schedule[-1][1]
        # d2 end_date
        # Convert the date strings to datetime objects
        d1 = datetime.strptime(d1, '%Y-%m-%d %H:%M:%S')
        d2 = datetime.strptime(d2, '%Y-%m-%d %H:%M:%S')

        if d1 >= d2:
            return 0
        # Calculate the difference between d2 and d1
        date_diff = d2 - d1
        # Calculate the number of weeks
        weeks = date_diff.days // 7

        # If there is a remainder, add 1 to the weeks count
        if date_diff.days % 7 != 0:
            weeks += 1

        return weeks

    def expand_schedule(self, original_schedule, num_expand):
        expanded_schedule = []

        for week in range(num_expand+1):
            for event in original_schedule:
                start_time = datetime.strptime(event[0], '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(event[1], '%Y-%m-%d %H:%M:%S')

                # Add num_expand * 7 days to the start and end time
                new_start_time = start_time + timedelta(days=week * 7)
                new_end_time = end_time + timedelta(days=week * 7)

                # Convert back to string format
                new_start_time_str = new_start_time.strftime('%Y-%m-%d %H:%M:%S')
                new_end_time_str = new_end_time.strftime('%Y-%m-%d %H:%M:%S')

                # Create a new event with the updated times
                new_event = [new_start_time_str, new_end_time_str] + event[2:]
                expanded_schedule.append(new_event)

        return expanded_schedule

if __name__ == '__main__':
    db = Database()
    # #     #     # add guidance
    #     guidance = "The person should be in upper class."
    db.gen_generator()
    # res1 = db.fill_information(guidance=guidance)
    print(db.get_all_users(1))
