from rest_framework import serializers
from app.models.annonce import Annonce

class AnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annonce
        fields = ['id', 'isbn', 'title', 'author', 'price', 'created_at', 'image']
        read_only_fields = ['id', 'created_at']
