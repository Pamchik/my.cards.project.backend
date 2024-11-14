from rest_framework import serializers

from .models import (
    NewChangeLogsModel
)


class NewChangeLogsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = NewChangeLogsModel
        fields = '__all__' 