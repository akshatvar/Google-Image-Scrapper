from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
import os

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            query = request.form['content'].replace(" ", "")

            save_dir = "images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # fake user agent to avoid getting blocked by Google
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }

            response = requests.get(f"https://www.google.com/search?q={query}&tbm=isch", headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            img_tag = soup.findAll("img")
            del img_tag[0]
            img_mongoDB = []
            for i in img_tag:
                img_url = i['src']
                img_data = requests.get(img_url).content
                mydict = {"index": img_url, "image": img_data}
                img_mongoDB.append(mydict)
                with open(os.path.join(save_dir, f"{query}_{img_tag.index(i)}.jpg"), "wb") as f:
                    f.write(img_data)

            client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.ejsgmu3.mongodb.net/?retryWrites=true&w=majority")
            db = client['my_image_scrapper']
            scap_col = db['my_image_scrap_data']
            scap_col.insert_many(img_mongoDB)
            return jsonify("image loaded")

        except Exception as e:
            logging.exception(e)
            return jsonify('something is wrong')
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
