
from requests_html import HTMLSession 
from pymongo import MongoClient
import json, base64
from datetime import datetime

NEWS18_IGNORE_CATEGORIES_LIST = ['Cricketnext', 'Movies', 'Viral']
COUNT = 50
TOTAL = 200

pages = int(TOTAL/COUNT)

list = [i for i in range(TOTAL, -1, -COUNT)]

pyclient = MongoClient()

pyNewsDb = pyclient.NewsDb

pyNewsCollection = pyNewsDb.NewsCollection

session = HTMLSession()
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36',
    'Referer': 'https://www.google.com/search?q=news18'
}

r =  session.get("https://www.news18.com/", headers=header, timeout=20)

header['Referer'] = 'https://www.news18.com/'

for thers in list:

    r =  session.get(f'https://api-en.news18.com/nodeapi/v1/eng/get-article-list?offset={thers}&count={COUNT}&fields=story_id,section,headline,created_at,updated_at,weburl,images,intro,display_headline,post_type&sortOrder=desc&sortBy=created_at', headers=header, timeout=20)
    newsList = r.json()
    newsList = newsList['data']

    # latest_created_at = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    count = 0
    # latest_document = pyNewsCollection.find_one({}, sort=[("createdAt", -1)])
    # if latest_document:
    #     latest_created_at =  latest_document['createdAt']
    docs={}
    for news in newsList:
        if len(news['section']) == 1:
            if news['section'][0] in NEWS18_IGNORE_CATEGORIES_LIST:
                continue
        response = session.get(news['images']['url'])
        if response.status_code > 400:
            # return render_template('index.html', msg=f'Failed to get image for {news["title"]}, url = {news["thumbnail"]}')
            print(f'Failed to get image for {news["headline"]}')
            exit

        news_created_at = datetime.strptime(str(news['created_at']), "%Y-%m-%d %H:%M:%S")

        # if news_created_at < latest_created_at:
        #     print(f'{count} news fected successfully. All news are up to date.')

        available_document = pyNewsCollection.find_one({"contentId": news['story_id']})
        if available_document:
            continue

        base64_image = base64.b64encode(response.content).decode("utf-8")
        image_document = {"image": base64_image}

        newDocument = {
            "title": news['headline'], 
            "category": news['section'][0] if len(news['section']) > 1 else "Others", 
            "image": image_document,
            "imageUrl": news['images']['url'],
            "url": news['weburl'],
            "createdAt": datetime.strptime(str(news['created_at']), "%Y-%m-%d %H:%M:%S"),
            "updatedAt": datetime.strptime(str(news['updated_at']), "%Y-%m-%d %H:%M:%S"),
            "intro": news['intro'],
            "contentId": news['story_id'],
            }

        docs.update(newDocument)
        count += 1
    if len(docs) > 0:
        pyNewsCollection.insert_one(docs)
    # return render_template('index.html', msg="5000 news fected successfully.")
    print(f'{COUNT} news fected successfully. \n{len(docs)} news fected successfully.')
    