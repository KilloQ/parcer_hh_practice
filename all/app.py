import sqlite3
import requests
from flask import Flask, render_template, request

app = Flask(__name__)
app.template_folder = 'templates'

db_path = "hh_bd.db"


def create_database():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            company TEXT,
            area TEXT,
            salary_from INT,
            salary_to INT,
            currency TEXT
        )
    """)
    connection.commit()
    connection.close()


def vacancies_search(keyword):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM vacancies")
    connection.commit()
    connection.close()

    for page in range(20):
        url = "https://api.hh.ru/vacancies?clasters=true&only_with_salary=true&order_by=publication_time"
        params = {
            "text": keyword,
            "area": 113,
            "per_page": 100,
            "pages": 20,
            "page": page
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            vacancies = data.get("items", [])
            for vacancy in vacancies:
                vacancy_id = str(vacancy.get("id"))
                vacancy_title = str(vacancy.get("name"))
                vacancy_url = str(vacancy.get("alternate_url"))
                company_name = str(vacancy.get("employer", {}).get("name"))
                vacancy_area = str(vacancy.get("area", {}).get("name"))
                vacancy_salary_from = vacancy.get("salary", {}).get("from")
                vacancy_salary_to = vacancy.get("salary", {}).get("to")
                valute = str(vacancy.get("salary", {}).get("currency"))

                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                cursor.execute("INSERT INTO vacancies VALUES (?,?,?,?,?,?,?,?)", (vacancy_id,
                                                                                  vacancy_title,
                                                                                  vacancy_url, company_name,
                                                                                  vacancy_area, vacancy_salary_from,
                                                                                  vacancy_salary_to,
                                                                                  valute))
                connection.commit()
                connection.close()


create_database()


@app.route('/', methods=['GET', 'POST'])
def index():
    keyword = request.form.get('keyword', '')
    city = request.form.get('city', '')
    salary_from = request.form.get('salary_from', None)

    if request.method == 'POST':
        if keyword:
            vacancies_search(keyword)

            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            if city and salary_from:
                cursor.execute("""
                    SELECT * FROM vacancies
                    WHERE area LIKE ? AND (
                        (salary_from >= ? AND salary_from IS NOT NULL) OR
                        (salary_to >= ? AND salary_from IS NULL)
                    )
                """, ('%' + city + '%', float(salary_from), float(salary_from)))
            elif city:
                cursor.execute("SELECT * FROM vacancies WHERE area LIKE ?", ('%' + city + '%',))
            elif salary_from:
                cursor.execute("""
                    SELECT * FROM vacancies
                    WHERE (
                        (salary_from >= ? AND salary_from IS NOT NULL) OR
                        (salary_to >= ? AND salary_from IS NULL)
                    )
                """, (float(salary_from), float(salary_from)))
            else:
                cursor.execute("SELECT * FROM vacancies")
            vacancies = cursor.fetchall()
            connection.close()

            if vacancies:
                return render_template('index.html', vacancies=vacancies, keyword=keyword, city=city,
                                       salary_from=salary_from)
            else:
                return render_template('index.html', error="Вакансии не найдены", keyword=keyword, city=city,
                                       salary_from=salary_from)
        else:
            return render_template('index.html', error="Please enter a keyword", keyword=keyword, city=city,
                                   salary_from=salary_from)
    else:
        return render_template('index.html', keyword=keyword, city=city, salary_from=salary_from)


if __name__ == '__main__':
    app.run(debug=True)
