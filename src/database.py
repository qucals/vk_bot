import os
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore


class Database(object):
    def __init__(self):
        if not len(firebase_admin._apps):
            path = os.path.join('cfg', 'database_settings.json')
            self.__cred = credentials.Certificate(path)
            firebase_admin.initialize_app(self.__cred)
        else:
            firebase_admin.get_app()

        self.__db = firestore.client()
        self.__chats_ref = self.__db.collection('chats')

    def getChatsUid(self):
        """
        Returning UID's doucments in the collection.
        """

        uids = []
        for member in self.getChatsDocuments():
            uids.append(member.id)
        return uids

    def getChatsDocuments(self):
        """
        Returning the collection 'chats'.
        """

        return self.__db.collection('chats').stream()

    def getChatDocument(self, chat_uid):
        """
        Returning a document by UID.
        """

        try:
            return self.__db.collection('chats').document(chat_uid).get().to_dict()
        except Exception:
            return None

    def updateChatDocument(self, document_uid, data):
        """
        Update the data in a document in the collection 'Chats'.
        """

        if not type(document_uid) == str:
            document_uid = str(document_uid)

        if not type(data) == dict:
            data = dict(data)

        try:
            self.__chats_ref.document(document_uid).set(data)
        except Exception as err:
            print(err)
