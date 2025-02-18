from email import message
from io import StringIO
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import (
    TemplateView,
    CreateView,
    RedirectView,
    UpdateView,
    ListView,
    DetailView
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django_weasyprint import WeasyTemplateResponseMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

import csv

from .forms import (
    CSVUploadForm, StudentSignUpForm, UserUpdateForm, TeacherUpdateForm)
from .models import Result, User, WebsiteSettings, DepartmentType
from ..thesis.models import Batch
from website.thesis.mixins import UserIsSuperuserMixin


class LoginRedirectView(LoginRequiredMixin, RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if user.is_teacher:
            if user.is_external:
                return reverse_lazy('thesis:external_group_list')
            return reverse_lazy('thesis:group_list')
        elif user.is_superuser:
            return reverse_lazy('admin:index')
        elif user.studentgroup:
            return reverse_lazy('thesis:document_list')
        return reverse_lazy('registration:teacher_list')


class AboutView(TemplateView):
    http_method_names = ['get']
    template_name = 'registration/about.html'


class UserCreateView(CreateView):
    model = User
    template_name = 'registration/user_create.html'
    form_class = StudentSignUpForm
    success_url = reverse_lazy('registration:teacher_list')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = WebsiteSettings.objects.first()
        context["enable_registration"] = settings.enable_registration
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            'User Created Successfully!',
            extra_tags='is-success')
        return response


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'registration/user_update.html'
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('registration:user_update')

    def get_form_class(self):
        if self.request.user.is_teacher:
            return TeacherUpdateForm
        else:
            return UserUpdateForm

    def get_object(self, *args, **kwargs):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Update Successful!',
            extra_tags='is-success')
        return response


class UserDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/user_delete.html'
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        messages.success(
            request,
            'Account deleted successfully!',
            extra_tags='is-success')
        return HttpResponseRedirect(reverse_lazy('registration:login'))


class TeachersListView(LoginRequiredMixin, ListView):
    template_name = 'registration/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        department_name = self.kwargs.get('department_name', '')
        queryset = User.objects.filter(is_teacher=True).order_by('full_name')
        if department_name:
            return queryset.filter(department=department_name)
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context_data = super().get_context_data(*args, object_list=object_list, **kwargs)
        context_data['department_name'] = self.kwargs.get('department_name', '')
        context_data['department_types'] = DepartmentType.choices
        return context_data


class TeacherDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'teacher'
    template_name = 'registration/teacher_detail.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            User, username=self.kwargs['username'])
        return obj


class StudentDetailView(TeacherDetailView):
    context_object_name = 'student'
    template_name = 'registration/student_detail.html'


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request,
                'Your password was successfully updated!',
                extra_tags='is-success')
            return redirect(reverse_lazy('registration:change_password'))
        else:
            messages.error(
                request,
                'Please correct the error below.',
                extra_tags='is-danger')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})


class ReportPDFView(
    LoginRequiredMixin,
    WeasyTemplateResponseMixin,
    ListView):
    context_object_name = 'results'
    pdf_attachment = False
    template_name = 'registration/result-report-pdf.html'

    def get_queryset(self):
        department = self.kwargs['department']
        batch_id = self.kwargs['batch_id']
        return Result.objects.annotate(marks_count=Count('marks')).filter(
            marks_count=3,
            student__department=department,
            student__studentgroup__batch__id=batch_id,
        ).order_by('student__username')

    def get_batch(self):
        return get_object_or_404(Batch, pk=self.kwargs['batch_id'])

    def get_pdf_filename(self):
        department = self.kwargs['department']
        batch = self.get_batch()
        return f'{department}-{batch.number}.pdf'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department'] = self.kwargs['department']
        context['batch'] = self.get_batch()
        return context


class StudentCSVUploadView(LoginRequiredMixin, UserIsSuperuserMixin, FormView):
    http_method_names = ['post', 'head', 'options']
    form_class = CSVUploadForm
    success_url = '/admin/registration/student/'
    template_name = 'registration/about.html'

    def form_valid(self, form):
        csv_file = form.files.get('csv_file')
        self.process_csv_file(StringIO(csv_file.read().decode('utf-8')))
        return super().form_valid(form)

    def process_csv_file(self, file):
        reader = csv.DictReader(file, delimiter=",")
        successful = []
        errored = []
        for row in reader:
            created, username = self.create_student_for_row(row)
            if created:
                successful.append(username)
            else:
                errored.append(username)
        self.show_message(successful, 'success')
        self.show_message(errored, 'error')

    def show_message(self, usernames, message_type):
        count = len(usernames)
        joined_usernames = ', '.join(usernames)
        if count > 0:
            if message_type == 'success':
                messages.success(self.request, f'Created {count} students successfully. {joined_usernames}')
            elif message_type == 'error':
                messages.error(self.request, f'Could not create {count} students. {joined_usernames}')

    def create_student_for_row(self, row):
        username = row.get('id')
        if User.objects.filter(username=username).exists():
            return (False, username)
        student = User.objects.create(
            username=row.get('id'),
            department=row.get('department'),
            full_name=row.get('full_name'),
            email=row.get('email'),
            phone_number=row.get('phone_number'),
            cgpa=row.get('cgpa'),
            is_student=True,
        )
        student.set_password(row.get('email'))
        return (True, username)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid CSV File')
        return redirect(self.success_url)
