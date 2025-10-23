from django.urls import path
from .views import (
    LoginUserView,
    UserCollaboratorListView,
    UserCollaboratorDetailView,
    SendCodeView,
    ValidateCodeView,
    ChangeForgotPasswordView,
    LearningRecordListView,
    LearningRecordDetailView,
    HomeView
)


urlpatterns = [
    path('login/', LoginUserView.as_view(), name='login'),
    path('users/collaborators/', UserCollaboratorListView.as_view(), name='list-users'),
    path('users/collaborators/<int:id>/', UserCollaboratorDetailView.as_view(), name='detail-users'),
    path('forgot-password/', SendCodeView.as_view(), name='forgot-password'),
    path('validate-code/', ValidateCodeView.as_view(), name='validate-code'),
    path('change-password/', ChangeForgotPasswordView.as_view(), name='change-password'),
    path('learning-records/', LearningRecordListView.as_view(), name='learning-record-list'),
    path('learning-records/<int:id>/', LearningRecordDetailView.as_view(), name='learning-record-detail'),
    path('home/', HomeView.as_view(), name='home')
]