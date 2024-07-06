from app import db


class Vacancy(db.Model):
    __tablename__ = 'vacancies'

    id = db.Column(db.Integer, autoincrement=True)
    name = db.Column(db.String(255))
    company = db.Column(db.String(255))
    location = db.Column(db.String(255))
    salary = db.Column(db.Integer)
    url = db.Column(db.Text)
    vacancy_id = db.Column(db.String(255), primary_key=True)
