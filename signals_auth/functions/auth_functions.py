import jwt
import os
from dotenv import load_dotenv

load_dotenv()

JWT_DECODE_KEY = os.getenv("JWT_DECODE_KEY")


def auth_encoder(payload):
    token = jwt.encode(payload, key=str(JWT_DECODE_KEY), algorithm="HS256")
    return token


def auth_decoder(token):
    payload = jwt.decode(token, key=JWT_DECODE_KEY, algorithms=["HS256"])
    return payload
