from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .models import Recipient, Message, Mailing, MailAttempt
from .serializers import RecipientSerializer, MessageSerializer, MailingSerializer, MailAttemptSerializer


class RecipientViewSet(viewsets.ModelViewSet):
    serializer_class = RecipientSerializer
    queryset = Recipient.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MailingViewSet(viewsets.ModelViewSet):
    serializer_class = MailingSerializer
    queryset = Mailing.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        mailing = self.get_object()
        recipients = mailing.recipients.all()
        message = mailing.message

        for recipient in recipients:
            try:
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email = settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                MailAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status="SUCCESS",
                    response="OK",
                    owner=request.user,
                )
            except Exception as e:
                MailAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status="FAILED",
                    response=str(e),
                    owner=request.user,
                )

        if mailing.status == "CREATED":
            mailing.status = "RUNNING"
        if mailing.end_at and mailing.end_at < timezone.now():
            mailing.status = "FINISHED"
        mailing.save()

        return Response({"status": "Рассылка выполнена"}, status=status.HTTP_200_OK)


class MailAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MailAttemptSerializer
    queryset = MailAttempt.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return MailAttempt.objects.all()
        return MailAttempt.objects.filter(owner=self.request.user)
