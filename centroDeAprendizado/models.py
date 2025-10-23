from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6)], blank=True, null=True)
    auth_code_created_at = models.DateTimeField(null=True, blank=True)

class Collaborator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="collaborator")
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

class Category(models.Model):
    name = models.CharField(max_length=100)

class LearningType(models.TextChoices):
    COURSE = 'Course', 'Course'
    BOOK = 'Book', 'Book'
    ARTICLE = 'Article', 'Article'
    VIDEO = 'Video', 'Video'
    PODCAST = 'Podcast', 'Podcast'
    WORKSHOP = 'Workshop', 'Workshop'
    WEBINAR = 'Webinar', 'Webinar'

class LearningRecord(models.Model):
    title = models.CharField(max_length=100)
    learning_type = models.CharField(max_length=50, choices=LearningType.choices, default=LearningType.ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    reading_duration = models.DurationField()
    summary = models.TextField()
    created_by = models.ForeignKey(Collaborator, on_delete=models.CASCADE, related_name="learning_records")
    category = models.ForeignKey(Category,  on_delete=models.CASCADE, related_name="learning_records")

class Videos(models.Model):
    url = models.URLField()
    learning_record = models.ForeignKey(LearningRecord, on_delete=models.CASCADE, related_name="videos")
    

