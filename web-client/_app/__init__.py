import json
import os
import threading
from datetime import datetime
from dotenv import load_dotenv

import requests
from flask import Flask, render_template, request, redirect

from _app.utils.order_data import save_json, update_payment
from _app.utils.payment_method import BankResource

load_dotenv()
app = Flask(__name__)

FINNET_AUTH_KEY=os.getenv('FINNET_AUTH_KEY')
SOCKET_SERVICE_KEY=os.getenv('SOCKET_SERVICE_KEY')

@app.route('/')
def input_payment():
    banks :list = BankResource.get_all()
    return render_template('input.html', banks=json.dumps(banks))


@app.route('/payment', methods=['POST'])
def payment():
    par = request.values
    order_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
    data = {}
    data.update(par)
    data.update({'order_id': order_id, 'status_payment': 'PENDING'})
    save_json(data)
    payload = {
        "customer": {
            "email": par['customer_email'],
            "firstName": par['customer_first_name'],
            "lastName": par['customer_last_name'],
            "mobilePhone": par['customer_mobile_phone']
        },
        "order": {
            "id": f"{order_id}",
            "amount": par['total_amount'],
            "surchargeAmount": par['surcharge_amount'],
            "itemAmount`": par['amount'],
            "currency": "IDR",
            "description": par['description']
        },
        "url": {
            "callbackUrl": "https://finpay-test.yukbil.my.id/callback_notification"
        },
        "sourceOfFunds": {
            "type": par['payment_method']
        }
    }
    try:
        req = requests.post('https://devo.finnet.co.id/pg/payment/card/initiate', data=json.dumps(payload), headers={
            'Authorization': F'Basic {FINNET_AUTH_KEY}',
            'Content-Type': 'application/json'
        })
        response = req.json()
        return redirect(f'/after_payment?order_id={order_id}&payment_code={response["paymentCode"]}')
    except Exception as e:
        print(e)
        return str(e), 500


@app.route('/after_payment')
def after_payment():
    return render_template('after_checkout.html', order_id= request.values.get('order_id'), payment_code = request.values.get('payment_code'))

@app.route('/callback_notification', methods=['POST'])
def callback_notification():
    par = request.json
    if not par:
        return {'message': 'Invalid request body type'}, 400
    thread_timeout_second = 600 # 10 minute
    loop_status = True
    response_status = None

    def status_check_wrapper():
        nonlocal response_status
        response_status = request_check(par['order']['id'])['status']

    while loop_status:
        thread = threading.Thread(target=status_check_wrapper)
        thread.start()

        thread.join(timeout=thread_timeout_second)
        if response_status:
            loop_status = False
        else: pass


    update_order = update_payment(order_id= par['order']['id'], status= response_status)
    socket_hit(data={'status': response_status}, channel='update_payment_status')

    if not update_order:
        return {
            "responseCode": "400",
            "responseMessage": "Bad request"
        }, 400

    return {
      "responseCode": "2000000",
      "responseMessage": "Success",
      "processingTime": 0.6609270572662354
    }, 200


@app.route('/check')
def check():
    response = request_check(request.args.get("order_id"))
    return response, 200


def request_check(order_id: str) -> dict:
    req = requests.get(f'https://devo.finnet.co.id/pg/payment/card/check/{order_id}', headers={
        'Authorization': f'Basic {FINNET_AUTH_KEY}'
    })
    response = req.json()
    return {'status': response['data']['result']['payment']['status']}


def socket_hit(data, channel):
    try:
        requests.post(f"https://finpay-test-socket.yukbil.my.id/hit_channel", data=json.dumps({
            'data': data,
            'channel': channel
        }), headers={
            'API_KEY': SOCKET_SERVICE_KEY,
            'Origin': 'https://finpay-test.yukbil.my.id',
            'Content-Type': 'application/json'
        })
    except Exception as e:
        print(e)