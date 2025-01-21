import shelve

class MyDB:
    def __init__(self, filename):
        self.filename = filename

    def __getitem__(self, key):
        with shelve.open(self.filename) as db:
            return db[key]

    def __setitem__(self, key, value):
        with shelve.open(self.filename) as db:
            db[key] = value

    def __delitem__(self, key):
        with shelve.open(self.filename) as db:
            del db[key]

    def keys(self):
        with shelve.open(self.filename) as db:
            return list(db.keys())

db = MyDB("userdb")
