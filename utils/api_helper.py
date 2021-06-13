# ----------------------------------------------------------------------------#
# API routes
# ----------------------------------------------------------------------------#


# root_url = "/"
# @app.route("/artists")
# @app.route("/artists/<int:artist_id>")
# @app.route("/artists/<int:artist_id>/edit", methods=["GET"])
# @app.route("/artists/<int:artist_id>/edit", methods=["POST"])
# @app.route("/artists/create", methods=["GET"])
# @app.route("/artists/create", methods=["POST"])
# @app.route("/artists/search", methods=["POST"])
# @app.route("/shows")
# @app.route("/shows/create")
# @app.route("/shows/create", methods=["POST"])
# @app.route("/venues")
# @app.route("/venues/<int:venue_id>")
# @app.route("/venues/<int:venue_id>/edit", methods=["GET"])
# @app.route("/venues/<int:venue_id>/edit", methods=["POST"])
# @app.route("/venues/<venue_id>", methods=["DELETE"])
# @app.route("/venues/create", methods=["GET"])
# @app.route("/venues/create", methods=["POST"])
# @app.route("/venues/search", methods=["POST"])

import requests


def request(method="GET", endpoint="", data=None):
    if not data:
        data = {}
    base_url = "http://localhost:5000"
    url = base_url + endpoint
    headers = {"api": "true"}
    r = requests.request(method, url, headers=headers, data=data)
    print(r.json())


request(endpoint="/venues")
request(method="post", endpoint="/venues/search")
request(method="get", endpoint="/venues/1")
