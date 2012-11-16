from flask import Flask, request, abort, make_response
import re
import requests

app = Flask(__name__)
whitelist_patterns = (
    '^http://where.yahooapis.com/geocode',
    '^http://kar2go.me/getInitData/',
    '^https://www.drive-now.com/php/metropolis/json.vehicle_filter',
)
whitelist_pattern = '('
for pattern in whitelist_patterns:
    whitelist_pattern += pattern + '|'
whitelist_pattern = whitelist_pattern[0:-1] + ')'
whitelist_re = re.compile(whitelist_pattern)
callback_re = re.compile('^[\w_]+$')

@app.route("/<path:url>")
def hello(url):
    if not "callback" in request.args:
        abort(500)
    callback = request.args.get('callback')
    if not callback_re.match(callback):
        abort(500)
    query_string = re.sub('&?callback=[^&]+', '', request.query_string)
    if len(query_string):
        url = "%s?%s" % (url, query_string)
    if not whitelist_re.match(url):
        abort(403)
    req = requests.get(url)
    if req.status_code != 200:
        abort(req.status_code)
    jsonp = u"%s(%s);" % (callback, req.text)
    resp = make_response(jsonp)
    resp.status_code = req.status_code
    resp.content_type = 'application/json; charset=utf-8'
    return resp

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0', port=5001)
