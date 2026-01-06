from rest_framework import viewsets
from app.models.annonce import Annonce
from app.serializers.annonce_serializer import AnnonceSerializer

class AnnonceViewSet(viewsets.ModelViewSet):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
