
from centroDeAprendizado.models import Collaborator, LearningRecord
from django.db.models import Sum
from datetime import timedelta, datetime

def activesCollaborators():
    return Collaborator.objects.filter(user__is_active=True).count()

def learningHours():
    duration = LearningRecord.objects.aggregate(total=Sum('reading_duration'))
    total_duration = duration['total'] or timedelta()  
    total_hours = total_duration.total_seconds() / 3600
    return round(total_hours)

def totalLearningRecords():
    total = LearningRecord.objects.all().count()
    return total

def totalLearningRecordsLastMonth():
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    return LearningRecord.objects.filter(created_at__gte=one_month_ago).count()


