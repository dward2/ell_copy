from pymongo import MongoClient
uri = "mongodb+srv://emf55:qFYD@cluster0.tjtcig3.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsAllowInvalidCertificates=True)
client.admin.command({'ping': 1})
db = client["patient_db"]          # creates it if it doesn't exist
collection = db["patient"]


def create_patient(room, name, mrn, i_pressure):
    entry = {
        "room": room,
        "name": name,
        "mrn": mrn,
        "pressures": [i_pressure]
    }
    r = collection.insert_one(entry)
    print(r)


create_patient(100, "ella", 123, 6)
