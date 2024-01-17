import json
from datetime import datetime

import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/')
def input():
    return render_template('input.html')


@app.route('/payment', methods=['POST'])
def payment():
    par = request.values
    order_id = f"{par['payment_method'][0:2]}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    payload = {
        "customer": {
            "email": par['customer_email'],
            "firstName": par['customer_first_name'],
            "lastName": par['customer_last_name'],
            "mobilePhone": par['customer_mobile_phone']
        },
        "order": {
            "id": f"{order_id}",
            "amount": par['amount'],
            "currency": "IDR",
            "description": par['description']
        },
        "url": {
            "callbackUrl": "https://sandbox.finpay.co.id/simdev/finpay/result/resultfailed.php"
        },
        "sourceOfFunds": {
            "type": par['payment_method']
        }
    }
    req = requests.post('https://devo.finnet.co.id/pg/payment/card/initiate', data=json.dumps(payload), headers={
        'Authorization': 'Basic U0tEQU45NjA6endaVjBoQ2NxZTcydU1tUkFGc0JKOXY1S0VHYXBUUWc=',
        'Content-Type': 'application/json'
    })
    try:
        response = req.json()
        print(response)
        print(response['redirecturl'])
        return redirect(response['redirecturl'])
    except Exception as e:
        print(e)
        return str(e), 500
