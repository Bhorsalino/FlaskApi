import subprocess
from http import client
from typing import Dict, Tuple
from flask_restful import Api, Resource
from flask import Flask, jsonify, request
from pymongo import MongoClient
import bcrypt
import spacy
import json
import requests

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017/')  #Run in container
db = client.SentencesDatabase
users = db['Users']

class Register(Resource):
    def post(self):
        postedData = request.get_json()

        userName = postedData['username']
        password = postedData['password']

        if UserExist(userName):
            return jsonify(generateReturnDictionary(301, 'Username: ' + userName + ' already exists'))
            
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one({
            "Username": userName,
            "Password": hashed_pw,
            "Sentence": "",
            "Own": 0,
            "Debt": 0,
            "Tokens": 5
        })

        return jsonify(generateReturnDictionary(200, 'Successfully signed up'))

class Classify(Resource):
    def post(self):
        postedData = request.get_json()
        userName = postedData['username']
        password = postedData['password']
        url = postedData['url']

        retJson, error = verifyCredentials(userName, password)
        if error:
            return jsonify(retJson)

        tokens = countTokens(userName)
        if tokens <= 0:
            return jsonify(generateReturnDictionary(303, "Not enough tokens!"))

        r = requests.get(url)
        retJson = {}
        with open('temp.jpg', 'wb') as f:
            f.write(r.content)
            proc = subprocess.Popen('python3 classify_image.py --model_dir=. --image_file=./temp.jpg', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            #subprocess.run('python3 classify_image.py --model_dir=. --image_file=./temp.jpg', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            proc.communicate()[0]
            proc.wait()
            subprocess.run('python3 create_file.py', shell=True)
            with open("text.txt") as f:
                retJson = json.load(f)

        users.update_one({
            "Username": userName,
        },{
            '$set':{
                "Tokens": tokens -1
            }
        })

        return retJson

class Detect(Resource):
    def post(self):
        postedData = request.get_json()
        
        userName = postedData['username']
        password = postedData['password']
        text1 = postedData['text1']
        text2 = postedData['text2']
        
        retJson, error = verifyCredentials(userName, password)
        if error:
            return jsonify(retJson)
        
        num_tokens = countTokens(userName)
        if num_tokens <= 0:
            return jsonify(generateReturnDictionary(301, 'You are out of tokens, please refill'))
            
        nlp = spacy.load('en_core_web_sm')
        text1 = nlp(text1)
        text2 = nlp(text2)
        ratio = text1.similarity(text2)

        users.update_one({
            "Username": userName,
        },{
            '$set':{
                "Tokens": num_tokens -1
            }
        })

        retJson = {"status": 200,
                    "similarity": ratio,
                    "msg": "Similarity score calculated successfully"}
        

        return jsonify(retJson)

class Store(Resource):
    def post(self):
        postedData = request.get_json()
        
        userName = postedData['username']
        password = postedData['password']
        sentence = postedData['sentence']

        retJson, error = verifyCredentials(userName, password)
        if error:
            return jsonify(retJson)
        
        num_tokens = countTokens(userName)
        if num_tokens <= 0:
            return jsonify(generateReturnDictionary(303, "Not enough tokens, please refill!"))

        users.update_one({
            "Username": userName
        }, {
            '$set':{
                "Sentence": sentence,
                "Tokens": num_tokens -1
            }
        })

        return jsonify(generateReturnDictionary(200, "Sentence saved successfully"))
        
class Get(Resource):
    def post(self):
        postedData = request.get_json()

        userName = postedData['username']
        password = postedData['password']

        retJson, error = verifyCredentials(userName, password)
        if error:
            return jsonify(retJson)
        
        num_tokens = countTokens(userName)
        if num_tokens <= 0:
            return jsonify(generateReturnDictionary(303, "Not enough tokens, please refill!"))

        users.update_one({
            "Username": userName
        },{
            '$set':{
                "Tokens": num_tokens - 1
            }
        })

        sentence = users.find({
            "Username": userName
        })[0]['Sentence']

        return jsonify(generateReturnDictionary(200, sentence))
                    
class Refill(Resource):
    def post(self):
        
        postedData = request.get_json()
        userName = postedData['username']
        password = postedData['admin_pwd']
        refill_amount = postedData['refill']

        if not UserExist(userName):
            return jsonify(generateReturnDictionary(301, 'Username: ' + userName + ' does not exists'))

        correct_pwd = 'abc123'
        if not correct_pwd == password:
            return jsonify(generateReturnDictionary(304, 'Invalid Admin Password'))
        
        users.update_one({
            "Username":userName
        },{
            '$set':{
                "Tokens": refill_amount
            }
        })

        return jsonify(generateReturnDictionary(200, 'Refilled successfully'))
        
class Add(Resource):
    def post(self):
        
        postedData = request.get_json()
        userName = postedData['username']
        password = postedData['admin_pwd']
        money = postedData['amount']

        retJson, error = verifyCredentials(userName, password)
        if error:
            return jsonify(retJson)        

        if money <= 0:
            return jsonify(generateReturnDictionary(304, 'The money account must be >= 0'))
        
        cash = cashWithUser(userName)
        money-=1
        bank_cash = cashWithUser('BANK')
        updateAccount('BANK', bank_cash + 1)
        updateAccount(userName, cash + money)

        return jsonify(generateReturnDictionary(200, 'Amount added sucessfully to account'))

class Transfer(Resource):
    def post(self):
        postedData = request.get_json()
        userName = postedData['username']
        password = postedData['admin_pwd']
        to       = postedData['to']
        money    = postedData['amount']

        retJson, error = verifyCredentials(userName, password)
        if error:
            return jsonify(retJson)

        cash = cashWithUser(userName)
        if cash <= 0:
            return jsonify(generateReturnDictionary(304, 'You are out of money, please add money'))


def cashWithUser(userName:str)->int:
    cash = users.find_one({
        "Username": userName
    })[0]['Own']
    return cash

def debtWithUser(userName:str)->int:
    debt = users.find_one({
        "Username": userName
    })[0]['Debt']
    return debt

def updateAccount(userName:str, balance:int)->None:
    users.update_one({
        "Username": userName
    },{
        '$set':{'Own':balance}
    })

def updateDebt(userName:str, balance:int)->None:
    users.update_one({
        "Username": userName
    },{
        '$set':{'Debt':balance}
    })

def generateReturnDictionary(status:int, msg:str)->Dict:
    retJson = {
        "status": status,
        "msg": msg
    }
    return retJson

def verifyCredentials(userName:str, password:str)->Tuple[Dict, bool]:
    if not UserExist(userName):
        return generateReturnDictionary(301, 'Invalid Username'), True
    
    correct_pwd = verifyPw(userName, password)
    if not correct_pwd:
        return generateReturnDictionary(302, 'Invalid password'), True        

    return None, False

def UserExist(userName:str)->bool:
    if users.count_documents({"Username":userName}) == 0:
        return False
    else:
        return True

def verifyPw(userName:str, password:str)->bool:
    
    if not UserExist(userName):
        return False

    hashed_pd = users.find({
            "Username": userName
        })[0]["Password"] 

    if bcrypt.hashpw(password.encode('utf8'), hashed_pd) == hashed_pd:
        return True
    else:
        return False  

def countTokens(userName:str)->int:
    tokens = users.find({
        "Username": userName
    })[0]["Tokens"]

    return tokens

api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')
api.add_resource(Classify, '/classify')

if __name__ == '__main__':
    app.run(host='0.0.0.0')