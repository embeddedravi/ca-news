from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

pyclient = MongoClient()
pyNewsDb = pyclient.NewsDb
pyNewsCollection = pyNewsDb.NewsCollection
@app.route('/', methods=['POST', 'GET'])
def show_news():
    if request.method == 'GET':
        pageNo = request.args.get('pageNo')
        if pageNo:
            pageNo = int(pageNo)
        else:
            pageNo = 1

        news = pyNewsCollection.find({}, sort=[("createdAt", -1)], limit=100, skip=(pageNo-1)*10)
        listnews=[]
        for nn in news:
            text = nn['title']+". "+nn['intro']
            text = text.replace(r'\s+', ' ')
            nn['summary'] = text
            nn['rephrase'] = nn['summary']
            listnews.append(nn)
        return render_template('news.html', newslist = listnews)
    
    else:
        return render_template('news.html', msg='Nothing to show.')