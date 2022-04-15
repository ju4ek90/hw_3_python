from flask import Flask, jsonify, request, abort
from flask_httpauth import HTTPBasicAuth
# from flask_jwt_extended.view_decorators import fresh_jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity
)
from datetime import timedelta
from flask_caching import Cache
import time

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "JWT_SECRET_KEY": 'super2-secret',
}

EXPIRE = 20

def safe_list_get (l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

app = Flask(__name__)
auth = HTTPBasicAuth()

app.config.from_mapping(config)

cache = Cache(app)
jwt = JWTManager(app)

users = {
    "sergii": generate_password_hash("hello"),
    "test": generate_password_hash("bye"),
    "test": generate_password_hash("test")
}

items = []


@app.route('/', methods=['GET'])
@auth.login_required
def pass200_no_auth():
    return jsonify(response='ok')


@app.route('/', methods=['POST'])
def pass200_no_auth_post():
    return jsonify(json=request.json)


@app.route('/items_unsafe', methods=['GET'])
@jwt_required()
def pass200_unsafe():
    item = safe_list_get(items, int(item_id), None)
    if item is None:
        abort(400, 'Not exist')

    return jsonify(items=item)


@app.route('/items', methods=['GET', 'PUT', 'PATCH'])
@jwt_required()
def pass200():
    return jsonify(items=items)


@app.route('/items/<string:item_id>', methods=['GET', 'PUT', 'PATCH'])
@jwt_required()
def item_id(item_id):
    item = safe_list_get(items, int(item_id), None)
    if item is None:
        abort(400, 'Not exist')

    return jsonify(items=item)



@app.route('/items/<string:item_id>', methods=['POST'])
@jwt_required()
def item_id_search(item_id):
    item = safe_list_get(items, int(item_id), None)
    if item is None:
        abort(400, 'Not exist')

    items.filter()

    return jsonify(items=item)


@app.route('/items', methods=['POST'])
@jwt_required()
def pass201():
    item = request.json
    print("Income JSON: {}".format(item))
    items.append(item)

    return jsonify(id=len(items)), 201


@app.route('/items/<string:item_id>', methods=['DELETE'])
@jwt_required()
def delete(item_id):
    del items[int(item_id)]
    return 'ok'

@app.route('/fail500')
def fail500():
    return (501, "please wait")
    return 1 + 's'

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@app.route('/basic_auth')
@auth.login_required
def index():
    return "Hello, %s!" % auth.username()


# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401

@app.route('/development/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    expires = timedelta(minutes=100500)
    ret = {
        'access_token': create_access_token(identity=username, expires_delta=expires, fresh=True),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


@app.route('/login', methods=['POST'])
def login_test():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    expires = timedelta(minutes=EXPIRE)
    ret = {
        'access_token': create_access_token(identity=username, expires_delta=expires, fresh=True),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    expires = timedelta(minutes=EXPIRE)
    ret = {
        'access_token': create_access_token(identity=current_user, expires_delta=expires, fresh=False),
    }
    return jsonify(ret), 200


@app.route('/protected', methods=['GET'])
@jwt_required(fresh=True)
def protected():
    username = get_jwt_identity()
    return jsonify(logged_in_as=username), 200


@app.route('/cached', methods=['GET'])
@cache.cached(timeout=5)
# @jwt_required()
def cached():
    print("SLEEP 10")
    time.sleep(10)
    # username = get_jwt_identity()
    return "cached"
    # return jsonify(logged_in_as=username), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)
