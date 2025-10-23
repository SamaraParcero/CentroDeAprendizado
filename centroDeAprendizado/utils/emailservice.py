from django.core.mail import send_mail
from decouple import config
import random

def sendEmail(code, email, name):
        codigomail=f"""
        Olá, {name}!

        Recebemos uma solicitação para verificar sua identidade.
        Seu código de verificação é:

        {code}

        Este código é válido por 10 minutos.
        Se você não solicitou este código, ignore esta mensagem

        Atenciosamente,
        Corporação SaMUel 
        """
        send_mail(
        subject='Código de Autenticação - Coorporação SaMUel',
        message=codigomail,
        from_email=config('DEFAULT_FROM_EMAIL'),
        recipient_list=[email],
        fail_silently=False,
        )

def generateCode():
         return str(random.randint(100000, 999999)) 


