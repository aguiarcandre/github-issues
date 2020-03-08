import os
from google.cloud import firestore

def get_document(doc):
    try:
        doc = db.collection("parameters").document(doc).get()
        return doc.to_dict()
    except Exception as e:
        print(e)

def update_document(doc, data):
    try:
        db.collection("parameters").document(doc).update(data)
    except Exception as e:
        print(e)

# Auth
db = firestore.Client()
