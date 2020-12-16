import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.storage.bucket import Bucket
import uuid

from config import properties

firebase_properties = getattr(properties, "firebase", None)

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred,)

class Firebase():
    def __init__(self) -> None:
        super().__init__()

    def write_workout(self, workout: dict) -> None:
        db = firestore.client()
        db.collection(firebase_properties.collection).document(str(uuid.uuid4())).set({firebase_properties.list_values_key: workout})
