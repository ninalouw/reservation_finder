import operator
import os
from datetime import datetime
from rq import Queue
from worker import conn
from rq.job import Job
from flask import Flask, render_template, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

q = Queue(connection=conn)
from models import *


@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == "POST":
        # get inputs from user
        data = json.loads(request.data.decode())
        form = data['form']
        departing_date = str(form['departing_date'])
        return_date = str(form['return_date'])
        depart_term = str(form['depart_term'])
        arrive_term = str(form['arrive_term'])
        run_trip_planner(departing=[departing_date], returning=[return_date],
                         departing_from=depart_term, arriving_in=[arrive_term])
    return render_template('index.html', results=results)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        res = AvailableSailing.query.filter_by(id=job.result).first()
        result_object = jsonify({"Vessel": res.vessel_name, "departing": res.departure_time, "arrival": res.arrival_time,
                "Departure Terminal": res.departure_terminal, "Arrival Terminal": res.arrival_terminal})
        return result_object
    else:
        return "Nay!", 202


def run_trip_planner(departing, returning, departing_from, arriving_in):
    from reservations import TripPlanner

    planner = TripPlanner(departing=departing,
                          returning=returning,
                          departing_from=departing_from,
                          arriving_in=arriving_in)
    planner.run()


if __name__ == '__main__':
    app.run()


