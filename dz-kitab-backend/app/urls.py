from django.urls import path
from .views import AnnouncementAdvancedSearchView
from .views.message_views import SendMessageView, ConversationListView, AnnouncementMessagesView

urlpatterns = [
    path('announcements/search/', AnnouncementAdvancedSearchView.as_view(), name='announcement-advanced-search'),
]
from .views.message_views import SendMessageView, ConversationListView, AnnouncementMessagesView

urlpatterns += [
    path('messages/', SendMessageView.as_view(), name='send-message'),
    path('messages/conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('messages/<int:announcement_id>/', AnnouncementMessagesView.as_view(), name='announcement-messages'),
]

