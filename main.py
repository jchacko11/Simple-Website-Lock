from flask import Flask, request, json, render_template
import hashlib
import base64
import requests
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)

BASE_URL = "https://simple-website-lock-ab27.firebaseio.com/"


def get_hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


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
    entry['hash'] = get_hash(entry['password'])
    entry['success'] = encode(entry['password'],
                              entry['success']).decode("utf-8")
    entry.pop('password', None)

    data = json.dumps(entry)

    r = requests.post(BASE_URL + 'keys.json', data=data)
    name = r.json()["name"]

    return name


def checker(name, user_password):
    resp = requests.get(BASE_URL + "keys/" + name + ".json").json()

    # check if user password is valid
    if get_hash(user_password) == resp["hash"]:
        # decode the success text
        decoded_success = resp["success"].encode("utf-8")
        decoded_success = decode(user_password, decoded_success)

        return decoded_success
    else:
        return False


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/embed')
def embed():
    affirmative = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

    name = request.args.get("name")
    background = request.args.get("background")

    box = request.args.get("box")
    box = True if box and box.lower() in affirmative else False

    obscure = request.args.get("obscure")
    obscure = True if obscure and obscure.lower() in affirmative else False

    header = request.args.get("header")

    resp = requests.get(BASE_URL + "keys/" + name + ".json").json()
    if resp:
        return render_template("embed.html", name=name, background=background, box=box, header=header, obscure=obscure)
    else:
        return render_template("404.html"), 404


@app.route('/api/add', methods=['POST'])
def add():
    keys = ['password', 'success']
    data = request.form.to_dict()

    filtered_dict = {key: data[key] for key in keys}

    name = add_entry(filtered_dict)
    return name


@app.route('/api/check', methods=['GET'])
def user():
    name = request.args.get("name")
    user_password = request.args.get("password")

    success = checker(name, user_password)

    if success is not False:
        return {'success': success}
    else:
        return app.response_class(
            json.dumps(False), content_type='application/json')


@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
