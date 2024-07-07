import sqlite3
import requests
from flask import Flask, render_template, request

app = Flask(__name__)
app.template_folder = 'templates'

def vacancies_search(keyword):
    connection = sqlite3.connect("../bd/hh_bd.db")
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
                vacancy_salary_from = str(vacancy.get("salary", {}).get("from"))
                vacancy_salary_to = str(vacancy.get("salary", {}).get("to"))
                valute = str(vacancy.get("salary", {}).get("currency"))
                connection = sqlite3.connect("../bd/hh_bd.db")
                cursor = connection.cursor()
                cursor.execute("INSERT INTO vacancies VALUES (?,?,?,?,?,?,?)", (vacancy_id,
                                                                                vacancy_title,
                                                                                vacancy_url, company_name,
                                                                                vacancy_area, vacancy_salary_from +
                                                                                '-' + vacancy_salary_to,
                                                                                valute))
                connection.commit()
                connection.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        city = request.form['city']
        vacancies_search(keyword)
        connection = sqlite3.connect("../bd/hh_bd.db")
        cursor = connection.cursor()
        if city:
            cursor.execute("SELECT * FROM vacancies WHERE area LIKE ?", ('%' + city + '%',))
        else:
            cursor.execute("SELECT * FROM vacancies")
        vacancies = cursor.fetchall()
        connection.close()
        return render_template('index.html', vacancies=vacancies)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
