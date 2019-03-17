import logging.config

from flask import Flask, Blueprint
from module.legolas_api import api

app = Flask(__name__)

app.register_blueprint(api, url_prefix='/api')

if __name__=='__main__':
    logging.config.fileConfig('log/logger.conf')

    LOGGER = logging.getLogger(__name__)

    app.secret_key = '65b46g4f68g4f6s4g6a5v465afg8aa5'
    app.run(host='0.0.0.0', port=2931, debug=True)