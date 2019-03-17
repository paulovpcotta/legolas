from pymongo import MongoClient
import datetime

class DataBase():
    def __init__(self):
        URI_LOCAL = "mongodb://localhost:27017"
        self.client = MongoClient(URI_LOCAL) 
        self.database = self.client.chat_legolas

    def close_connection(self):
        self.client.close()

    def check_conversation(self, conversation_id):
        collection = self.database['conversation']
        find = collection.find_one({'conversation_id': conversation_id})
        if find:
            return True
        else:
            return False

    def insert_new_conversation(self, conversation_id, user, messages):

        conversation = {
            'conversation_id': conversation_id,
            'user': user,
            'messages': [{'message': message, 'time': datetime.datetime.today()} for message in messages]
        }

        collection = self.database['conversation']
        collection.insert_one(conversation)

    def update_conversation(self, conversation_id, messages):
        collection = self.database['conversation']

        [collection.update({'conversation_id': conversation_id}, {'$push': {'messages': {'message': message, 'time': datetime.datetime.today()}}}) for message in messages]