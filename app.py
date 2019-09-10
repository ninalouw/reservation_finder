import os
from reservations import TripPlanner
import requests
from rq import Queue
from worker import conn
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result

q = Queue(connection=conn)


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == "POST":
        # get inputs from user
        try:
            departing_date = request.form['departing_date']
            return_date = request.form['return_date']
            depart_term = request.form['depart_term']
            arrive_term = request.form['arrive_term']
            available_sailings = run_trip_planner(departing=[departing_date], returning=[return_date],
                                                  departing_from=depart_term, arriving_in=[arrive_term])
        except:
            errors.append(
                "Unable to find reservations. Please make sure inputs are valid and try again."
            )
            return render_template('index.html', errors=errors)
        if available_sailings:
            results = available_sailings
            try:
                result = Result(
                    route=[depart_term, arrive_term],
                    dates=[departing_date, return_date],
                    result_all=available_sailings,
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")
    return render_template('index.html', errors=errors, results=results)


def run_trip_planner(departing, returning, departing_from, arriving_in):

    planner = TripPlanner(departing=departing,
                          returning=returning,
                          departing_from=departing_from,
                          arriving_in=arriving_in)
    return planner.run()


if __name__ == '__main__':
    app.run()


