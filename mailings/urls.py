from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipientViewSet, MessageViewSet, MailingViewSet, MailAttemptViewSet

router = DefaultRouter()
router.register(r"recipients", RecipientViewSet, basename="recipient")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r"mailings", MailingViewSet, basename="mailing")
router.register(r"attempts", MailAttemptViewSet, basename="attempt")

urlpatterns = [
    path("api/", include(router.urls)),
]
