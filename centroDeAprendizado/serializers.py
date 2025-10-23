from rest_framework import serializers
from .models import User, Collaborator, LearningRecord, Videos, Category
from django.contrib.auth.hashers import make_password
from .utils.autenticacaosevice import validatePassword
from django.db import transaction
from .utils.learninginsightsservice import totalLearningRecords, totalLearningRecordsLastMonth, activesCollaborators, learningHours

class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'is_superuser', 'is_staff']

class CadastrarUserCollaboratorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    department = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_superuser', 'name', 'department', 'role']
    
    def create(self, validated_data):
        name = validated_data.pop('name')
        department = validated_data.pop('department')
        role = validated_data.pop('role')
        password = validated_data.pop('password')

        user = User.objects.create(
            **validated_data,
            password=make_password(password)
        )

        Collaborator.objects.create(
            user=user,
            name=name,
            department=department,
            role=role
        )

        return user
    
    def validate(self, attrs):
        password = attrs['password']

        if not validatePassword(password):
             raise serializers.ValidationError({"detail": "A senha deve ter no mínimo 6 caracteres, um número, uma letra maiúscula e um caracter especial"})
        
        return attrs
    

class ListUserCollaboratorSerializer(serializers.ModelSerializer):
    collaborator = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_superuser', 'collaborator']

    def get_collaborator(self, obj):
        if hasattr(obj, 'collaborator'):
            return {
                'name': obj.collaborator.name,
                'department': obj.collaborator.department,
                'role': obj.collaborator.role
            }
        return None
    
class SendCodeSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    
class ValidateUserCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

class ChangeForgotPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    repeat_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        repeat_new_password = attrs.get('repeat_new_password')

        if new_password != repeat_new_password:
            raise serializers.ValidationError({'detail': 'As senhas devem estar iguais'})
        
        validated_new_password = validatePassword(new_password)

        if not validated_new_password:
             raise serializers.ValidationError({"detail": "A senha deve ter no mínimo 6 caracteres, um número, uma letra maiúscula e um caracter especial"})
    
        return attrs

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = ['id', 'url']
        read_only_fields = ['id']

class LearningRecordSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True
    )
    videos = VideoSerializer(many=True, required=False)
    
    class Meta:
        model = LearningRecord
        fields = [
            'id',
            'title',
            'learning_type',
            'created_at',
            'reading_duration',
            'summary',
            'created_by',
            'category',      
            'category_name', 
            'videos'
        ]

    def create(self, validated_data):
        videos_data = validated_data.pop('videos', [])
        user = self.context['request'].user
        validated_data['created_by'] = user.collaborator

        with transaction.atomic():
            learning_record = LearningRecord.objects.create(**validated_data)
            for video_data in videos_data:
                Videos.objects.create(learning_record=learning_record, **video_data)
        
        return learning_record

    def update(self, instance, validated_data):
        videos_data = validated_data.pop('videos', [])

        with transaction.atomic():
            
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

           
            existing_videos = {video.id: video for video in instance.videos.all()}
            for video_data in videos_data:
                video_id = video_data.get('id', None)
                if video_id and video_id in existing_videos:
                    video = existing_videos.pop(video_id)
                    for attr, value in video_data.items():
                        setattr(video, attr, value)
                    video.save()
                else:
                    Videos.objects.create(learning_record=instance, **video_data)

            
            for video in existing_videos.values():
                video.delete()

        return instance
    
class InsightsSerializer(serializers.Serializer):
    total_learning = serializers.SerializerMethodField()
    active_collaborators = serializers.SerializerMethodField()
    total_hours_learning = serializers.SerializerMethodField()
    total_learning_last_month = serializers.SerializerMethodField()

    def get_total_learning(self, obj):
        return totalLearningRecords()

    def get_total_hours_learning(self, obj):
        return learningHours()
    
    def get_active_collaborators(self, obj):
        return activesCollaborators()
    
    def get_total_learning_last_month(self, obj):
        return totalLearningRecordsLastMonth()


class HomeSerializer(serializers.Serializer):
    insights = InsightsSerializer()
    learning_records = LearningRecordSerializer(many=True)

    def to_representation(self, instance):
        home = super().to_representation(instance)
        user = self.context['request'].user
        if not user.is_staff:
            home.pop('insights', None)
        return home
   


