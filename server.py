from flask import Flask, request
import mongo

app = Flask(__name__)

@app.route("/", methods=['GET'])
def server_status():
    return "server is running"
