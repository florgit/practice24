import requests
import psycopg2
import os


def get_vacancies(text, salary, area, only_with_salary):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'per_page': 20,
        'text': text,
        'only_with_salary': only_with_salary,
    }

    if salary:
        params['salary'] = salary
    if area:
        params['text'] += ' ' + area

    r = requests.get(url, params=params)
    data = r

    if data.status_code == 200:
        data = data.json()
        if len(data['items']) != 0:
            write_in_db(data['items'])
        else:
            print('соси, нет вакансий')
    elif data.status_code == 400:
        print('Параметры переданы с ошибкой')
    elif data.status_code == 403:
        print('капча')
    elif data.status_code == 404:
        print('Указанная вакансия не существет')


def write_in_db(data):
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    conn = psycopg2.connect(
        dbname='vacancies_db',
        user='postgres',
        password='postgres',
        host=db_host,
    )

    cursor = conn.cursor()

    for item in data:
        name = item['name']
        company = item['employer']['name']
        alternate_url = item['alternate_url']
        location = item['area']['name']
        vacancy_id = item['id']

        if item['salary'] is None:
            item_salary = 'NULL'
        else:
            currency_dict = requests.get('https://api.hh.ru/dictionaries').json()['currency']
            salary_obj = item['salary']
            rate = 1
            if salary_obj['currency'] != 'RUR':
                for i in currency_dict:
                    if salary_obj['currency'] == i['code']:
                        rate = i['rate']

            if item['salary']['to']:
                item_salary = item['salary']['to'] // rate
            else:
                item_salary = item['salary']['from'] // rate

        cursor.execute(
            f"INSERT INTO vacancies (name, company, location, salary, url, vacancy_id)"
            f"VALUES ('{name}', '{company}', '{location}', {item_salary}, '{alternate_url}', '{vacancy_id}')"
            f"ON CONFLICT (vacancy_id)"
            f"DO UPDATE SET"
            f"  name = EXCLUDED.name,"
            f"  company = EXCLUDED.company,"
            f"  location = EXCLUDED.location,"
            f"  salary = EXCLUDED.salary,"
            f"  url = EXCLUDED.url;"
        )

    conn.commit()
    cursor.close()
    conn.close()
