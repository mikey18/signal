import jwt
import os
from django.http import JsonResponse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv


load_dotenv()

ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def auth_decoder(token, action):
    try:
        payload = jwt.decode(
            token,
            key=REFRESH_SECRET_KEY if action == "refresh" else ACCESS_SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def access_refresh_token(user, action):
    payload = {
        "id": user.id,
        "type": action,
        "exp": datetime.now(timezone.utc)
        + (timedelta(days=365) if action == "refresh" else timedelta(minutes=5)),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(
        payload,
        key=REFRESH_SECRET_KEY if action == "refresh" else ACCESS_SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return token


def jwt_required(token_type):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if token_type == "refresh" and request.data["platform"] == "web":
                token = request.COOKIES.get("refresh")  # Extract token from cookie
            else:
                token = request.META.get("HTTP_AUTHORIZATION")


            if not token:
                return JsonResponse({"msg": "Invalid auth"}, status=403)

            payload = auth_decoder(token, token_type)
            if payload is None:
                return JsonResponse({"msg": "Invalid auth"}, status=403)
            if payload["type"] != token_type:
                return JsonResponse({"msg": "Invalid auth"}, status=403)

            request.user_id = payload["id"]
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def jwt_required_ws(token, token_type):
    if not token:
        return None

    payload = auth_decoder(token, token_type)
    if payload is None:
        return None
    if payload["type"] != token_type:
        return None

    return payload


def get_tokens(user):
    return {
        "access": access_refresh_token(user, "access"),
        "refresh": access_refresh_token(user, "refresh"),
    }
