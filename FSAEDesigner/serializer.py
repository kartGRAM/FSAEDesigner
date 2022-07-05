from .models import GeometryDesignerFile
from rest_framework import serializers


class GeometryDesignerFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeometryDesignerFile
        fields = ('name', 'user', 'is_public', 'thumbnail', 'content')
        read_only_fields = ('username',)
        extra_kwargs = {
            'password': {'write_only': True},
        }
