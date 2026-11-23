from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from .models import StudentGroup


class RecordView(LoginRequiredMixin, PermissionRequiredMixin):
    section = ''
    action = ''
    heading = ''
    template_name = 'record_form.html'

    def get_permission_required(self):
        return (f'cards.{self.action}_{self.model._meta.model_name}',)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            heading=self.heading, section=self.section,
            cancel_url=self.get_success_url(), **kwargs,
        )

    def get_success_url(self):
        return reverse(self.section)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ma’lumot o‘chirildi.' if self.action == 'delete' else 'Ma’lumot saqlandi.')
        return response


class RecordCreate(RecordView, CreateView):
    action = 'add'


class RecordUpdate(RecordView, UpdateView):
    action = 'change'


class GroupStudentCreate(RecordCreate):
    def get_form(self, form_class=None):
        group = get_object_or_404(StudentGroup, pk=self.kwargs['group_id'])
        form = super().get_form(form_class)
        form.initial['group'] = group.pk
        form.fields['group'].disabled = True
        return form

    def get_success_url(self):
        return reverse('group_detail', args=[self.kwargs['group_id']])


class RecordDelete(RecordView, DeleteView):
    action = 'delete'
    template_name = 'record_delete.html'
