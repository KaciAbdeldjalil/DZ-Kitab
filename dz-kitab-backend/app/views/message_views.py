# app/views/message_views.py
from rest_framework import viewsets
from app.models.message import Message
from app.serializers.message_serializer import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
