# *******************************************************************
#
# Author : Gabriel Nogueira, 2019
# C-Key  : c1297800
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from flask import Flask, request, Blueprint, jsonify
from service.watson import Assistant

import logging

chat = Blueprint('chat', __name__)
assistant = Assistant()


@chat.route('/start_conversation', methods=['POST'])
def start():
    """
    Used to open a conversation with the watson chatbot and a user.
    Uri: localhost:2931/chat/start_conversation

    Params:
        - name: The name of the person who started de conversation or logged in a app.
    Return:
        - Dict with the id of the conversation and the messages of the bot at the start of the conversation.
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("start_conversation: Getting parameters from request")

        req = request.json
        name = req['name']
    except:
        logger.error("start_conversation: Error getting parameters from request")

        return jsonify({'id': None, 'messages': None}, 400)

    try:
        logger.info("start_conversation: Started a new conversation")

        data_dict = assistant.start_conversation(name)

        return jsonify(data_dict)

    except Exception as err:
        logger.error("start_conversation: Error starting the conversation", exc_info=True)

        return jsonify({'id': None, 'messages': None})


@chat.route('/send_message', methods=['POST'])
def send():
    """
    Used to continue a conversation already started with the watson chatbot and a user.
    Uri: localhost:2931/chat/send_message

    CAUTION: if the conversation aren't started, the application may have some issues.

    Params:
        - name: The name of the person who started de conversation or logged in a app.
        - id: Conversation id that is sent to watson to recovery the conversation already started.
        - message: A string of the message of the user.
    Return:
        - Dict with the id of the conversation and the messages of the bot at the start of the conversation.
    """
    logger = logging.getLogger(__name__)
    try:
        logger.info("send_message: Getting parameters from request")

        req = request.json
        name = req['name']
        conversation_id = req['id']
        message = req['message']

    except:
        logger.error("send_message: Error getting parameters from request")

        return jsonify({'id': None, 'messages': None}, 400)

    try:
        logger.info(f"send_message: Conversation {conversation_id} continued")

        data_dict = assistant.continue_conversation(name, conversation_id, message)

        return jsonify(data_dict)
    
    except Exception as err:
        logger.error(f"send_message: Error returning to conversation {conversation_id}", exc_info=True)

        return jsonify({'id': None, 'messages': None})
