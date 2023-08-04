from flask import Flask, render_template, g, request
from database import get_db
from datetime import datetime

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date']
        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')
        db.execute('insert into log_date (entry_day) values (?)', [database_date])
        db.commit()
    cur = db.execute('select log_date.entry_day, sum(food.protein) as protein, sum(food.carbohydrates) as carbo, '
                     'sum(food.fat) as fat, sum(food.calories) as cal from log_date '
                     'join food_date on food_date.log_date_id = log_date.id '
                     'join food on food.id = food_date.food_id '
                     'group by log_date.id '
                     'order by log_date.entry_day desc')
    results = cur.fetchall()

    day_results = []
    for each in results:
        single_date = {'entry_day': each['entry_day'], 'protein': each['protein'], 'carbohydrates': each['carbo'],
                       'fat': each['fat'], 'calories': each['cal']}

        d = datetime.strptime(str(each['entry_day']), '%Y%m%d')
        single_date['pretty_day'] = datetime.strftime(d, '%B %d, %Y')
        day_results.append(single_date)

    return render_template('home.html', results=day_results)


@app.route('/view/<date>', methods=['POST', "GET"])
def view(date):
    db = get_db()
    cur = db.execute('select id, entry_day from log_date where entry_day = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        db.execute('insert into food_date (food_id, log_date_id) '
                   'values (?, ?)', [request.form['food-select'], date_result['id']])
        db.commit()
        #return f'<h1> The food item added is {request.form["food-select"]}</h1>'

    d = datetime.strptime(str(date_result['entry_day']), '%Y%m%d')

    pretty_day = datetime.strftime(d, "%B %d, %Y")
    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()
    #return f'<h1> the day is {result["entry_day"]} </h1>'

    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories '
                         'from log_date '
                         'join food_date on food_date.log_date_id = log_date.id '
                         'join food on food.id = food_date.food_id '
                         'where log_date.entry_day = ?', [date])
    log_result = log_cur.fetchall()

    totals = {'protein': 0, 'carbohydrates': 0, 'fat': 0, 'calories': 0}

    for food in log_result:
        totals['protein'] += int(food['protein'])
        totals['carbohydrates'] += int(food['carbohydrates'])
        totals['fat'] += int(food['fat'])
        totals['calories'] += int(food['calories'])

    return render_template('day.html', pretty_day=pretty_day, food_results=food_results,
                           entry_day=date_result['entry_day'], log_results=log_result, totals=totals)


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()
    if request.method == 'POST':
        name = request.form["food-name"]
        protein = int(request.form["protein"])
        carbohydrates = int(request.form["carbohydrates"])
        fat = int(request.form["fat"])
        calories = protein * 4 + carbohydrates * 4 + fat * 9

        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?,?,?,?,?)',
                   [name, protein, carbohydrates, fat, calories])
        db.commit()
        """return f'<h1> Name: {request.form["food-name"]}. Protein: {request.form["protein"]}. ' \
               f'Carbs: {request.form["carbohydrates"]}. Fat: {request.form["fat"]}</h1>'"""
    cur = db.execute('select name, protein, carbohydrates, fat, calories from food;')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
