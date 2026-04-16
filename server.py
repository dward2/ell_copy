from flask import Flask, request, jsonify
import mongo

app = Flask(__name__)


@app.route("/", methods=['GET'])
def server_status():
    return "server is running"


@app.route("/rooms", methods=['GET'])
def get_rooms():
    return [100, 200, 300]


@app.route("/patient/<room>", methods=["GET"])
def get_patient_data_from_room(room):
    # implement to get:
    # name, mrn, apnea
    # latest cpap image
    # latest pressure
    # list of cpap timestamps
    patient = {"name": "ella", "mrn": 1234, "cpap image": "image_str",
               "times": ["mm/dd/yy 00:00"], "pressure": 5, "apnea": 3}
    return jsonify(patient)


@app.route("/cpap/<time>", methods=["GET"])
def get_cpap_from_time(time):
    # implement to get the cpap image string at specific time
    return "img_str"


@app.route("/pressure/<p>", methods=["POST"])
def new_pressure(p):
    return "added pressure", 200
