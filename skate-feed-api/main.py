from bs4 import BeautifulSoup
import requests
import psycopg2
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

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

class BerricsVideoItem:
    def __init__(self, title, description, img_src, url, date, source, subsection):
        self.title = title
        self.description = description
        self.img_src = img_src
        self.url = url
        self.update_date = date
        self.source = source
        self.subsection = subsection


def get_berrics_video_data_for_page(berrics_url: str, subsection: str) -> []:
    req = requests.get(berrics_url)
    src = req.text

    soup = BeautifulSoup(src, 'lxml')

    videos = soup.find_all("div", {"class": "row post"})

    video_list = []

    for video in videos:

        title = ""
        if video.find("h3", {"class": "content-title"}):
            title = video.find("h3", {"class": "content-title"}).text

        description = ""
        if video.find("div", {"class": "content-tagline"}):
            description = video.find("div", {"class": "content-tagline"}).text

        img_src = ""
        if video.find("div", {"class": "feed-teaser-col"}):
            img_src = video.find("div", {"class": "feed-teaser-col"}).find("img")["src"]

        url = ""
        if video.find("h3", {"class": "content-title"}).find("a"):
            url = video.find("h3", {"class": "content-title"}).find("a")["href"]

        date = ""
        if video.find("div", {"class": "content-meta"}).find("time"):
            date = video.find("div", {"class": "content-meta"}).find("time").text

        video_list.append(BerricsVideoItem(title, description, img_src, url, date, 'Berrics', subsection))

    return video_list

def get_reddit_video_data_for_page() -> []:
    # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
    auth = requests.auth.HTTPBasicAuth('2Neq-AW3-hteVVOD-f66bw', 'IzDkT00NWaMlTmimE7wBWiPFEyBoBA')

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': 'Puzzleheaded_Bite975',
            'password': '<PASSWORD>'}

    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'MyBot/0.0.1'}

    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    # while the token is valid (~2 hours) we just add headers=headers to our requests
    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    res = requests.get("https://oauth.reddit.com/r/skateboarding/hot",
                       headers=headers)

    print(res.json())  # let's see what we get

@app.route('/generate')
def generate_data():
    # get_reddit_video_data_for_page()

    berrics_video_source_list = [
        {"url": "https://theberrics.com/series/bangin", "section": "bangin"},
        {"url": "https://theberrics.com/series/first-try-fridays", "section": "first-try-fridays"}
    ]

    list_of_videos = []

    for video_source in berrics_video_source_list:
        list_of_videos.extend(get_berrics_video_data_for_page(video_source["url"], video_source["section"]))

    print(len(list_of_videos))

    conn = psycopg2.connect(host='ec2-52-70-186-184.compute-1.amazonaws.com',
                            database='dcuhruluoeo0tn',
                            user='vlmgxlegrduwss',
                            password='89e6c4f2f498c01a2339daf246e60d9e25f64c3b408108fd5ad4af716ea31b68')

    for video in list_of_videos:
        cur = conn.cursor()
        cur.execute("Select exists(Select 1 From video_feed WHERE title = %s)", (video.title,))

        if not cur.fetchone()[0]:
            sql = "INSERT INTO video_feed(title, description, img_src, url, update_date, source, subsection) VALUES (%s,%s,%s,%s,%s,%s,%s)"

            try:
                cur.execute(sql, (
                video.title, video.description, video.img_src, video.url, video.update_date, video.source,
                video.subsection))
                conn.commit()
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

    if conn is not None:
        conn.close()

    return "Fin"

@app.route('/feed', methods = ['GET'])
@cross_origin(supports_credentials=True)
def get_feed_data():

    # print(request.url)
    # if('http://127.0.0.1' not in request.url and 'localhost:3000' not in request.url):
    #     return "not valid request"

    conn = psycopg2.connect(host='ec2-52-70-186-184.compute-1.amazonaws.com',
                            database='dcuhruluoeo0tn',
                            user='vlmgxlegrduwss',
                            password='89e6c4f2f498c01a2339daf246e60d9e25f64c3b408108fd5ad4af716ea31b68')

    cur = conn.cursor()
    sql = "SELECT * FROM video_feed"
    data = ''

    try:
        cur.execute(sql)
        data = cur.fetchall()
        print(data)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


    if conn is not None:
        conn.close()

    return jsonify(data)

api.add_resource(get_feed_data, '/feed')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=int(os.environ.get("PORT", 5000)))


