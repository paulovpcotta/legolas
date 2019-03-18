import logging.config

from flask import Flask, Blueprint
# from module.legolas_api import api
from module.chat_api import chat

app = Flask(__name__)

# app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(chat, url_prefix='/chat')

@app.route("/status")
def status():

    return "<h1>You have my bow.</h1>" 

if __name__=='__main__':
    logging.config.fileConfig('log/logger.conf')

    LOGGER = logging.getLogger(__name__)

    app.secret_key = '65b46g4f68g4f6s4g6a5v465afg8aa5'
    app.run(host='0.0.0.0', port=2933, debug=True)