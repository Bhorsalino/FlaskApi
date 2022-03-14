from http import client
from typing import Dict
from flask_restful import Api, Resource
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017/')  #Run in container
#client = MongoClient('mongodb://localhost:27017')  #Run in local
db = client.newDB
#mydb = client['mydatabase']
#mycol = mydb['UserNum']
UserNum = db['UserNum']

UserNum.insert_one({
    'num_of_users': 0
})

class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        new_num = prev_num + 1
        UserNum.update_one({}, {'$set':{'num_of_users': new_num}})
        return 'Hello user ' + str(new_num)

def checkPostedData(postedData:Dict, functionName:str)-> int:
    if (functionName == 'add'):
        if 'x' not in postedData or 'y' not in postedData:
            return 301
        else:
            return 200
        
class Add(Resource):
    def post(self):
        postedData = request.get_json()
        status_code = checkPostedData(postedData, 'add')
        if (status_code != 200):
             resMap = {
            'Message': 'An error happened',
            'Status Code': status_code
            }
        else:
            x = int(postedData['x'])
            y = int(postedData['y'])
            res = x + y
            resMap = {
                'Message': res,
                'Status Code': 200
            }
        return jsonify(resMap)        

api.add_resource(Add, '/add')
api.add_resource(Visit, '/hello')

@app.route('/')
def hello_world():
    return 'Hello world'


@app.route('/add_two_numbers', methods=['POST'])
def add_two_nums():
    dataDic = request.get_json
    x = dataDic['x']
    y = dataDic['y']

    z = x + y
    retJson = {
        'z': z
    }

    return jsonify(retJson), 200

def hello_world():
    return 'Hello world'

@app.route('/atma')
def hello_atma():
    salary = 1500 * 2
    retJson = {
        'name': 'Atma',
        'apellido': 'Sangri',
        'age': 25,
        'salary': salary,
        'phones':[
            {
                'phoneName': 'nokia',
                'phoneNumber': 346245
            },
            {
                'phoneName': 'Iphone8',
                'phoneNumber': 971243
            }
        ]
    }
    return jsonify(retJson)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)