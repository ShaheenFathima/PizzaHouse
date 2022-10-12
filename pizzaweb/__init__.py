import pymongo
import csv
import os
import random
import colorama
from flask import render_template, request, redirect, Flask, make_response, send_file


colorama.init()
url = "http://localhost/?code="
app = Flask(__name__)
mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongoclient["Pizza"]['Pizzas']
codedb = mongoclient["Pizza"]["Codes"]
codedb.insert_one({'code': '12345'})  # <-- for unit testing


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':
        name = request.form['fname']
        pizza = request.form['dropdown']
        code = str(request.form['code'])
        if codedb.find({'code': code}).count() == 0:
            return render_template('index.html', code='', message='Code does not exist!'), 400
        if len(name) > 10:
            return render_template('index.html', code='', message='Name too long, max 10 characters.'), 400
        data = {"name": name, 'pizzatype': pizza, "code": str(code)}
        db.insert_one(data)
        resp = make_response(redirect('/confirmation'))
        resp.set_cookie('userID', name)
        resp.set_cookie('pizza', pizza)
        resp.set_cookie('code', code)
        return resp
    if 'code' in request.args:
        code = request.args['code']
    else:
        code = None
    if code is not None:
        return render_template('index.html', code=code, disabled='readonly="readonly"')
    return render_template('index.html', code=None, disabled="")


@app.route('/newcode')
def newcode():
    code = random.randint(10000, 99999)
    for i in codedb.find():
        if code == i['code']:
            code = "Error, please reload the page."
            return render_template('newcode.html', url="", code=code)
    codedb.insert_one({'code': str(code)})
    return render_template('newcode.html', url=url, code=code)


@app.after_request
def add_header(r):  # Prevent caching for development
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/confirmation')
def confirmationpage():
    name = request.cookies.get('userID')
    pizza = request.cookies.get('pizza')
    return render_template('confirmation.html', name=name, pizza=pizza)


@app.route('/admin')
def adminpage():
    if 'code' in request.args:
        code = request.args['code']
    else:
        return render_template('admin.html', pizzas='Enter code above to view and download lists.')
    if db.find({'code': code}).count() == 0:
        y = codedb.find({'code': code}).count()
        if y == 0:
            return render_template('admin.html', pizzas='Invalid code', code="")
    return render_template('admin.html',
                           pizzas=f"Total Pizzas: {db.find({'code': code}).count()}",
                           code=code)


@app.route('/admin/fulllist')
def showfulllist():
    if request.args['code'] == '':
        return redirect('/admin')
    try:
        os.remove('names.csv')
    except FileNotFoundError:
        pass
    with open('names.csv', 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Pizza']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in db.find({'code': request.args['code']}):
            writer.writerow({'Name': i['name'], 'Pizza': i['pizzatype']})
    return send_file('../names.csv', as_attachment=True)


@app.route('/assets/bootstrap/css/bootstrap.min.css')
def css():
    return send_file('./assets/bootstrap.min.css')


@app.route('/assets/js/grayscale.js')
def grayscale():
    return send_file('./assets/grayscale.js')


@app.route('/assets/img/intro-bg.jpg')
def bg():
    return send_file('./assets/intro-bg.jpg')
