import os, sys
from pathlib import Path as pt

def delete_last_line(filename):

    print(f"File received: {filename}")
    with open(filename, "r+", encoding = "utf-8") as file:

        file.seek(0, os.SEEK_END)
        pos = file.tell() - 2
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()

        print(f"Last line deleted")

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")

    normMethod = args[-1]
    filename = f"{args[0]}_{normMethod}.expfit"
    
    location = pt(args[1])
    if location.name == "DATA": datfile_location = location.parent/"EXPORT"
    else: datfile_location = location/"EXPORT"

    filename = datfile_location / filename
    delete_last_line(filename)