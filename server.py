from flask import Flask, request, jsonify
import mongo
import base64

app = Flask(__name__)


@app.route("/", methods=['GET'])
def server_status():
    return "server is running"


@app.route("/rooms", methods=['GET'])
def get_rooms():
    return jsonify([100, 200, 300])


@app.route("/patient/<room>", methods=["GET"])
def get_patient_data_from_room(room):
    # implement to get:
    # name, mrn, apnea, breathing rate
    # latest cpap image
    # latest pressure
    # list of cpap timestamps
    print(room)
    patient = {"name": f"ella {room}", "mrn": 1234, "cpap image": "image_str",
               "times": ["mm/dd/yy 00:00", "01/30/04 00:00"], "pressure": 5,
               "apnea": 3, "br": 4}
    return jsonify(patient)


@app.route("/cpap/<time>", methods=["GET"])
def get_cpap_from_time(time):
    # implement to get the cpap image string at specific time
    return "img_str"


@app.route("/pressure/<p>", methods=["POST"])
def new_pressure(p):
    try:
        p = int(p)
    except TypeError:
        return "invalid", 400

    if p >= 4 and p <= 25:
        print(f'add pressure {p}')
        return "added pressure", 200
    else:
        return "invalid", 400


def encode_image(image_file):
    image_bytes = image_file.read()
    img_str = base64.b64encode(image_bytes).decode("utf-8")
    return img_str


@app.route("/upload_image", methods=['POST'])
def upload_image():
    file = request.files["file"]

    # encode image to str
    image_str = encode_image(file)

    # upload image here with mongo file

    return "data received", 200


if __name__ == "__main__":
    app.run()
