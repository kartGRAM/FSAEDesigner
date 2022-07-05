from django.shortcuts import render
from django.http import request
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from serializer import GeometryDesignerFileSerializer as gdFileSerializer

@api_view(['POST'])
def checkLoggedIn(request, format=None):
    content = {
        'status': 'ok'
    }
    return Response(content)

@api_view(['POST'])
def gdSaveAs(request, format=None):
    if request.method == "POST":
        serializer = gdFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
