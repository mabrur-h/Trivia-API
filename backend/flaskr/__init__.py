import os
from flask import (
  Flask,
  request,
  abort,
  jsonify)
from models import (
  setup_db,
  Question,
  Category)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # set up cors
  CORS(app, resources={r"/api/*":{"origins":"*"}})


  # set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
    return response


  # GET requests for all available categories.
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })



  # pagination, get requests for questions.

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  @app.route('/questions')
  def get_questions():
    try:
      selection = Question.query.all()
      current_questions = paginate_questions(request, selection)

      categories = Category.query.all()
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type

      if (len(current_questions) == 0):
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'categories': categories_dict
      })
    except:
      abort(404)


  # delete question using a question ID
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(404)


  # POST question

  @app.route('/questions', methods=['POST'])
  def post_question():
    data = request.get_json()

    new_question = data.get('question', None)
    new_answer = data.get('answer', None)
    new_difficulty = data.get('difficulty', None)
    new_category = data.get('category', None)

    if ((new_question is None) or (new_answer is None) or (new_difficulty is None)
            or (new_category is None)):
      abort(422)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422)


  # search questions

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    data = request.get_json()
    if data.get('searchTerm'):
      search_term = data.get('searchTerm')
      selection = Question.query.filter(Question.question.ilike(f'%{search_term}%'))
      total = [question.format() for question in selection]

      if len(total) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': total,
        'current_category': None
      })
    else:
      abort(404)


  # get by category

  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    try:
      category = Category.query.filter_by(id=id).one()

      selection = Question.query.filter_by(category=category.id).all()
      paginated = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': paginated,
        'current_category': category.type
      })
    except:
      abort(404)


  # play quizzes

  @app.route('/quizzes', methods=['POST'])
  def quizzes():
    try:
      data = request.get_json()
      prev_q = data.get('previous_questions')
      # print(prev_q)
      category = data.get('quiz_category')['id']
      selection = Question.query.filter_by(category=category).all()
      questions = [question.format() for question in selection]
      sorted_questions = []
      for item in questions:
        if(item['id'] not in prev_q):
          sorted_questions.append(item)
      if len(sorted_questions) == 0:
        return jsonify({'question': False})
      random_question = random.choice(sorted_questions)
      return jsonify({
        'question': random_question,
        'success': True
      })

    except:
      abort(422)


  # errorhandlers

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Resource not found'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400


  return app

    