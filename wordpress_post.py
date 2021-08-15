#!/usr/bin/python3

from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import json
import base64
import os
import mimetypes
import pprint

url_post = "https://YOUR-WP-URL-HERE/wp-json/wp/v2/posts"
url_media = "https://YOUR-WP-URL-HERE/wp-json/wp/v2/media"
user = "USERNAME"
password = "APPL ICAT IONP ASSW ORDH ERE!"

credentials = user + ':' + password
token = base64.b64encode(credentials.encode())

# Upload image
def wp_image_upload(filename, title):
    imgPath = filename
    imgType = mimetypes.guess_type(imgPath)
    fileName = os.path.basename(imgPath)
    multipart_data = MultipartEncoder(
        fields={
            # a file upload field
            'file': (fileName, open(imgPath, 'rb'), imgType),
            # plain text fields
            'title' : title,
        }
    )

    header = {'Authorization': 'Basic ' + token.decode('utf-8'),
            'Content-Type': multipart_data.content_type}
    response = requests.post(url_media, data=multipart_data,
                            headers=header)
    return json.loads(response.text)
    

# regular post
def wp_post_upload(title, formatStr, content, dateStr):
    header = {'Authorization': 'Basic ' + token.decode('utf-8')}
    post = {
    'title'    : title,
    'status'   : 'draft',
    'format'   : formatStr,
    'content'  : content,
    'categories': 551, # category ID
    'date'   : dateStr
    }

    response = requests.post(url_post , headers=header, json=post)
    return json.loads(response.text)


# Looks up an image in a Piwigo gallery to find its URL
def piwigo_get_image_path(imageFile):
    url = f"https://YOUR-PIWIGO-URL-HERE/ws.php?format=json&method=pwg.images.search&query={imageFile}"
    response = requests.post(url)
    result = json.loads(response.text)
    if (len(result["result"]["images"]) == 0): return "#"
    return result["result"]["images"][0]["element_url"].replace("http", "https")

with open('media-posts.json') as json_file:
    data = json.load(json_file)

postCount = 1
totalPosts = len(data)
for post in data:
    print (f'[{postCount}/{totalPosts}] [{int(postCount/totalPosts*100)}] {post["date"]}')
    postCount += 1

    content = ""
    if ("content" in post):
        content = post["content"]
    title = "NO TITLE"
    if ("title" in post):
        title = post["title"]

    for media in post["media"]:
        url = piwigo_get_image_path(media["file"])
        content += f'<br><img src={url}><br>'

    wp_post_upload(title,"standard",content, post["date"])
