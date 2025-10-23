import re
import jwt
from datetime import datetime, timezone, timedelta
from django.conf import settings
from rest_framework import serializers

def validatePassword(password):  
        if len(password) < 6:
            return False
        if not re.search(r'[A-Z]', password):  
            return False
        if not re.search(r'[a-z]', password):  
            return False
        if not re.search(r'[0-9]', password):  
            return False
        if not re.search(r'[@#$%^&+=!]', password):  
            return False
        return True

def generateForgotPasswordToken(user):
    exp = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload = {"user_id":user.id, "email": user.email, "exp": exp}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    return token

def validateForgotPasswordToken(token:str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("email")
    except jwt.ExpiredSignatureError:
        raise serializers.ValidationError("Token expirado.")
    except jwt.InvalidTokenError:
        raise serializers.ValidationError("Token inválido.")
     
     