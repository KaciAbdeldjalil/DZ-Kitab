from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from app.models import Announcement
from app.serializers import AnnouncementSerializer
from app.filters import AnnouncementAdvancedFilter
from app.pagination import AnnouncementSearchPagination
class AnnouncementAdvancedSearchView(ListAPIView):

    queryset = Announcement.objects.select_related('book').filter(status='Active')
    serializer_class = AnnouncementSerializer
    pagination_class = AnnouncementSearchPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AnnouncementAdvancedFilter

    ordering_fields = ['price', 'created_at', 'book__published_date']
    ordering = ['-created_at']
