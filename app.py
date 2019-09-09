import os
from reservations import TripPlanner
from rq import Queue
from worker import conn
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result

q = Queue(connection=conn)


@app.route('/')
def hello():
    run_trip_planner()
    return "Hello World!"


def run_trip_planner(departing=['Sep 6'], returning=['Sep 9'], departing_from='Vancouver',
                     arriving_in=['Langdale', 'Nanaimo']):

    planner = TripPlanner(departing=departing,
                          returning=returning,
                          departing_from=departing_from,
                          arriving_in=arriving_in)
    planner.run()


if __name__ == '__main__':
    app.run()


