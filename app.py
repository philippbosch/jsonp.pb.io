from flask import Flask, request, abort, make_response
import re
from urllib2 import urlopen

app = Flask(__name__)
whitelist_patterns = (
    '^http://where.yahooapis.com/geocode',
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
    u = urlopen(url)
    if u.code != 200:
        abort(u.code)
    json = u.read()
    jsonp = "%s(%s);" % (callback, json)
    resp = make_response(jsonp)
    resp.status_code = u.code
    resp.headers = dict(u.headers)
    resp.content_type = u.headers.get('Content-Type', 'application/json; charset=utf-8')
    return resp

if __name__ == "__main__":
    app.debug = True
    app.run()