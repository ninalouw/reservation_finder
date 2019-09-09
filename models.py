from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(80), nullable=False)
    dates = db.Column(db.String(100), nullable=False)
    result_all = db.Column(JSON)

    def __init__(self, route, result_all):
        self.route = route
        self.result_all = result_all

    def __repr__(self):
        return '<id {}>'.format(self.id)