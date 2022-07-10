from .models import GeometryDesignerFile
from rest_framework import serializers


class GeometryDesignerFileSerializer(serializers.ModelSerializer):
    overwrite = serializers.BooleanField(required=True, write_only=True)
    clientLastUpdated = serializers.DateTimeField(required=True, write_only=True)

    class Meta:
        model = GeometryDesignerFile
        fields = ('id','name','note', 'user', 'is_public','thumbnail',
         'content',  "lastUpdated","created", "overwrite", "clientLastUpdated")
        read_only_fields = ('created',)
        extra_kwargs = {
            'overwrite': {'write_only': True},
            'clientLastUpdated': {'write_only': True},
        }

    def create(self, validated_data):
        del validated_data["overwrite"], validated_data["clientLastUpdated"]
        return super().create(validated_data)
