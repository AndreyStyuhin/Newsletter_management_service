from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .models import Recipient, Message, Mailing, MailAttempt
from .serializers import RecipientSerializer, MessageSerializer, MailingSerializer, MailAttemptSerializer
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from .forms import RecipientForm, MessageForm, MailingForm

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

# Web views

class BaseOwnedMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

# Messages
class MessageListView(BaseOwnedMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'

class MessageDetailView(BaseOwnedMixin, DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('messages_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MessageUpdateView(BaseOwnedMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('messages_list')

class MessageDeleteView(BaseOwnedMixin, DeleteView):
    model = Message
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('messages_list')

# Recipients
class RecipientListView(BaseOwnedMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'

class RecipientDetailView(BaseOwnedMixin, DetailView):
    model = Recipient
    template_name = 'mailings/recipient_detail.html'

class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipients_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class RecipientUpdateView(BaseOwnedMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipients_list')

class RecipientDeleteView(BaseOwnedMixin, DeleteView):
    model = Recipient
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('recipients_list')

# Mailings
class MailingListView(BaseOwnedMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'

class MailingDetailView(BaseOwnedMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.all()
        return context

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        recipients = mailing.recipients.all()
        message = mailing.message
        for recipient in recipients:
            try:
                send_mail(
                    message.subject,
                    message.body,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient.email],
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
        if mailing.end_at < timezone.now():
            mailing.status = "FINISHED"
        else:
            mailing.status = "RUNNING"
        mailing.save()
        return HttpResponseRedirect(reverse('mailing_detail', args=(mailing.pk,)))

class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MailingUpdateView(BaseOwnedMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form

class MailingDeleteView(BaseOwnedMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('mailings_list')

# Attempts (read-only)
class MailAttemptListView(LoginRequiredMixin, ListView):
    model = MailAttempt
    template_name = 'mailings/attempt_list.html'

    def get_queryset(self):
        return MailAttempt.objects.filter(owner=self.request.user)