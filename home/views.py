from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User,auth,Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login,get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.urls import path,reverse
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count, Prefetch
from .models import *
from .forms import *
from student import models as smodel
from teacher import models as tmodel
import sweetify

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

# Create your views here.
def index(request):
    return HttpResponseRedirect('home') 

@login_required
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin') 
    
# Check User Groups
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()
def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# HomePage

# หน้า Home
def home(request):
    course = Course.objects.all().count()
    student = smodel.Student.objects.all().count()
    teacher = tmodel.Teacher.objects.all().count()

    # จำนวนนักเรียนและจำนวนการรีวิว
    popular_courses = Course.objects.annotate(
        student_count=Count('studentcourse', distinct=True),
        rating_count=Count('rating', distinct=True)
    ).order_by('-student_count')[:2]
    
    # แสดงผลการรีวิว
    popular_courses = popular_courses.prefetch_related(
        Prefetch('rating_set', queryset=Rating.objects.all(), to_attr='course_ratings')
    )

    return render(request, 'home/home.html', {'popular_courses':popular_courses, 'student':student, 'teacher':teacher, 'course':course})


# หน้า About
def about(request):
    return render(request,'home/about.html',{})


# สำหรับระบบที่ยังสร้างไม่เสร็จ
def page_404(request):
    return render(request,'home/404.html',{})


# หน้า Contact
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'ทำการบันทึกเรียบร้อยแล้ว')
    else:
        form = ContactForm()

    return render(request,'home/contact.html',{ 'form':form })


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# ระบบ Authentication
    
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            student=smodel.Student.objects.create(user_id=user.id)
            student.save()
            student_group = Group.objects.get_or_create(name='STUDENT')
            student_group[0].user_set.add(user) 
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'home/register.html', {'form': form})
    

# หน้า register สำหรับอาจารย์ 
def teacher_sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            teacher=tmodel.Teacher.objects.create(user_id=user.id)
            teacher.save()
            teacher_group = Group.objects.get_or_create(name='TEACHER')
            teacher_group[0].user_set.add(user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'home/teacher_register.html', {'form': form})


# หน้า login
def sign_in(request):
    if request.method == 'GET':
        return render(request,'home/login.html')
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
    user = auth.authenticate(request,username=username,password=password)
    if user is not None:
       auth.login(request,user)
       if is_student(request.user):      
            return HttpResponseRedirect('/home') 
       elif is_teacher(request.user):      
            return HttpResponseRedirect('/home') 
       else:
           return redirect('/admin/')
    else :
        messages.warning(request,f'Invalid username or password')
        return redirect('login')
    

# เปลี่ยนรหัสผ่าน
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            auth.logout(request)
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'home/change_password.html', {'form': form})


# เมื่อทำการ logout
def sign_out(request):
    auth.logout(request)
    messages.success(request,f'You have been logged out.')

    return redirect('login') 


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
