from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Collaborator, LearningRecord
from django.contrib.auth import authenticate
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserLoginSerializer, CadastrarUserCollaboratorSerializer, ListUserCollaboratorSerializer, ValidateUserCodeSerializer, SendCodeSerializer, ChangeForgotPasswordSerializer, LearningRecordSerializer, HomeSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .utils.emailservice import generateCode, sendEmail
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from .utils.autenticacaosevice import generateForgotPasswordToken, validateForgotPasswordToken
from django_filters.rest_framework import DjangoFilterBackend
from .filters import LearningRecordsFilters
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import LimitOffsetPagination

class LoginUserView(APIView):
    permission_classes = []
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'detail':'username ou senha não informados'},status = status.HTTP)
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail':'Username ou senha incorreto'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({'detail':'Usuário inativo'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_authenticated = authenticate(request, username=username, password=password)

        if not user_authenticated:
            return Response({'detail':'Username ou senha incorretos'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = RefreshToken.for_user(user)
        serializer =  UserLoginSerializer(user)

        login(request, user_authenticated)
        return Response({
            'usuario': serializer.data,
            'refresh': str(token),
            'access': str(token.access_token),
        }, status=status.HTTP_200_OK)



class SendCodeView(APIView):
    permission_classes= []

    def post(self, request):
        serializer = SendCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')

        if not email:
            return Response({'detail': 'Email não informado'})
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'E-mail não cadastrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        min_seconds = 180
        if user.auth_code_created_at and (timezone.now() - user.auth_code_created_at) < timedelta(seconds=min_seconds):
            return Response({'detail': 'Agurde o tempo necessário para fazer o próximo envio do código.'}, status=status.HTTP_400_BAD_REQUEST)
        
        code = generateCode()
        user = User.objects.get(email=email)
        user.code = code
        user.auth_code_created_at = timezone.now()
        user.save()

        try:
            colaborador = Collaborator.objects.get(user=user)
        except Collaborator.DoesNotExist:
            return Response({'detail': 'Colaborador não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
       
        sendEmail(code, email, colaborador.name )

        return Response({'detail': 'Código de verificação enviado com sucesso.'}, status=status.HTTP_200_OK)


class ValidateCodeView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ValidateUserCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        code = serializer.validated_data.get('code')

        if not email or not code:
            return Response({'detail': 'E-mail e código são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'E-mail não cadastrado.'}, status=status.HTTP_404_NOT_FOUND)

        if user.code != code:
            return Response({'detail': 'Código incorreto.'}, status=status.HTTP_400_BAD_REQUEST)


        expiration_time = timedelta(minutes=10)
        if user.auth_code_created_at and timezone.now() - user.auth_code_created_at > expiration_time:
            return Response({'detail': 'Código expirado.'}, status=status.HTTP_400_BAD_REQUEST)

    
        user.code = None
        user.auth_code_created_at = None
        user.save()
        token = generateForgotPasswordToken(user)

        return Response({"detail": "Código verificado com sucesso.", "token": token}, status=status.HTTP_200_OK)


class ChangeForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ChangeForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = request.data.get("token")  
        if not token:
            return Response({"detail": "Token obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = validateForgotPasswordToken(token)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        new_password = serializer.validated_data['new_password']
        user.password = make_password(new_password)
        user.save()

        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)


class UserCollaboratorListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CadastrarUserCollaboratorSerializer   
        return ListUserCollaboratorSerializer


class UserCollaboratorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH', 'POST']:
            return CadastrarUserCollaboratorSerializer
        return ListUserCollaboratorSerializer


class LearningRecordListView(generics.ListCreateAPIView):
    queryset = LearningRecord.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LearningRecordSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LearningRecordsFilters


class LearningRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningRecord.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LearningRecordSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Você não tem permissão para deletar este registro."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.created_by.user != user and not user.is_staff:
            return Response(
                {"detail": "Você não tem permissão para atualizar este registro."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    
class HomeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeSerializer

    def get(self, request):
        learning_records = LearningRecord.objects.all().order_by('-created_at')
        paginated = self.paginate_queryset(learning_records)

        instance = {
            "insights": {},  
            "learning_records": paginated
        }

        serializer = self.get_serializer(instance, context={'request': request})
        data = serializer.data

        paginated_response = self.get_paginated_response(serializer.data["learning_records"]).data

        response = {
            "learning_records_pagination": {
                "count": paginated_response["count"],
                "next": paginated_response["next"],
                "previous": paginated_response["previous"]
            },
            "insights": data.get("insights", {}),
            "learning_records": paginated_response["results"]
        }

        return Response(response)

