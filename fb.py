#!/usr/bin/python3
import webscrape
import fileops
import json
from datetime import datetime
import os

def parse_obj(obj):
    if isinstance(obj, str):
        return obj.encode('latin_1').decode('utf-8')

    if isinstance(obj, list):
        return [parse_obj(o) for o in obj]

    if isinstance(obj, dict):
        return {key: parse_obj(item) for key, item in obj.items()}

    return obj

with open('posts/your_posts_1.json', encoding='utf-8') as json_file:
    data = parse_obj(json.load(json_file))

text_posts = []
media_posts = []

print ("There are ", len(data), "posts.")
post_count = len(data)
post_counter = 1

for entry in data:
    print (f'[{post_counter}/{post_count}] - [{int((post_counter/post_count)*100)}%] - {entry["timestamp"]}')
    post_counter += 1
    # Just do regular post first
    if ("attachments" not in entry):
        print ("Regular post ", end="")
        continue
        if ("data" in entry) and (len(entry["data"]) > 0):
            if ("post" in entry["data"][0]):
                newpost = dict()
                title = entry["data"][0]["post"][0:50] + "..."
                newpost["title"] = title
                newpost["status"] = "draft"
                newpost["content"] = entry["data"][0]["post"]
                newpost["categories"] = 551
                newpost["date"] = datetime.utcfromtimestamp(entry["timestamp"]).strftime('%Y-%m-%dT%H:%M:%S')
                text_posts.append(newpost)
                print (f"added [{len(text_posts)}] ")
                continue
        else:
            #print ("Junk post")
            continue
    else:
        # Prune out any junk (other people's things I've shared, etc that I didn't export)
        if (len(entry["attachments"]) == 0):
            #print ("Junk Post")
            continue

        print ("Media post")
        has_data = False
        newpost = dict()

        newpost["date"] = datetime.utcfromtimestamp(entry["timestamp"]).strftime('%Y-%m-%dT%H:%M:%S')
        newpost["categories"] = 551
        newpost["status"] = "draft"

        # Figure out if this entry has a data->post entry to use as the body text
        if ("data" in entry) and (len(entry["data"]) > 0) and ("post" in entry["data"][0]):
            print ("\tHas data entry")
            has_data = True
            title = entry["data"][0]["post"][0:50] + "..."
            newpost["title"] = title
            newpost["content"] = entry["data"][0]["post"]
        
        # So now we might or might not have some body text and a title
        # figure out what the attachments are
        if (len(entry["attachments"]) > 1):
            print ("\tPost has", len(entry["attachments"]),"attachments")
        # go through each attachment 

        newpost["media"] = []
        validPost = False

        print ("\tProcessing Attachments")
        for att in entry["attachments"]:
            # Work out what the attachments are
            # They always have "data" as the first element
            
            if ("media" in att["data"][0]):
                print ("\t\tMedia attachments [",end="")
                # If just a bunch of images, try to make up a post tile from the first image's title
                if (has_data == False and len(entry["attachments"]) == 1):
                    title = ""
                    content = ""
                    if ("title" in att["data"][0]["media"]):
                        title = att["data"][0]["media"]["title"]
                    
                    
                    if ("description" in att["data"][0]["media"]):
                        if (title == ""):
                            title = att["data"][0]["media"]["description"]
                        else:
                            content = att["data"][0]["media"]["description"]

                    if (title == ""):
                        if ("title" in entry):
                            title = entry["title"]
                        else:
                            title = "IMPORT ERROR - NO TITLE"

                    newpost["content"] = content
                    newpost["title"] = title
                    has_data = True
                # Potential for this being multiple pictures / videos
                for media in att["data"]:
                    print("*", end="")
                    # Add them all to the post as filename and album name
                    # Albums are uploaded elsewhere, differently
                    imageFile = fileops.extract_file_album(media["media"]["uri"])
                    newpost["media"].append(imageFile)
                    validPost = True
                # uri, title, possibly description
                print ("]")
            elif("place" in att["data"][0]):
                # Ignored, can't think of a good way to use them
                # Always added to something else
                # name, coordinate, address, possibly url
                pass
            elif("external_context" in att["data"][0]):
                if ("url" in att["data"][0]["external_context"]):
                    url = att["data"][0]["external_context"]["url"]
                    print (f"\t\tURL Attachment ({url})")
                    # Sometimes added to other things, sometimes by themselves
                    result = webscrape.scrape_URL_title(url)
                    #result = {"title":"Title", "content":"content"}
                    
                    if (has_data == False and len(entry["attachments"]) == 1):
                        newpost["title"] = result["title"]
                        has_data = True
                        newpost["content"] = result["content"]
                    else:
                        if ("content" in newpost):
                            newpost["content"] += result["content"]
                        else:
                            newpost["content"] = result["content"]
                validPost = True
            elif("text" in att["data"][0]):
                # Junk entry
                #junk_posts.append(entry)
                #print ("\t\tJunk text attachment")
                pass
            else:
                #print ("\t\tJunk attachment", end="")
                pass
                #junk_posts.append(entry)

        if (validPost == True):
            print ("Valid Post")
            media_posts.append(newpost)
        print (f"Complete [{len(media_posts)}]")

print ("processed ", len(data), "posts")
print ("valid text posts", len(text_posts))
print ("Valid media posts", len(media_posts))

# Now dump this out to disk so we don't have to process it again

with open('text-posts.json', 'w', encoding='utf-8') as f:
    json.dump(text_posts, f, ensure_ascii=False, indent=4)

with open('media-posts.json', 'w', encoding='utf-8') as f:
    json.dump(media_posts, f, ensure_ascii=False, indent=4)