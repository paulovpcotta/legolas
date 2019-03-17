# *******************************************************************
#
# Author : Gabriel Nogueira, 2019
# C-Key  : c1297800
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from pymongo import MongoClient
import datetime

class DataBase():
    #TODO: new methods and URI for dev and production with necessary 

    def __init__(self):
        URI_LOCAL = "mongodb://localhost:27017"
        self.client = MongoClient(URI_LOCAL) 
        self.database = self.client.chat_legolas

    def close_connection(self):
        self.client.close()

    def check_conversation(self, conversation_id):
        """
        Verify if a conversation id are in use.

        Paras:
            - conversation_id: the if of conversation to check.

        """

        collection = self.database['conversation']
        find = collection.find_one({'conversation_id': conversation_id})
        if find:
            return True
        else:
            return False

    def insert_new_conversation(self, conversation_id:str, user:str, messages:str):
        """
        Insert a new conversation recently started with the watson chatbot.

        Paras:
            - conversation_id: The id of the conversation. (Used as Primary Key)
            - messages: New messages to update the array of messages.
            - user: Person who started the conversation

        """

        conversation = {
            'conversation_id': conversation_id,
            'user': user,
            'messages': [{'message': message, 'time': datetime.datetime.today()} for message in messages]
        }

        collection = self.database['conversation']
        collection.insert_one(conversation)

    def update_conversation(self, conversation_id : str , messages : str):
        """
        Used to update a array of messages inserting a new one in the collection conversation.

        Paras:
            - conversation_id: The id of the conversation. (Used as Primary Key)
            - messages: New messages to update the array of messages.

        """

        collection = self.database['conversation']

        if self.check_conversation(conversation_id):
            [collection.update({'conversation_id': conversation_id}, {'$push': {'messages': {'message': message, 'time': datetime.datetime.today()}}}) for message in messages]