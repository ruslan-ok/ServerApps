from django.db import models
from rest_framework import serializers
from task.models import Group, Task

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    app = serializers.ReadOnlyField()
    class Meta:
        model = Group
        fields = ['url', 'id', 'user', 'app', 'node', 'name', 'sort', 'is_open', 'is_leaf']

class GroupSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'node', 'app', 'name', 'is_open']
    
class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Task
        fields = ['url', 'user', 'created', 'name', 'start', 'completed', 'completion', 'in_my_day', 'important', 'remind', 
                  'repeat', 'repeat_num', 'repeat_days', 'categories', 'info',
                  'app_task', 'app_note', 'app_news', 'app_store', 'app_doc', 'app_warr', 'app_expen', 
                  'app_trip', 'app_fuel', 'app_apart', 'app_health', 'app_work', 'app_photo']

