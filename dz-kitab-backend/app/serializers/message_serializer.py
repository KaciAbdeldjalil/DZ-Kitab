# app/serializers/message_serializer.py
from rest_framework import serializers
from app.models.message import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['IdM', 'sender', 'receiver', 'annonce', 'contenu', 'etat', 'reponses']
