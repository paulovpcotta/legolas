# *******************************************************************
#
# Author : Gabriel Nogueira, 2019
# C-Key  : c1297800
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from watson_developer_cloud import AssistantV1
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import TextToSpeechV1
import json
from service.database import DataBase
# from database import DataBase # Use only when is local test

db = DataBase()

class Assistant():

    def __init__(self):

        self.assistant = AssistantV1(
            version='2019-03-17',
            username='apikey',
            password='Z6qqko3QC1tg39Fmu8_j1lWgu3040G0Ns5PXQUhBDekx',
            url='https://gateway.watsonplatform.net/assistant/api'
        )

    def start_conversation(self, user:str, persist=True) -> dict:   
        """
        This function start a new conversation with the user who are logged in and watson chatbot.

        Params:
            - user: User who started the conversation.
            - persist: This variable defines if the conversation will be saved in the MongoDB. (default = True)

        Return:
            - Dict with the id of the conversation and the messages of the bot at the start of the conversation.

        TODO: Treat exceptions.

        """

        response = self.assistant.message(
            workspace_id='911ed507-9118-425c-8fd8-594b547f8583',
            context={'cliente': user}
        ).get_result()

        conversation_id = response['context']['conversation_id']
        messages = response['output']['text']

        if persist:
            db.insert_new_conversation(conversation_id, user, messages)

        return {'id': conversation_id, 'messages': messages}

    def continue_conversation(self, user:str, conversation_id:str, message:str, persist=True) -> dict:
        """
        Continue a conversation already started with the watson chatbot.

        Params:
            - user: User who started the conversation.
            - conversation_id: needed to know what chatbot conversation to recover.
            - message: A string with the messages to sendo to watson.
            - persist: This variable defines if the conversation will be saved in the MongoDB. (default = True)

        Return:
            - Dict with the id of the conversation and the messages sent by the user and the answer of the bot.

        TODO: Treat exceptions.

        """

        response = self.assistant.message(
            workspace_id='911ed507-9118-425c-8fd8-594b547f8583',
            context={'cliente': user, 'conversation_id': conversation_id},
            input={'text': message}
        ).get_result()

        messages = [message] + response['output']['text']

        if persist:
            db.update_conversation(conversation_id, messages)

        return {'id': conversation_id, 'messages': messages}

class Stt():

    def __init__(self):

        self.stt = SpeechToTextV1(
            iam_apikey='GO7GuxJB2TUqYzmNnBO7MM4l_s6Op2eFbBOmu516Id6f',
            url='https://stream.watsonplatform.net/speech-to-text/api'
        )


    def recognize(self, audio:bytes) -> dict:

        response  = self.stt.recognize(
            audio=audio,
            content_type='audio/mp3',
            model='pt-BR_BroadbandModel'
            ).get_result()

        return response['results'][0]['alternatives'][0]['transcript']

class Tts():

    def __init__(self):
        
        self.text_to_speech = TextToSpeechV1(
            iam_apikey='azNQmwP6chQBX8Tm-6cp7Dmv8-4jw1B8hxq_Hky1ZAzC',
            url='https://stream.watsonplatform.net/text-to-speech/api'
        )

    def synthesize(self, text:str) -> bytes:
        
        response = self.text_to_speech.synthesize(
                        text,
                        'audio/mp3',
                        'pt-BR_IsabelaVoice'
                    ).get_result().content


        return response