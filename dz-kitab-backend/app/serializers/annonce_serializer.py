from rest_framework import serializers
from app.models.annonce import Annonce

class AnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annonce
        fields = '__all__'
