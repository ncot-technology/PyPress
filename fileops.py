#!/usr/bin/python3

import os

def extract_file_album(file):
    filename = os.path.basename(file)
    pathComps = os.path.dirname(file).split("/")
    albumName = ""
    if (pathComps[1] == "your_posts"):
        albumName = pathComps[1]
    else:
        albumName = pathComps[1].split("_")[0]

    return {"file":filename, "album":albumName}