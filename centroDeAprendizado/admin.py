from django.contrib import admin
from .models import User, Collaborator, Category, LearningRecord, LearningType


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'role', 'user')
    list_filter = ('department', 'role')
    search_fields = ('name', 'user__username', 'department')
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(LearningRecord)
class LearningRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'learning_type', 'created_at', 'created_by', 'category', 'reading_duration')
    list_filter = ('learning_type', 'category', 'created_at')
    search_fields = ('title', 'summary', 'created_by__name', 'category__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'