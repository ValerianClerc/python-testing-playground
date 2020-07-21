from flask import Flask, request, jsonify
import os
from tinydb import TinyDB, Query
from functools import wraps

app = Flask(__name__)
app.wsgi_app = middleware.Middleware(app.wsgi_app)
db = TinyDB('./db.json')
port = int( os.getenv( 'PORT', 5000 ) )
api_token = os.getenv('API_TOKEN', 'this-is-an-api-token')

def verify_body(body):
    try:
        return body['title'] and body['content']
    except:
        return False

@app.before_request
def verify_token():
    if request.headers['X-Api-Token'] != api_token:
        return jsonify({'msg': 'Unauthorized'}), 401

@app.route('/')
def root():
    return jsonify({'msg': 'root route of api'}), 200

@app.route('/blogs', methods=['GET'])
def index():
    Blog = Query()
    blogs = db.search(Blog['type'] == 'blog')
    return jsonify(blogs), 200

@app.route('/blogs/<blog_title>', methods=['GET'])
def show(blog_title):
    Blog = Query()
    blogs = db.search((Blog['type'] == 'blog') & (Blog['title'] == blog_title))
    resp = blogs[0] if len(blogs) > 0 else {}
    if resp == {}:
        return jsonify({'msg': 'blog with that name not found'}), 404
    return jsonify(resp), 200

@app.route('/blogs', methods=['POST'])
def create():
    body = request.json
    valid = verify_body(body)
    if not valid:
        return jsonify({'msg': 'invalid request body'}), 400
    
    Blogs = Query()
    q = db.search((Blogs['type'] == 'blog') & (Blogs['title'] == body['title']))
    if len(q) != 0:
        return jsonify({'msg': 'blog with that title already exists'}), 409
    
    new_blog = {
        'type': 'blog',
        'title': body['title'],
        'content': body['content']
    }
    db.insert(new_blog)

    return jsonify(new_blog), 200

@app.route('/blogs/<blog_title>', methods=['DELETE'])
def delete(blog_title):
    Blog = Query()
    q = db.search((Blog['type'] == 'blog') & (Blog['title'] == blog_title))
    if len(q) == 0:
        return jsonify({'msg': 'blog with that name not found'}), 404
    
    db.remove((Blog['type'] == 'blog') & (Blog['title'] == blog_title))
    return jsonify({'msg': 'blog deleted'}), 200

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=port, debug=True)