from pymongo import MongoClient
from datetime import datetime

uri = "mongodb+srv://emf55:qFYD@cluster0.tjtcig3.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsAllowInvalidCertificates=True)
client.admin.command({'ping': 1})
db = client["patient_db"]          # creates it if it doesn't exist
collection = db["patient"]


def create_patient(mrn, rn, name=None):
    '''Creates a new patient record in the
    database with only the required fields.
    Args:
        mrn(int): medical record number
        rn(str): room number
    '''
    new_patient = {
        "mrn": mrn,
        "room_number": rn,
        "name": name,
    }
    collection.insert_one(new_patient)


def create_patient_cpap(mrn, rn, pres, apnea, br, cpap_image, time, name=None):

    new_patient = {
        "name": name,
        "mrn": mrn,
        "room_number": rn,
        "pressure": pres,
        "apnea_count": apnea,
        "breathing_rate": br,
        "cpap_data": [{
            "time": time,
            "image": cpap_image
        }]
    }
    collection.insert_one(new_patient)


def update_patient_name(mrn, name):
    patient = collection.find_one({"mrn": mrn})
    if patient is not None:
        collection.update_one(
            {"mrn": mrn},
            {"$set": {"name": name}}
        )


def update_cpap_data(mrn, apnea, br, cpap_image, time):
    # change the pressure, br, and apnea to new data.
    # append new cpap image with timestamp
    collection.update_one(
        {"mrn": mrn},
        {
            "$set": {
                "apnea_count": apnea,
                "breathing_rate": br
            },
            "$push": {
                "cpap_data":
                    {
                        "time": time,
                        "image": cpap_image
                    }
            }
        }
    )


def get_room_list():
    all_rooms = collection.distinct("room_number")
    print(all_rooms)
    return all_rooms


def get_patient(room):
    return collection.find_one({"room_number": room})


def change_pressure(room, p):
    patient = collection.find_one({"room_number": room})
    if patient is not None:
        collection.update_one({"room_number": room}, {"$set": {"pressure": p}})


def reset_db():
    collection.delete_many({})
