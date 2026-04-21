from pymongo import MongoClient
from datetime import datetime

uri = "mongodb+srv://emf55:qFYD@cluster0.tjtcig3.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsAllowInvalidCertificates=True)
client.admin.command({'ping': 1})
db = client["patient_db"]          # creates it if it doesn't exist
collection = db["patient"]


def create_patient(mrn, rn):
    '''Creates a new patient record in the
    database with only the required fields.
    Args:
        mrn(int): medical record number
        rn(str): room number
    '''
    new_patient = {
        "mrn": mrn,
        "room_number": rn,
    }
    collection.insert_one(new_patient)
