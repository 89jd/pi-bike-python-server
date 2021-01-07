import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import messaging
import uuid

from utils import print_debug

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

    def push_heartrate_request(self, start: bool) -> None:
        # The topic name can be optionally prefixed with "/topics/".
        topic = f"exercise"

        # See documentation on defining a message payload.
        message = messaging.Message(
            data={'started': str(start)},
            topic=topic,
        )

        print_debug(message)
        # Send a message to the devices subscribed to the provided topic.
        response = messaging.send(message)
        print_debug(response)

if __name__ == "__main__":
    Firebase().push_heartrate_request(True)