from watson_developer_cloud import AssistantV1
import json
from service.database import DataBase

db = DataBase()

class Assistant():

    def __init__(self):

        self.assistant = AssistantV1(
            version='2019-03-17',
            username='apikey',
            password='Z6qqko3QC1tg39Fmu8_j1lWgu3040G0Ns5PXQUhBDekx',
            url='https://gateway.watsonplatform.net/assistant/api'
        )

    def start_conversation(self, user, persist=True):

        response = self.assistant.message(
            workspace_id='911ed507-9118-425c-8fd8-594b547f8583',
            context={'cliente': user}
        ).get_result()

        conversation_id = response['context']['conversation_id']
        messages = response['output']['text']

        if persist:
            db.insert_new_conversation(conversation_id, user, messages)

        return {'id': conversation_id, 'messages': messages}

    def continue_conversation(self, user, conversation_id, message, persist=True):

        response = self.assistant.message(
            workspace_id='911ed507-9118-425c-8fd8-594b547f8583',
            context={'cliente': user, 'conversation_id': conversation_id},
            input={'text': message}
        ).get_result()

        messages =[message] + response['output']['text']

        if persist:
            db.update_conversation(conversation_id, messages)

        return {'id': conversation_id, 'messages': messages}