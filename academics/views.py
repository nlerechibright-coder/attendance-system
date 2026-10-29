from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView
from accounts.views import admin_required
from .forms import FacultyForm, DepartmentForm, CourseForm, EnrollmentForm
from .models import Faculty, Department, Course, StudentCourseEnrollment


@method_decorator(admin_required, name='dispatch')
class FacultyListView(ListView):
    model = Faculty
    template_name = 'academics/faculty_list.html'
    context_object_name = 'faculties'
    paginate_by = 10
    def get_queryset(self):
        qs = Faculty.objects.all().order_by('name')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs


@method_decorator(admin_required, name='dispatch')
class FacultyCreateView(CreateView):
    model = Faculty
    form_class = FacultyForm
    template_name = 'academics/faculty_form.html'
    success_url = reverse_lazy('faculty_list')
    def form_valid(self, form):
        messages.success(self.request, f'Faculty "{form.instance.name}" created.')
        return super().form_valid(form)


@method_decorator(admin_required, name='dispatch')
class FacultyUpdateView(UpdateView):
    model = Faculty
    form_class = FacultyForm
    template_name = 'academics/faculty_form.html'
    success_url = reverse_lazy('faculty_list')
    def form_valid(self, form):
        messages.success(self.request, f'Faculty "{form.instance.name}" updated.')
        return super().form_valid(form)


@method_decorator(admin_required, name='dispatch')
class DepartmentListView(ListView):
    model = Department
    template_name = 'academics/department_list.html'
    context_object_name = 'departments'
    paginate_by = 10
    def get_queryset(self):
        qs = Department.objects.select_related('faculty').all().order_by('name')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs


@method_decorator(admin_required, name='dispatch')
class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'academics/department_form.html'
    success_url = reverse_lazy('department_list')
    def form_valid(self, form):
        messages.success(self.request, f'Department "{form.instance.name}" created.')
        return super().form_valid(form)


@method_decorator(admin_required, name='dispatch')
class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'academics/department_form.html'
    success_url = reverse_lazy('department_list')
    def form_valid(self, form):
        messages.success(self.request, f'Department "{form.instance.name}" updated.')
        return super().form_valid(form)


@method_decorator(admin_required, name='dispatch')
class CourseListView(ListView):
    model = Course
    template_name = 'academics/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    def get_queryset(self):
        qs = Course.objects.select_related('department', 'department__faculty', 'assigned_lecturer__user').order_by('course_code')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(course_code__icontains=q) | Q(title__icontains=q))
        return qs


@method_decorator(admin_required, name='dispatch')
class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'academics/course_form.html'
    success_url = reverse_lazy('course_list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            form.add_error('course_code', 'A course with this code already exists.')
            return self.form_invalid(form)
        messages.success(self.request, f'Course "{self.object.course_code}" created.')
        return redirect(self.get_success_url())


@method_decorator(admin_required, name='dispatch')
class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'academics/course_form.html'
    success_url = reverse_lazy('course_list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            form.add_error('course_code', 'A course with this code already exists.')
            return self.form_invalid(form)
        messages.success(self.request, f'Course "{self.object.course_code}" updated.')
        return redirect(self.get_success_url())


@method_decorator(admin_required, name='dispatch')
class EnrollmentListView(ListView):
    model = StudentCourseEnrollment
    template_name = 'academics/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 12
    def get_queryset(self):
        qs = StudentCourseEnrollment.objects.select_related('student__user', 'course').order_by('-enrolled_date')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(student__registration_number__icontains=q) | Q(course__course_code__icontains=q))
        return qs


@method_decorator(admin_required, name='dispatch')
class EnrollmentCreateView(CreateView):
    model = StudentCourseEnrollment
    form_class = EnrollmentForm
    template_name = 'academics/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            form.add_error(None, 'This student is already enrolled in the selected course.')
            return self.form_invalid(form)
        messages.success(self.request, 'Student enrolled successfully.')
        return redirect(self.get_success_url())
