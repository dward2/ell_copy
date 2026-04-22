from pymongo import MongoClient
from datetime import datetime

uri = "mongodb+srv://emf55:qFYD@cluster0.tjtcig3.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsAllowInvalidCertificates=True)
client.admin.command({'ping': 1})
db = client["patient_db"]          # creates it if it doesn't exist
collection = db["patient"]


def create_patient(mrn, rn, name=None):
    '''Create a new patient record in the
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


def create_patient_cpap(mrn, rn, apnea, br, cpap_image, time, name=None):
    '''Create a new patient record with pressure and
    cpap file data.

     Args:
        mrn (int): medical record number.
        rn (str): room number.
        apnea (int): number of apnea events.
        br (int): breathing rate in bpm.
        cpap_image (str): base64 encoded cpap plot.
        time (str): timestamp of the CPAP data.
        name (str) (optional): patient name.
    '''
    new_patient = {
        "name": name,
        "mrn": mrn,
        "room_number": rn,
        "pressure": None,
        "apnea_count": apnea,
        "breathing_rate": br,
        "cpap_data": [{
            "time": time,
            "image": cpap_image
        }]
    }
    collection.insert_one(new_patient)


def update_patient_name(mrn, name):
    '''Update an existing patient's
    name in the database.

    Args:
        mrn(int): medical record number
        name(str): new patient name
    '''
    patient = collection.find_one({"mrn": mrn})
    if patient is not None:
        collection.update_one(
            {"mrn": mrn},
            {"$set": {"name": name}}
        )


def update_cpap_data(mrn, apnea, br, cpap_image, time):
    '''Update CPAP data for existing patients.
    Replace breathing rate and apnea count with new values.
    Append new image and timestamp into a list.

    Args:
        mrn (int): medical record number.
        apnea (int): number of apnea events.
        br (int): breathing rate in bpm.
        cpap_image (str): base64 encoded CPAP plot.
        time (str): timestamp of the CPAP data.
    '''
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
    '''Get a list of all unique room numbers
    from database.

    Returns:
        list: all uploaded room numbers
    '''
    all_rooms = collection.distinct("room_number")
    print(all_rooms)
    return all_rooms


def get_patient(room):
    '''Get patient data for specific room.

    Args:
        room(str): room number

    Returns:
        dict: patient data, or None if no patient found
    '''
    return collection.find_one({"room_number": room})


def change_pressure(room, p):
    '''Update the commanded CPAP pressure
    for a specific room.

    Args:
        room(str): room number.
        p (int): new CPAP pressure

    '''
    patient = collection.find_one({"room_number": room})
    if patient is not None:
        collection.update_one({"room_number": room}, {"$set": {"pressure": p}})


def reset_db():
    '''Delete all documents from
    patient collection. Used in testing.
    '''
    collection.delete_many({})
