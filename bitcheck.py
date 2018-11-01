import datetime
import hashlib
import json
import random
import re
import time

import pymysql
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

db = pymysql.connect("localhost", "root", "", "blockvotes")

cursor = db.cursor()


class Watcher:
    DIRECTORY_TO_WATCH = "../xampp/.bvusers"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            astr = event.src_path
            aeventlist = re.sub("[^\w]", " ", astr).split()
            cdt = datetime.datetime.now()
            hash = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            # print(cdt)
            with open("%s" % astr) as json_file:
                json_data = json.load(json_file)
            email = (json_data["email"])
            print("User %s has been registered." % email)
            sql = (
                    "INSERT INTO users (username, nickname, password, created_at, role) VALUES ('%s', '%s', '%s', '%s', '1');" % (
                email, aeventlist[2], hash, cdt))
            cursor.execute(sql)
            db.commit()
            print(cursor.rowcount, "record(s) affected")

        elif event.event_type == 'deleted':
            # Taken any action here when a file is deleted.
            rstr = event.src_path
            reventlist = re.sub("[^\w]", " ", rstr).split()
            print("User %s has been removed." % reventlist[2])
            sql = ("DELETE FROM users WHERE nickname='%s';" % reventlist[2])
            cursor.execute(sql)
            db.commit()
            print(cursor.rowcount, "record(s) affected")


if __name__ == '__main__':
    w = Watcher()
    w.run()
