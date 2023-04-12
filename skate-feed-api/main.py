import requests
import psycopg2
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
from flask import render_template
from flask import request
from flask import Flask, jsonify, redirect, url_for, request
from flask_restful import Api

app = Flask(__name__, static_folder='./build', static_url_path='/')
api = Api(app)
CORS(app)
db_username = ""
db_password = ""
db_host = ""
db_database = ""

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

def getJsonData():
    try:
        with open("./skate-feed-api/source_data.json", "r") as j:
            return json.loads(j.read())["data"]
        
    except ValueError as e:
        print(e)

    return

def getDbInfo():
    try:
        with open("./skate-feed-api/dbInfo.json", "r") as j:
            data = json.loads(j.read())["data"]
            global db_username, db_password, db_host, db_database
            db_username = data['username']
            db_password = data['password']
            db_host = data['host']
            db_database = data['database']
    except ValueError as e:
        print(e)

    return

class VideoItem:
    def __init__(self, title, description, img_src, url, date, source, subsection):
        self.title = title
        self.description = description
        self.img_src = img_src
        self.url = url
        self.update_date = date
        self.source = source
        self.subsection = subsection


def get_video_data_for_page(src: dict):

    req = requests.get(src['page_url'])
    html = req.text

    soup = BeautifulSoup(html, 'lxml')

    videos = soup.find_all(src['video_container']['tag'], {src['video_container']['target_type']: src['video_container']['target_name']})

    video_list = []

    for video in videos:
        try:
            title = ""
            if video.find(src['title']['tag'], {src['title']['target_type']: src['title']['target_name']}):
                title = video.find(src['title']['tag'], {src['title']['target_type']: src['title']['target_name']}).text

            description = ""
            if video.find(src['description']['tag'], {src['description']['target_type']: src['description']['target_name']}):
                description = video.find(src['description']['tag'], {src['description']['target_type']: src['description']['target_name']}).text

            img_src = ""
            if video.find(src['img_src']['tag'], {src['img_src']['target_type']: src['img_src']['target_name']}):
                img_src = video.find(src['img_src']['tag'], {src['img_src']['target_type']: src['img_src']['target_name']}).find(src['img_src']['find_tag'])[src['img_src']['find_index']]

                if "://" not in img_src:
                    img_src = src["page_url"] + img_src
            url = ""
            if video.find(src['url']['tag'], {src['url']['target_type']: src['url']['target_name']}):
                url = video.find(src['url']['tag'], {src['url']['target_type']: src['url']['target_name']}).find(src['url']['find_tag'])[src['url']['find_index']]
                
            #Need specific find function for VHS Mag sources for url
            if src['source'] == 'VHS Mag':
                url = video.find(src['url']['find_tag'])[src['url']['find_index']]
                
            if url != "" and "://" not in url:
                url = src["page_url"] + url

            date = ""
            if video.find(src['date']['tag'], {src['date']['target_type']: src['date']['target_name']}):
                dateSrc = video.find(src['date']['tag'], {src['date']['target_type']: src['date']['target_name']}).find(src['date']['find_tag'])
                if dateSrc is None:
                    date = video.find(src['date']['tag'], {src['date']['target_type']: src['date']['target_name']}).text
                else:
                    date = dateSrc.text

            #Fix date format for place.tv videos
            if src['source'] == 'Place.tv':
                dateArr = date.split(' ')
                date = dateArr[1] + ' ' + dateArr[0].replace('.', '') + ' ' + dateArr[2]

            #Prevent duplicates (some websites have 2 of the same videos but for different languages, this will prevent pulling both)
            if len(video_list) == 0:
                video_list.append(VideoItem(title, description, img_src, url, date, src['source'], src['section']))
            elif any(video.url == url or video.img_src == img_src for video in video_list) != True:
                video_list.append(VideoItem(title, description, img_src, url, date, src['source'], src['section']))
        except Exception as e:
            print(e)

    return video_list

def already_generated_data():
    global db_username, db_password, db_host, db_database
    conn = psycopg2.connect(host=db_host, user=db_username, password=db_password, database=db_database)

    cur = conn.cursor()
    cur.execute("""Select exists(Select 1 From "ScrapeHistory" WHERE "Date" = %s AND "Success" = %s)""", 
    (datetime.today().strftime('%Y-%m-%d'), True ))
    
    if not cur.fetchone()[0]:
        return False
    return True

@app.route('/generate')
def generate_data():
    print('generating')

    if already_generated_data():
        print('data already generated today')
        return

    src_data = getJsonData()
        
    print('successfully retrieved json data')


    list_of_videos = []

    print('starting scrape process')

    for video_source in src_data:
        list_of_videos.extend(get_video_data_for_page(video_source))
        
    print('scrape proccess successful')

    print('starting connection to upload data')

    global db_username, db_password, db_host, db_database
    conn = psycopg2.connect(host=db_host, user=db_username, password=db_password, database=db_database)

    try:
        for video in list_of_videos:
            cur = conn.cursor()
            cur.execute("""Select exists(Select 1 From "Videos" WHERE "Title" = %s)""", (video.title,))

            if not cur.fetchone()[0]:
                sql = """INSERT INTO "Videos"("Title", "Description", "ImgSrc", "Url", "UploadDate", "Source", "Section", "Watched") VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""

                try:
                    cur.execute(sql, (
                    video.title, video.description, video.img_src, video.url, video.update_date, video.source,
                    video.subsection, False))
                    conn.commit()
                    cur.close()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
        
        cur = conn.cursor()
        scrape_history_update = """INSERT INTO "ScrapeHistory"("Date", "Message", "Success") Values (%s,%s,%s)"""
        cur.execute(scrape_history_update, (
            datetime.today().strftime('%Y-%m-%d'), '', True
        ))
        conn.commit()
        cur.close()

        print('successfully updloaded data to database')
    except Exception as error:
        print(error)
        scrape_history_update = """INSERT INTO "ScrapeHistory"("Date", "Message", "Success") Values (%s,%s,%s)"""
        cur.execute(scrape_history_update, (
            datetime.today().strftime('%Y-%m-%d'), error, False
        ))
        conn.commit()
        cur.close()


    if conn is not None:
        conn.close()
    return "FIN"

@app.route('/feed', methods = ['GET'])
@cross_origin(supports_credentials=True)
def get_feed_data():
    generate_data()

    global db_username, db_password, db_host, db_database
    conn = psycopg2.connect(host=db_host, user=db_username, password=db_password, database=db_database)

    cur = conn.cursor()
    sql = """SELECT * FROM "Videos" """
    dto = []

    try:
        cur.execute(sql)
        results = cur.fetchall()

        for result in results:
            data = {
                "Id": result[0],
                "Title": result[1],
                "Description": result[2],
                "ImgSrc": result[3],
                "Url": result[4],
                "UploadDate": result[5],
                "Source": result[6],
                "Section": result[7],
                "Watched": result[8]
            }
            dto.append(data)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


    if conn is not None:
        conn.close()

    dto.sort(key=lambda x: x["UploadDate"], reverse=True)
    return jsonify(dto)

if __name__ == '__main__':
    getDbInfo()
    app.run(host='0.0.0.0', debug=False, port=int(os.environ.get("PORT", 5000)))


