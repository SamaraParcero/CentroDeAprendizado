from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinLengthValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6)], blank=True, null=True)
    auth_code_created_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  

    objects = UserManager()  
    def __str__(self):
        return self.email


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
    

