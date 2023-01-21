"""
https://www.youtube.com/watch?v=z6q9kug0PL0

"""

from flask import Flask
from flask import request
import json
import time

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def handle_request():
    text = str(request.args.get('input'))
    dataset = {'req': text, 'timestamp': time.time()}
    json_dump = json.dumps(dataset)
    return json_dump

