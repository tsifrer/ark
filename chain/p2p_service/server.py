import json
import os
import platform
from copy import deepcopy

from flask import Flask, current_app, jsonify, request

from gunicorn.app.base import BaseApplication

from werkzeug.exceptions import HTTPException

from chain.common.config import config
from chain.common.utils import get_chain_version
from chain.p2p_service.exceptions import P2PException
from chain.p2p_service.external import close_db
from chain.p2p_service.views import peer


def _validate_request_headers():
    # Don't validate request headers for paths that start with /config
    if request.path.startswith("/config"):
        return None

    # TODO: Also validate that the values are correct
    required_headers = ["version", "nethash", "port"]
    errors = []
    for header in required_headers:
        if header not in request.headers:
            errors.append("Missing {} in request header".format(header))

    if errors:
        raise P2PException("Missing request headers", payload={"errors": errors})
    return None


# TODO: tests for this
def _accept_request():
    if request.headers.get("x-auth") == "forger" or request.path.startswith("/remote"):
        if request.remote_addr in config.p2p_service["remote_access"]:
            return None
        else:
            raise P2PException("Forbidden", status_code=403)

    # Only forger requests are allowed to access /internal
    if request.path.startswith("/internal"):
        raise P2PException("Forbidden", status_code=403)


def _handle_api_errors(ex):
    if isinstance(ex, HTTPException):
        data = {"success": False, "status_code": ex.code, "message": ex.description}
    elif isinstance(ex, P2PException):
        data = ex.to_dict()
    else:
        data = {
            "success": False,
            "status_code": 500,
            "message": "Internal Server Error",
        }

    log = current_app.logger.debug
    if data["status_code"] >= 500:
        log = current_app.logger.exception
    elif data["status_code"] >= 400:
        log = current_app.logger.debug

    log_data = deepcopy(data)
    log_data["error"] = str(ex)
    log(json.dumps(log_data))
    return jsonify(data), data["status_code"]


def _set_default_response_headers(response):
    # Core implementation also sets `height` in the headers, but I it doesn't seem
    # to be used anywhere and it just adds an extra DB query on each request.
    response.headers["nethash"] = config.network["nethash"]
    response.headers["version"] = get_chain_version()
    response.headers["port"] = 4002  # TODO: get this from the config somewhere
    response.headers["os"] = platform.system().lower()
    return response


class P2PService(BaseApplication):
    def __init__(self):
        self.options = {
            "bind": "{}:{}".format(os.environ.get("SERVER_HOST", "127.0.0.1"), "8080"),
            "workers": 1,  # number_of_workers(),
            "accesslog": "-",
        }
        self.application = create_app()
        super().__init__()

    def load_config(self):
        cfg = dict(
            [
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in cfg.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def create_app():
    app = Flask(__name__)

    app.teardown_appcontext(close_db)

    # Error handlers
    app.register_error_handler(Exception, _handle_api_errors)

    # Before request
    app.before_request(_validate_request_headers)
    app.before_request(_accept_request)

    # After request
    app.after_request(_set_default_response_headers)

    # Blueprints
    app.register_blueprint(peer.blueprint(), url_prefix="/peer")
    return app


def start_server():
    P2PService().run()
