import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Course, Enrollment, Question, Submission

logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html',
                      context)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("onlinecourse:index")
        context['message'] = "User with this username already exists."
        return render(request, 'onlinecourse/user_registration_bootstrap.html',
                      context)
    return render(request, 'onlinecourse/user_registration_bootstrap.html',
                  context)


def login_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_login_bootstrap.html',
                      context)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        context['message'] = "Invalid username or password."
        return render(request, 'onlinecourse/user_login_bootstrap.html',
                      context)
    return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect("onlinecourse:index")


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        num_results = Enrollment.objects.filter(
            user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


class CourseListView(generic.ListView):
    model = Course
    context_object_name = "course_list"
    template_name = "onlinecourse/course_list_bootstrap.html"


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = "onlinecourse/course_details_bootstrap.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_enrolled'] = check_if_enrolled(
            self.request.user, self.object)
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        enrollment = Enrollment.objects.get_or_create(
            user=user, course=course, mode=Enrollment.AUDIT)[0]
        enrollment.save()
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(
        reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    submission.save()
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id
    return HttpResponseRedirect(
        reverse(viewname='onlinecourse:exam_result',
                args=(course_id, submission_id)))


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()
    questions = Question.objects.filter(
        lesson__course=course).order_by('lesson__order', 'id')
    selected_ids = [choice.id for choice in choices]
    total_score = 0
    for question in questions:
        if question.is_get_score(selected_ids):
            total_score += question.grade
    total_grade = sum(question.grade for question in questions)
    grade = round(total_score / total_grade * 100)
    context['course'] = course
    context['grade'] = grade
    context['choices'] = choices
    context['selected_ids'] = selected_ids
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
