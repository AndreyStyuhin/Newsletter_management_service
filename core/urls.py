from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import HomeView, CustomLoginView, CustomLogoutView, CustomRegisterView, CustomProfileView
from mailings.views import (
    MessageListView, MessageDetailView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    RecipientListView, RecipientDetailView, RecipientCreateView, RecipientUpdateView, RecipientDeleteView,
    MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView,
    MailAttemptListView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("mailings.urls")),

    # Web paths
    path('', HomeView.as_view(), name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('profile/', CustomProfileView.as_view(), name='profile'),

    # Messages
    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    # Recipients
    path('recipients/', RecipientListView.as_view(), name='recipients_list'),
    path('recipients/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    # Mailings
    path('mailings/', MailingListView.as_view(), name='mailings_list'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),

    # Attempts
    path('attempts/', MailAttemptListView.as_view(), name='attempts_list'),
]