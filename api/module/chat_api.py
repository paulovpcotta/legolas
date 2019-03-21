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
from pydub import AudioSegment
import os
import subprocess
import ftplib
import time

import logging

chat = Blueprint('chat', __name__)
assistant = Assistant()
stt = Stt()
tts = Tts()

# @chat.route('/start_conversation', methods=['POST'])
# def start():
#     """
#     Used to open a conversation with the watson chatbot and a user
#     Uri: localhost:2931/chat/start_conversation

#     Params:
#         - name: The name of the person who started de conversation or logged in a app.
#         - persist: Used to persist or not the conversation in the database. (default = True) 
#         - audio: Used to make a representations of messages in audio. (default = None)
#     Return:
#         Dict with the id of the conversation and a list of messages of the bot at the start of the conversation,
#         is audio is set as True, return an audio representation of the messages.
#     """
#     logger = logging.getLogger(__name__)

#     try:
#         logger.info("start_conversation: Getting parameters from request")

#         req = request.json
#         name = req['name']
#         persist = req['persist'] if req.get('persist') is not None else True
#         audio = req['audio'] if req.get('audio') is not None else None

#     except:
#         logger.error("start_conversation: Error getting parameters from request")

#         return jsonify({'id': None, 'messages': None}, 400)

#     try:
#         logger.info("start_conversation: Starting a new conversation")

#         data_dict = assistant.start_conversation(name, persist=persist)

#         if audio:
#             data_dict['speechs'] = [base64.encodebytes(tts.synthesize(message)).decode("utf-8") for message in data_dict['messages']]

#         return jsonify(data_dict)

#     except Exception as err:
#         logger.error("start_conversation: Error starting the conversation", exc_info=True)

#         return jsonify({'id': None, 'messages': None})


@chat.route('/conversation', methods=['POST'])
def send():
    """
    Used to continue a conversation already started with the watson chatbot and a user.
    Uri: localhost:2931/chat/send_message

    CAUTION: if the conversation aren't started, the application may have some issues.

    Params:
        - context
        - message: A string of the message of the user. (default = None)
        - persist: Used to persist or not the conversation in the database. (default = True) 
        - audio: Message sent from the user as audio encoded in base64. (default = None)
        - bot_audio: Generate a audio from the text that watson return. (default = True)
    Return:
        Dict with the id of the conversation and a list of messages of the bot at the start of the conversation,
        is audio is set as True, return an audio representation of the messages.
    """
    logger = logging.getLogger(__name__)
    try:
        logger.info("send: Getting parameters from request")

        req = request.json
        name = req['name'] if req.get('name') is not None else None
        context = req['context'] if req.get('context') is not None else None
        message = req['message'] if req.get('message') is not None else None
        persist = req['persist'] if req.get('persist') is not None else True
        audio = base64.decodebytes(req['audio'].encode()) if req.get('audio') is not None else None
        bot_audio = req['bot_audio'] if req.get('bot_audio') is not None else True

    except:
        logger.error("send: Error getting parameters from request")

        return jsonify({'id': None, 'messages': None}, 400)

    try:
        logger.info(f"send: Communicating with Watson")

        if not context:
            context = {"cliente": name}

        if audio:  
            
            with open('audio.aiff', 'wb') as f:
                f.write(audio)

            subprocess.run(['ffmpeg', '-i', 'audio.aiff', '-f', 'mp3', '-acodec', 'libmp3lame', '-ab', '320000', '-ar', '44100', 'audio.mp3'])
            
            with open('audio.mp3', 'rb') as f:
                message = stt.recognize(f)

            os.remove('audio.aiff')
            os.remove('audio.mp3')


        data_dict = assistant.conversation(message, context, persist=persist)

        if audio or bot_audio:
            data_dict['speechs'] = [base64.encodebytes(tts.synthesize(message)).decode("utf-8") for message in data_dict['answers']]

        return jsonify(data_dict)
    
    except Exception as err:
        logger.error(f"send: Error communicating with Watson", exc_info=True)

        return jsonify({'context': None, 'answers': None, 'speechs': None, 'message':None})


@chat.route('/audio_gambira', methods=['POST'])
def audioGambira():
    #static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'serving_static')
    objLegolas = request.json
    print(objLegolas)
    #os.remove('audio.mp3')
    name = str(int(time.time())) + '.mp3'
    with open('audio.aiff', 'wb') as f:
        if('[' not in objLegolas['base64']):
            f.write(base64.decodebytes(objLegolas['base64'][0].encode()))
        else:
            f.write(base64.decodebytes(objLegolas['base64'].encode()))

    subprocess.run(['ffmpeg', '-i', 'audio.aiff', '-f', 'mp3', '-acodec', 'libmp3lame', '-ab', '320000', '-ar', '44100', name])

    session = ftplib.FTP('ftp.cafofobinladen.com.br','cafofobinladen','Fabiane0912@')
    file = open(name, 'rb')                  # file to send
    session.storbinary('STOR ./Web/' + name, file)     # send the file
    file.close()                                    # close file and FTP
    session.quit()

    #return send_file('audio.mp3', mimetype='audio/x-wav', attachment_filename='audio.mp3')
    #return send_from_directory('./serving_static', 'audio.mp3', as_attachment=True)
    return 'http://cafofobinladen.com.br/' + name