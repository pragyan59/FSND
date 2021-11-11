import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

    
def paginate_questions(request, selection_question):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection_question]
    current_questions = questions[start:end]

    return current_questions
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'*':{'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

  def get_categories_d():
      categories_all = Category.query.all()
      categories_d = {}
      for category in categories_all:
        categories_d[category.id] = category.type
      return categories_d

  '''
  
    
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def get_categories():
        return jsonify(
            {
                'success':True,
                'categories': get_categories_d(),
            }
        )


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route("/questions")
  def get_questions():
        selection_question = Question.query.order_by(Question.id).all()
        
        current_questions = paginate_questions(request, selection_question)
        category = Category.query.filter(Question.id==Category.id).first()
        # currentCategory = category.type
        if len(current_questions) == 0:
            abort(404)
        else:
            return jsonify(
            {
               'success': True,
               'questions': current_questions,
               'totalQuestions': len(Question.query.all()),
               'categories': get_categories_d(),
               'currentCategory': None,
            }

        )

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_questions(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            selection_question = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection_question)

            return jsonify(
                {
                    'success': True,
                    'deleted': question_id,
                }
            )

        except:
            abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route("/questions/add", methods=["POST"])
  def add_question():
        body = request.get_json()
        try:
                
                new_question_question = body.get("question", None)
                new_question_answer = body.get("answer", None)
                new_question_difficulty = body.get("difficulty", None)
                new_question_category = body.get("category", None)
              
                question = Question(question=new_question_question, answer=new_question_answer, difficulty=new_question_difficulty, category=new_question_category)
                question.insert()

                selection_question = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection_question)

                return jsonify(
                    {
                        'success': True,
                        'created': question.id,
                        'questions': current_questions,
                        'total_questions': len(Question.query.all()),
                    }
                )

        except:
            abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route("/questions/search", methods=["POST"])
  def search_question():
        body = request.get_json()
        search = body.get("searchTerm")
        try:
             if "searchTerm" in body:
        
                selection_question = Question.query.order_by(Question.id).filter(
                    Question.question.ilike(f'%{search}%')).all()
                current_questions = paginate_questions(request, selection_question)
                category = Category.query.filter(Question.id==Category.id).first()
                currentCategory = category.type
                return jsonify(
                    {
                        'success': True,
                        'questions': current_questions,
                        'total_questions': len(Question.query.all()),
                        'currentCategory': currentCategory,
                    }
                )

        except:
            abort(422)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:categories_id>/questions", methods=["GET"])
  def question_by_category(categories_id):
        try:
            category = Category.query.filter(categories_id==Category.id).first()
            currentCategory = category.type

            questions = Question.query.filter(Question.category == categories_id).all()
            
            if questions is None:
                abort(404)
            final_quest = [q.format() for q in questions]
            return jsonify(
                {
                  'success': True,
                  'questions': final_quest,
                  'totalQuestions': len(final_quest),
                  'currentCategory': currentCategory,
                }
            )

        except:
            abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods= ['POST'])
  def create_quiz():
        try:
            data = request.get_json()
            quiz_category = int(data['quiz_category']['id'])
            category_query = Category.query.get(quiz_category)
            previous_questions = data["previous_questions"]
            if not quiz_category == None:
                if "previous_questions" in data and len(previous_questions) > 0:
                    quiz_list = Question.query.filter(Question.id.notin_(previous_questions), Question.category == category_query.id).all()
                else:
                    quiz_list = Question.query.filter(Question.category == category_query.id).all()
            else:
                if "previous_questions" in data and len(previous_questions) > 0:
                    quiz_list = Question.query.filter(Question.id.notin_(previous_questions)).all()
                else:
                    quiz_list = Question.query.all()
            l = len(quiz_list) - 1
            if l > 0:
                random_ques = quiz_list[random.randint(0, l)].format()
            else:
                random_ques = False
            return jsonify({
                "success": True,
                "question": random_ques
            })
        except:
            abort(500)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

  @app.errorhandler(422)
  def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


  @app.errorhandler(405)
  def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )
  @app.errorhandler(500)
  def internal_server(error):
        return (
            jsonify({"success": False, "error": 500, "message": "Internal server error"}),
            500,
        )

  return app.  

    
