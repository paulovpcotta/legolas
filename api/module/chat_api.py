# *******************************************************************
#
# Author : Gabriel Nogueira, 2019
# C-Key  : c1297800
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from flask import Flask, request, Blueprint, jsonify
from service.watson import Assistant

chat = Blueprint('chat', __name__)
assistant = Assistant()

@chat.route('/start_conversation', methods=['POST'])
def start():
    """
    Used to open a conversation with the watson chatbot and a user.
    Route: localhost:2931/chat/start_conversation

    Params:
        - name: The name of the person who started de conversation or logged in a app.
    Return:
        - Dict with the id of the conversation and the messages of the bot at the start of the conversation.
    """

    req = request.json
    name = req['name']

    return jsonify(assistant.start_conversation(name))

@chat.route('/send_message', methods=['POST'])
def send():
    """
    Used to continue a conversation already started with the watson chatbot and a user.
    Route: localhost:2931/chat/send_message

    CAUTION: if the conversation aren't started, the application may have some issues.

    Params:
        - name: The name of the person who started de conversation or logged in a app.
        - id: Conversation id that is sent to watson to recovery the conversation already started.
        - message: A string of the message of the user.
    Return:
        - Dict with the id of the conversation and the messages of the bot at the start of the conversation.
    """

    req = request.json
    name = req['name']
    conversation_id = req['id']
    message = req['message']

    return jsonify(assistant.continue_conversation(name, conversation_id, message))