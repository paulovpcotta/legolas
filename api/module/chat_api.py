# *******************************************************************
#
# Author : Gabriel Nogueira, 2019
# C-Key  : c1297800
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from flask import Flask, request, Blueprint, jsonify
import base64
from service.watson import Assistant, Stt, Tts

import logging

chat = Blueprint('chat', __name__)
assistant = Assistant()
stt = Stt()
tts = Tts()

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
        persist = req['persist'] if req.get('persist') is not None else True
        audio = req['audio'] if req.get('audio') is not None else None

    except:
        logger.error("start_conversation: Error getting parameters from request")

        return jsonify({'id': None, 'messages': None}, 400)

    try:
        logger.info("start_conversation: Started a new conversation")

        data_dict = assistant.start_conversation(name, persist=persist)

        if audio:
            data_dict['speechs'] = [base64.encodebytes(tts.synthesize(message)).decode("utf-8") for message in data_dict['messages']]

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
        message = req['message'] if req.get('message') is not None else None
        persist = req['persist'] if req.get('persist') is not None else True
        audio = req['audio'] if req.get('audio') is not None else None
        base_64 = req['base64'] if req.get('base64') is not None else None

    except:
        logger.error("send_message: Error getting parameters from request")

        return jsonify({'id': None, 'messages': None}, 400)

    try:
        logger.info(f"send_message: Conversation {conversation_id} continued")

        if audio and base_64:
            
            speech = base64.decodebytes(base_64.encode())
            text = stt.recognize(speech)

            data_dict = assistant.continue_conversation(name, conversation_id, text, persist=persist)
            data_dict['speechs'] = [base64.encodebytes(tts.synthesize(message)).decode("utf-8") for message in data_dict['messages']]

        elif message:
            data_dict = assistant.continue_conversation(name, conversation_id, message, persist=persist)
        else:
            return jsonify({'id': None, 'messages': None}) 

        return jsonify(data_dict)
    
    except Exception as err:
        logger.error(f"send_message: Error returning to conversation {conversation_id}", exc_info=True)

        return jsonify({'id': None, 'messages': None})