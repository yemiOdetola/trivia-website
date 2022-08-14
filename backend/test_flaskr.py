import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        
    def test_get_page_unavailable(self):
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
    
    def test_delete_question(self):
        res = self.client().delete("/questions/9")
        data = json.loads(res.data)

        question = Question.query.get(9)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(question, None)

    def test_delete_question_fail(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        
    def test_create_question(self):
        new_question = {
            'question': "What is this test?",
            'answer': "Nothing",
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_get_questions_in_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Art')

    def test_questions_in_category_error(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_question_search_with_results(self):
        res = self.client().post('/questions', json={"searchTerm": "Largest Lake"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    
    
    def test_question_search_with_error(self):
        res = self.client().post('/questions', json={"searchTerm": "Largest Ocean"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], None)
        self.assertEqual(data['questions'], [])
        self.assertEqual(data['total_questions'], 0)
        
    def test_next_question(self):
        res = self.client().post('/quizzes',
            json={
                "previous_questions":[],
                "quiz_category": {"id":0, "type":"All"}
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data['question'], None)

    def test_422_get_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions': []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Processable')

if __name__ == "__main__":
    unittest.main()