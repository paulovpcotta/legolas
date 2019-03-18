# *******************************************************************
#
# Author : Gabriel Nogueira, 2019
# C-Key  : c1297800
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from pymongo import MongoClient
import datetime

import logging

class DataBase():
    #TODO: new methods and URI for dev and production with necessary 

    def __init__(self):
        """
        Change between URI to get acess to different mongodb.
        """
        URI_LOCAL = "mongodb://localhost:27017"
        # URI_DEV =
        # URI_PROD = 
 
        self.client = MongoClient(URI_LOCAL) # Change URI in here
        self.database = self.client.chat_legolas # Change the after after the last dot to acess other database

    def close_connection(self):
        self.client.close()

    def check_conversation(self, conversation_id:str) -> bool:
        """
        Verify if a conversation id are in use.

        Params:
            - conversation_id: the id of conversation to check.

        """
        logger = logging.getLogger(__name__)

        try:
            logger.info(f"DataBase::check_conversation: Checking if exist {conversation_id} in the database")

            collection = self.database['conversation']
            find = collection.find_one({'conversation_id': conversation_id})
            if find:
                return True
            else:
                return False
        except:
            logger.error(f"DataBase::check_conversation: Error checking if exist {conversation_id} in the database", exc_info=True)

            return False

    def insert_new_conversation(self, conversation_id:str, user:str, messages:str):
        """
        Insert a new conversation recently started with the watson chatbot.

        Params:
            - conversation_id: The id of the conversation. (Used as Primary Key)
            - messages: New messages to update the array of messages.
            - user: Person who started the conversation

        """
        logger = logging.getLogger(__name__)
        try:
            logger.info("DataBase::insert_new_conversation: Inserting new data")

            conversation = {
                'conversation_id': conversation_id,
                'user': user,
                'messages': [{'message': message, 'time': datetime.datetime.today()} for message in messages]
            }

            collection = self.database['conversation']
            collection.insert_one(conversation)
        except:
            logger.error("DataBase::insert_new_conversation: Error inserting new data", exc_info=True)

    def update_conversation(self, conversation_id : str , messages : str):
        """
        Used to update a array of messages inserting a new one in the collection conversation.

        Params:
            - conversation_id: The id of the conversation. (Used as Primary Key)
            - messages: New messages to update the array of messages.

        """
        logger = logging.getLogger(__name__)

        try:
            logger.info(f"DataBase::update_conversation: Updating convesations {conversation_id}")
            collection = self.database['conversation']

            if self.check_conversation(conversation_id):
                [collection.update({'conversation_id': conversation_id}, {'$push': {'messages': {'message': message, 'time': datetime.datetime.today()}}}) for message in messages]
        except:
            logger.error(f"DataBase::update_conversation: Error Updating convesations {conversation_id}", exc_info=True)          

    def insert_video_base64(self, base_64 : str , user : str):
        """
        Insert a video encoded in base 64 in the legola's database.

        Params:
            - user: the user who logged in the application.
            - base_64: a video encoded in base 64.
        """
        logger = logging.getLogger(__name__)

        try:
            logger.info("DataBase::insert_video_base64: Saving video")
            
            collection = self.database['video']

            video = {
                'video': base_64,
                'user': user
            } 

            collection.insert_one(video)
        except:
            logger.error("DataBase::insert_video_base64: Error saving video", exc_info=True)          

