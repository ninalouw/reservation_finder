from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(80), nullable=False)
    dates = db.Column(db.String(100), nullable=False)
    result_all = db.Column(JSON)

    def __init__(self, route, dates, result_all):
        self.route = route
        self.dates = dates
        self.result_all = result_all

    def __repr__(self):
        return '<id {}>'.format(self.id)


class AvailableSailing(db.Model):

    __tablename__ = 'available_sailings'

    id = db.Column(db.Integer, primary_key=True)
    departure_time = db.Column(db.String, nullable=False)
    arrival_time = db.Column(db.String, nullable=False)
    departure_terminal = db.Column(db.String, nullable=False)
    arrival_terminal = db.Column(db.String, nullable=False)
    vessel_name = db.Column(db.String, nullable=False)
    reservations_available = db.Column(db.Boolean, default=False)

    def __init__(self, departure_time, arrival_time, departure_terminal,
                 arrival_terminal, vessel_name, reservations_available):
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.departure_terminal = departure_terminal
        self.arrival_terminal = arrival_terminal
        self.vessel_name = vessel_name
        self.reservations_available = reservations_available

    def __repr__(self):
        return '<id {}>'.format(self.id)
