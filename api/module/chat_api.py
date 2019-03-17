from flask import Flask, request, Blueprint, jsonify
from service.watson import Assistant

chat = Blueprint('chat', __name__)
assistant = Assistant()

@chat.route('/start_conversation', methods=['POST'])
def start():

    req = request.json
    name = req['name']

    return jsonify(assistant.start_conversation(name))

@chat.route('/send_message', methods=['POST'])
def send():

    req = request.json
    name = req['name']
    conversation_id = req['id']
    message = req['message']

    return jsonify(assistant.continue_conversation(name, conversation_id, message))