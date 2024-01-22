import json
import threading
from datetime import datetime

import requests
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO

from _app.utils.json_data import save_json, update_payment

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def input():
    return render_template('input.html')


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
    response_status = ''

    def status_check_wrapper():
        nonlocal response_status
        response_status = request_check(par['order']['id'])['status']

    while loop_status:
        thread = threading.Thread(target=status_check_wrapper)
        thread.start()

        thread.join(timeout=thread_timeout_second)
        if response_status in ['PAID', 'DECLINE', 'CANCEL']:
            loop_status = False
        else: pass


    update_order = update_payment(order_id= par['order']['id'], status= response_status)
    socketio.emit('update_payment_status', {'status': response_status})

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


@socketio.on('client_connect')
def socket_connect_event(data):
    print('Socket connect: {}'.format(data))


def request_check(order_id: str) -> dict:
    req = requests.get(f'https://devo.finnet.co.id/pg/payment/card/check/{order_id}', headers={
        'Authorization': 'Basic U0tEQU45NjA6endaVjBoQ2NxZTcydU1tUkFGc0JKOXY1S0VHYXBUUWc='
    })
    response = req.json()
    return {'status': response['data']['result']['payment']['status']}