import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'postgres', 'localhost:5432',
                                                             self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))


    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_get_paginated_questions(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_delete_question(self):
        response = self.client().delete('/questions/5')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_delete_question(self):
        response = self.client().delete('/questions/1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_post_question(self):
        new_question = {
            'question': 'abcd',
            'answer': 'dcba',
            'difficulty': 2,
            'category': 3
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_post_new_question(self):
        post_data = {
            'question': 'a',
            'answer': 'a',
            'category': 1
        }
        res = self.client().post('/questions', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")


    def test_search_questions(self):
        search = {'searchTerm': 'what'}
        response = self.client().post('/questions/search', json=search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])


    def test_404_search_questions(self):
        search = {'searchTerm': 'asd,.ndsa,madnsdashadksjadskl'}
        response = self.client().post('/questions/search', json=search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])

    def test_404_get_questions_by_category(self):
        response = self.client().get('/categories/99/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    def test_quizzes(self):
        question = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        response = self.client().post('/quizzes', json=question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


    def test_422_quizzes(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()