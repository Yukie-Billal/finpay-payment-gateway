import json
import os.path



class BankResource:
    filename = 'banks.json'
    file_path = '_app/static/data/'

    @classmethod
    def check_path(cls):
        if not os.path.exists(cls.file_path):
            os.makedirs(cls.file_path)

        if not os.path.exists(f'{cls.file_path}{cls.filename}'):
            with open(f'{cls.file_path}{cls.filename}', 'w') as file:
                file.write('[]')


    @classmethod
    def load_json(cls) -> list:
        cls.check_path()
        with open(f'{cls.file_path}{cls.filename}') as file:
            data = file.read()
        return json.loads(data or '[]')


    @classmethod
    def get_all(cls) -> list:
        data = cls.load_json()
        return data