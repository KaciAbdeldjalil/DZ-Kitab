from django.urls import path
from .views import AnnouncementAdvancedSearchView

urlpatterns = [
    path('announcements/search/', AnnouncementAdvancedSearchView.as_view(), name='announcement-advanced-search'),
]
