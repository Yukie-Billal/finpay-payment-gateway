import json
import os.path

filename = 'order.json'

def check_path():
    if not os.path.exists('_app/static/data/'):
        os.makedirs('_app/static/data/')

def load_json() -> dict:
    check_path()
    with open(f'_app/static/data/{filename}') as file:
        data = file.read()
    return json.loads(data or '{}')


def save_json(data: dict):
    if not type(data) == dict:
        raise Exception('Tipe order salah')
    check_path()
    with open(f'_app/static/data/{filename}', 'w') as file:
        file.write(json.dumps(data))
    return True

def update_payment(order_id: str, status: str) -> bool:
    data = load_json()
    if not data.get('order_id') == order_id:
        return False
    data.update({'status_payment': status})
    save_json(data)
    return True