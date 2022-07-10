from django.shortcuts import render
from django.http import request
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializer import GeometryDesignerFileSerializer as gdFileSerializer
from .models import GeometryDesignerFile as gdFile
from django.utils import timezone

@api_view(['POST'])
def checkLoggedIn(request, format=None):
    content = {
        'status': 'ok'
    }
    return Response(content)

@api_view(['POST'])
def gdSaveAs(request, format=None):
    if request.method == "POST" and "name" in request.data:
        data = request.data
        data["user"] = request.user.id
        data["lastUpdated"] = timezone.now()
        serializer = gdFileSerializer(data=data)
        if serializer.is_valid():
            data = serializer.validated_data
            duplicated = list(gdFile.objects.filter(
                user=request.user, name=data["name"]
                ))
            if len(duplicated) > 0:
                if not data["overwrite"]:
                    return Response(
                        {"error": "File already exists."}
                        , status=status.HTTP_409_CONFLICT)

                duplicated = duplicated[0]
                data = {k:v for k, v in data.items()}
                del data['user']
                serializer = gdFileSerializer(instance=duplicated,
                  data=data,
                  partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def gdGetAllUserFiles(request, format=None):
    user = request.user
    if request.method == "GET":
        files = gdFile.objects.filter(user=user)
        serializer = gdFileSerializer(files, many=True)
        return Response(serializer.data)
