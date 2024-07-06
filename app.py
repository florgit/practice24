import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from vacancies_parser import get_vacancies

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL',
                                                  'postgresql://postgres:postgres@localhost/vacancies_db')
db = SQLAlchemy(app)

from models import Vacancy

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text').strip()
        salary = request.form.get('salary').strip()
        area = request.form.get('area').strip()
        only_with_salary = bool(request.form.get('only_with_salary'))

        if not text:
            flash('Поле поиска обязательно для заполнения')
            return redirect(url_for('index'))

        get_vacancies(text, salary, area, only_with_salary)

        return redirect(url_for('results'))

    return render_template('index.html')


@app.route('/results')
def results():
    name = request.args.get('name', '').strip()
    city = request.args.get('city', '').strip()
    company = request.args.get('company', '').strip()
    from_salary = request.args.get('from_salary', '').strip()
    to_salary = request.args.get('to_salary', '').strip()

    filters = []
    if name:
        filters.append(Vacancy.name.ilike(f'%{name}%'))
    if city:
        filters.append(Vacancy.location.ilike(f'%{city}%'))
    if company:
        filters.append(Vacancy.company.ilike(f"%{company}%"))
    if from_salary:
        if from_salary.isdigit():
            filters.append(Vacancy.salary >= from_salary)
        else:
            flash('Неверно задан параметр зарплаты!')
    if to_salary:
        if to_salary.isdigit():
            filters.append(Vacancy.salary <= to_salary)
        else:
            flash('Неверно задан параметр зарплаты!')

    if filters:
        filtered_vacancies = Vacancy.query.filter(*filters).order_by(Vacancy.id.desc()).all()
    else:
        filtered_vacancies = Vacancy.query.order_by(Vacancy.id.desc()).all()

    return render_template('results.html', data=filtered_vacancies)


if __name__ == '__main__':
    app.run(debug=True)
