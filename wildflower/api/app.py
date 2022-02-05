#!/usr/bin/env python3
from flask import Flask, url_for, request
import database
import json
app = Flask(__name__)

@app.route("/<script>.js")
def script(script):
    return url_for('static', filename = script + ".js")

@app.route("/<sheet>.css")
def stylesheet(sheet):
    return url_for('static', filename = sheet + ".css")

@app.route("/<pic>.gif")
def gif(pic):
    return url_for('static', filename = pic + ".gif")

@app.route("/")
def hello():
    r = database.list_found()
    d = {}
    for taxon, place, date in r:
        if taxon not in d:
            d[taxon] = []
        d[taxon].append([str(date), place])
        d[taxon].sort()
    return json.dumps(d)

@app.route("/data", methods = ["POST"])
def data():
    return database.data(request.form)

if __name__ == "__main__":
    app.run()
