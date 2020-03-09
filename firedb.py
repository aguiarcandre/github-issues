import os, tg
from google.cloud import firestore

def get_document(doc):
    try:
        doc = db.collection("parameters").document(doc).get()
        return doc.to_dict()
    except Exception as e:
        error = f"Error during 'firedb.get_document()' execution: {e}"
        tg.send_error_message(error)

def update_document(doc, data):
    try:
        db.collection("parameters").document(doc).update(data)
    except Exception as e:
        error = f"Error during 'firedb.update_document()' execution: {e}"
        tg.send_error_message(error)

# Auth
db = firestore.Client()
