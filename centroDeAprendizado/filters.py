from django_filters import rest_framework as filters
from .models import LearningRecord

class LearningRecordsFilters(filters.FilterSet):
    title = filters.CharFilter(        
        field_name='title',
        lookup_expr='icontains',
        label='Title:'
    )
    category = filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',
        label='Category:'
    )
    collaborator = filters.CharFilter(
        field_name='created_by__name',
        lookup_expr='icontains',
        label='Collaborator:'
    )

    class Meta:
        model = LearningRecord
        fields = ['title', 'category', 'collaborator']