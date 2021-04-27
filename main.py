from flask import Flask, redirect
from flask_caching import Cache

import config
import bbb_request

app = Flask(__name__)
app.config.from_mapping(config.flask)
cache = Cache(app)


@app.route('/', methods=['GET'])
@cache.cached()
def request():
    room_id = bbb_request.get_least_visited(config.room_ids)

    if room_id:
        return redirect(config.url + room_id[0])
    else:
        return "Currently no room is active. Please try again later!"


app.run()
