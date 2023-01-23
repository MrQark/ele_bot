import os
from flask import Flask
from flask import request
import json
import time

absolute_path = os.path.dirname(os.path.abspath(__file__))
cfg_file_path = os.path.join(absolute_path, "", "ele_bot_cfg.json")


def read_cfg():
    with open(cfg_file_path) as f:
        elebot_cfg = json.load(f)
    return elebot_cfg


def write_ping_counter(counter) -> None:
    elebot_cfg = read_cfg()
    with open(cfg_file_path, 'w') as f:
        elebot_cfg['counter'] = counter
        f.write(json.dumps(elebot_cfg))


app = Flask(__name__)

PING_COUNTER = 0
write_ping_counter(PING_COUNTER)


@app.route('/ele_bot_ping', methods=['GET', 'POST'])
def ele_bot_ping():
    global PING_COUNTER
    PING_COUNTER = PING_COUNTER + 1
    text = str(request.args.get('input'))
    dataset = {'req': text, 'timestamp': time.time()}
    json_dump = json.dumps(dataset)
    write_ping_counter(PING_COUNTER)
    return json_dump


if __name__ == "__main__":
    app.run(debug=True)
