from flask import Flask, request, json, render_template
import hashlib
import base64
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_URL = "https://simple-website-lock-ab27.firebaseio.com/"


def hash(str):
    return hashlib.md5(str.encode('utf-8')).hexdigest()


def encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    encoded_string = encoded_string.encode('utf-8')
    return base64.urlsafe_b64encode(encoded_string).rstrip(b'=')


def decode(key, string):
    string = base64.urlsafe_b64decode(string + b'===')
    string = string.decode('utf-8')
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string


def add_entry(entry):
    entry['hash'] = hash(entry['password'])
    entry['success'] = encode(entry['password'], entry['success']).decode("utf-8")
    entry.pop('password', None)

    data = json.dumps(entry)

    r = requests.post(BASE_URL + 'keys.json', data=data)
    name = r.json()["name"]

    return name


def checker(name, user_password):
    resp = requests.get(BASE_URL + "keys/" + name + ".json").json()

    # check if user password is valid
    if hash(user_password) == resp["hash"]:
        # decode the success text
        decoded_success = resp["success"].encode("utf-8")
        decoded_success = decode(user_password, decoded_success)

        return decoded_success
    else:
        return False


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/embed/<name>')
def embed(name):
    return render_template("embed.html", name=name)


@app.route('/api/add', methods=['POST'])
def add():
    data = request.form

    name = add_entry(data.to_dict())
    return name


@app.route('/api/check', methods=['GET'])
def user():
    name = request.args.get("name")
    user_password = request.args.get("password")

    success = checker(name, user_password)

    if success != False:
        return {'success' : success}
    else:
        return app.response_class(json.dumps(False), content_type='application/json')



@app.route('/api/get', methods=['GET'])
def get_data():
    name = request.args.get("name")
    resp = requests.get(BASE_URL + "keys/" + name + ".json").json()
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
