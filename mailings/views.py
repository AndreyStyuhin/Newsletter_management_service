from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .models import Recipient, Message, Mailing, MailAttempt
from .serializers import RecipientSerializer, MessageSerializer, MailingSerializer, MailAttemptSerializer
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from .forms import RecipientForm, MessageForm, MailingForm
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

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
                    from_email=settings.DEFAULT_FROM_EMAIL,
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
        if self.request.user.groups.filter(name='Менеджеры').exists() or self.request.user.is_staff:
            return self.model.objects.all()
        return self.model.objects.filter(owner=self.request.user)

# Messages
class MessageListView(BaseOwnedMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class MessageDetailView(PermissionRequiredMixin, BaseOwnedMixin, DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'
    permission_required = 'mailings.can_view_message'

class MessageCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('messages_list')
    permission_required = 'mailings.can_add_message'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MessageUpdateView(PermissionRequiredMixin, BaseOwnedMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('messages_list')
    permission_required = 'mailings.can_change_message'

class MessageDeleteView(PermissionRequiredMixin, BaseOwnedMixin, DeleteView):
    model = Message
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('messages_list')
    permission_required = 'mailings.can_delete_message'

# Recipients
class RecipientListView(BaseOwnedMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class RecipientDetailView(PermissionRequiredMixin, BaseOwnedMixin, DetailView):
    model = Recipient
    template_name = 'mailings/recipient_detail.html'
    permission_required = 'mailings.can_view_recipient'

class RecipientCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipients_list')
    permission_required = 'mailings.can_add_recipient'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class RecipientUpdateView(PermissionRequiredMixin, BaseOwnedMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipients_list')
    permission_required = 'mailings.can_change_recipient'

class RecipientDeleteView(PermissionRequiredMixin, BaseOwnedMixin, DeleteView):
    model = Recipient
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('recipients_list')
    permission_required = 'mailings.can_delete_recipient'

# Mailings
class MailingListView(BaseOwnedMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class MailingDetailView(PermissionRequiredMixin, BaseOwnedMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    permission_required = 'mailings.can_view_mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.all()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('mailings.can_send_mailing'):
            return HttpResponseRedirect(reverse('mailing_detail', args=(self.object.pk,)))
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

class MailingCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings_list')
    permission_required = 'mailings.can_add_mailing'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MailingUpdateView(PermissionRequiredMixin, BaseOwnedMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings_list')
    permission_required = 'mailings.can_change_mailing'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form

class MailingDeleteView(PermissionRequiredMixin, BaseOwnedMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('mailings_list')
    permission_required = 'mailings.can_delete_mailing'

# Attempts
class MailAttemptListView(LoginRequiredMixin, ListView):
    model = MailAttempt
    template_name = 'mailings/attempt_list.html'

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists() or self.request.user.is_staff:
            return MailAttempt.objects.all()
        return MailAttempt.objects.filter(owner=self.request.user)