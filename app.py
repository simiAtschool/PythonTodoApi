from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'  #mysql://username:password@host:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/tododb'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    done = db.Column(db.Boolean)
    created = db.Column(db.DateTime, server_default=db.func.now())
    finished_on = db.Column(db.DateTime, server_default=None, nullable=True)

    def __init__(self, title):
        self.title = title
        self.done = False

    def __repr__(self):
        return f'<Todo {self.title}>'


@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    todosjson = [todo.to_dict() for todo in todos]
    return jsonify({'todos': todosjson})


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'not found'}), 404
    else:
        return jsonify({'todo': todo.to_dict()})


@app.route('/todos', methods=['POST'])
def create_todo():
    body = request.get_json()
    todo = Todo(body['title'])
    db.session.add(todo)
    db.session.commit()
    return jsonify({'todo': todo.to_dict()})


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo_by_id(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'not found'}), 404
    else:
        body = request.get_json()
        if 'title' in body:
            todo.title = body['title']
        if 'done' in body:
            todo.done = body['done']
        if todo.done:
            todo.finished_on = db.func.now()
        else:
            todo.finished_on = None
        db.session.commit()
        return jsonify({'todo': todo.to_dict()})


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo_by_id(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'not found'}), 404
    else:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'result': True})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
