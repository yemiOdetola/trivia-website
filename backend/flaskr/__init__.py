import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
db = SQLAlchemy()


def paginate_data(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        categories_obj = {}

        if not categories:
            abort(404)

        for category in categories:
            categories_obj[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categories_obj
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions_all = Question.query.all()
        paginated_questions = paginate_data(request, questions_all)

        if not paginated_questions:
            abort(404)

        try:
            categories_all = Category.query.all()
            categories_obj = {}
            for category in categories_all:
                categories_obj[category.id] = category.type

            # return all required data to view
            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(questions_all),
                'categories': categories_obj
            })
        except:
            db.session.rollback()
            print(sys.exc_info())
            abort(422)
        finally:
            db.session.close()

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if not question:
                abort(404)

            question.delete()
            questions_all = Question.query.all()
            current_questions = paginate_data(request, questions_all)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions_all)
            })

        except Exception:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=['POST'])
    def create_search_question():

        try:
            req_body = request.get_json()
            search = req_body.get('searchTerm', None)
            if search:
                filtered_questions = Question.query.filter(Question.question.ilike(f'%{search}%'))\
                    .order_by(Question.difficulty)\
                    .all()
                paginated_questions = paginate_data(request, filtered_questions)
                return jsonify({
                    'success': True,
                    'questions': paginated_questions,
                    'total_questions': len(filtered_questions),
                    'current_category': None
                })
            else:
                question = req_body['question']
                answer = req_body['answer']
                category = req_body['category']
                difficulty = req_body['difficulty']
                new_question = Question(question, answer, category, difficulty)
                new_question.insert()
                return jsonify({
                    "success": True
                })
        except Exception as e:
            print(str(e))
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_question_by_category(id):
        category = Category.query.get(id)
        if not category:
            abort(404)

        try:
            questions_all = Question.query.filter_by(category=category.id).all()
            paginated_questions = paginate_data(request, questions_all)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'current_category': category.type,
                'total_questions': len(questions_all)
            })
        except:
            abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:
            request_body = request.get_json()
            category = request_body.get('quiz_category')
            available_questions = None
            if category['id'] != 0:
                available_questions = Question.query\
                    .filter(Question.category == category['id'])\
                    .order_by(Question.difficulty)\
                    .all()
            else:
                available_questions = Question.query.order_by(Question.difficulty).all()
            print('available_q: ', available_questions)
            quiz_question = available_questions[random.randrange(0, len(available_questions))].format()\
            if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': quiz_question
            })
        except Exception as error:
            print('error: ', error)
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable request"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    return app
