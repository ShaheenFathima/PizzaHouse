import unittest
from pizzaweb import app, mongoclient


class BasicTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        db = mongoclient['Pizza']
        db.Pizzas.drop()
        db.Codes.drop()
        db.Pizzas.insert_one({"name": "initaldbtest", 'pizzatype': "Pepperoni", "code": "12345"})
        db.Codes.insert_one({'code': '12345'})

    # executed after each test
    def tearDown(self):
        pass

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_page(self):
        response = self.app.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_createcode_page(self):
        db, x, y = mongoclient['Pizza'], 0, 0
        for _ in db.Codes.find({}):
            x = x + 1
        response = self.app.get('/newcode', follow_redirects=True)
        for _ in db.Codes.find({}):
            y = y + 1
        self.assertEqual(response.status_code, 200)
        self.assertGreater(y, x)

    def test_error(self):
        data = {"fname": "thisistoolong123", "dropdown": "Pepperoni", "code": "12345"}
        response = self.app.post('/', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 400)

    def test_confirmation_page(self):
        response = self.app.get('/confirmation', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_order(self):
        db = mongoclient['Pizza']
        data = {"fname": "webtest", "dropdown": "Pepperoni", "code": "12345"}
        response = self.app.post('/', follow_redirects=True, data=data)
        for i in db.Pizzas.find({'name': 'webtest', 'pizzatype': 'Pepperoni', 'code': '12345'}):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(i['name'], data['fname'])
            self.assertEqual(i['pizzatype'], data['dropdown'])
            self.assertEqual(i['code'], data['code'])


if __name__ == "__main__":
    unittest.main()
