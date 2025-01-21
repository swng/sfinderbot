from db import db

print(db["key1"])
db["key1"] = "value2"

db["silly"] = ":3"
print(db["silly"])
