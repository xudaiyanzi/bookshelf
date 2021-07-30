import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book, db

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there. 
#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 
def pagination_books(request,selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    formatted_books = [book.format() for book in selection]
    current_books = formatted_books[start:end]

    return current_books

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # @TODO: Write a route that retrivies all books, paginated. 
  #         You can use the constant above to paginate by eight books.
  #         If you decide to change the number of books per page,
  #         update the frontend to handle additional books in the styling and pagination
  #         Response body keys: 'success', 'books' and 'total_books'
  # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

  @app.route('/books', methods=['GET'])
  def get_books():

    selections = Book.query.order_by(Book.id).all()
    current_books = pagination_books(request,selections)

    if len(current_books) == 0:
      abort(404)

    else:
      total_books = len(selections)

    return jsonify({
      'success': True,
      'books': current_books,
      'total_books': total_books
    })

  # @TODO: Write a route that will update a single book's rating. 
  #         It should only be able to update the rating, not the entire representation
  #         and should follow API design principles regarding method and route.  
  #         Response body keys: 'success'
  # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

####################################
  ## test this route in termial with the following command:
  ## $curl -i -H "Content-Type: application/json" -X PATCH -d '{"rating": "5"}' http://localhost:5000/books/1
  ## or
  ## $curl http://127.0.0.1:5000/books/1 -X PATCH -H "Content-Type: application/json" -d '{"rating":"5"}'

  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_book_rating(book_id):
    body = request.get_json()
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()    
      if book is None:
        abort(404)
      if 'rating' in body:

        book.rating = body['rating']
        ## OR use 'get' to retrive the rating in json
        # book.rating = int(body.get('rating'))
    
        book.update()

      return jsonify({'success': True,
                      'book': book.format(),
                      'id': book.id
                      })
    except:
      abort(404)

  # @TODO: Write a route that will delete a single book. 
  #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
  #        Response body keys: 'success', 'books' and 'total_books'

  # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
  ##################
  # to test this route in terminal with the following command:
  # $curl -X DELETE http://localhost:5000/books/1
  # or
  # $curl http://127.0.0.1:5000/books/1 -X DELETE

  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()
      if book is None:
        abort(404)
      else:
        book.delete()
        
        selections = Book.query.order_by(Book.id).all()
        current_books = pagination_books(request,selections)

        return jsonify({'success': True,
                        'deleted': book.id,
                        'books': current_books,
                        'total_books': len(selections)
                        })
    except:
      # code 422 Unprocessable Entity
      abort(422) 


  # @TODO: Write a route that create a new book. 
  #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
  # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books. 
  #       Your new book should show up immediately after you submit it at the end of the page. 

  ## different from get books route, which use 'GET' method to retrive all books
  ## this route use 'POST' method to create a new book

  #########
  # to test this route in terminal with the following command:
  # $curl -X POST -H "Content-Type: application/json" -d '{"title":"Neverwhere", "author":"Neil Gaiman", "rating": "5"}' http://127.0.0.1:5000/books

  @app.route('/books', methods=['POST'])
  def create_book():

    body = request.get_json()

    book_title = body.get('title', 'No title') ## if no title is provided, use 'No title'
    book_author = body.get('author', 'No author') ## if no author is provided, use 'No author'
    book_rating = body.get('rating', 'No rating') ## if no rating is provided, use 'No rating'

    try:
      book = Book(title=book_title, author=book_author, rating=book_rating)
      book.insert()

      selections = Book.query.order_by(Book.id).all()
      current_books = pagination_books(request,selections)

      return jsonify({'success': True,
                      'created': book.id,
                      'books': current_books,
                      'total_books': len(selections)
                    })
    except:
      abort(422)

  return app

    