from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User,auth,Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import logout, login
from django.db.models import Count, Prefetch
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.urls import path,reverse
from django.views.decorators import gzip
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.request import urlopen
from .forms import UpdateUserForm, UpdateStudentForm, AssignmentForm
from .models import *
from home import models as hmodel
from teacher import models as tmodel
import sweetify
import json

# เช็คว่า user ปัจจุบันเป็นผู้เรียนใช่ไหม
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# หน้า profile
@login_required
@user_passes_test(is_student)
def profile(request):
    user = User.objects.get(id=request.user.id)
    student = Student.objects.filter(user=request.user)
    # แก้ไข profile ปัจจุบัน
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        student_form = UpdateStudentForm(request.POST, request.FILES, instance=request.user.student)

        if user_form.is_valid() and student_form.is_valid():
            user_form.save()
            student_form.save()
            sweetify.success(request, 'แก้ไขโปรไฟล์เรียบร้อยแล้ว')
            return redirect('/student/profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        student_form = UpdateStudentForm(instance=request.user.student)

    return render(request, 'student/profile.html',{'user':user, 'student': student,'user_form': user_form, 'student_form': student_form})


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# ระบบห้องเรียน

# filter หมวดหมู่รายวิชา
def filter_courses_by_subject(courses, subject_filter):
    if subject_filter:
        courses = courses.filter(subject__in=subject_filter)
    return courses


# หน้ารวมคอร์สทั้งหมด
def course(request):
    # จำนวนนักเรียนและจำนวนการรีวิว
    course = hmodel.Course.objects.annotate(
        student_count=Count('studentcourse', distinct=True),
        rating_count=Count('rating', distinct=True)
    ).order_by('-id')

    # แสดงผลการรีวิว
    course = course.prefetch_related(
        Prefetch('rating_set', queryset=Rating.objects.all(), to_attr='course_ratings')
    )

    # ค้นหาจากชื่อคอร์ส
    search_query = request.GET.get('search', '')
    if search_query:
        course = course.filter(course_name__icontains=search_query)
    
    # ค้นหาจากหมวดหมู่รายวิชา
    subject_filter = request.GET.getlist('subject')
    course = filter_courses_by_subject(course, subject_filter)
    
    all_subjects = hmodel.Course.SUBJECT_CHOICES
    total_course = course.count()
    
    return render(request,'home/course.html',{'course':course,'total_course':total_course,'all_subjects': all_subjects,'selected_subjects': subject_filter})
    

# หน้ารายละเอียดต่างๆจองคอร์สนั้นๆ
def course_view(request,slug):
    course = hmodel.Course.objects.get(slug=slug)
    rating = Rating.objects.filter(course=course)
    classroom = tmodel.Classroom.objects.all().filter(course_id=course).count()
    assign = tmodel.Assignment.objects.all().filter(course_id=course).count()
    rating_count = Rating.objects.all().filter(course_id=course).count()

    return render(request,'student/course_view.html',{'course':course,'rating':rating,'classroom':classroom,'assign':assign,'rating_count':rating_count})


# การลงทะเบียนเรียน
@login_required
@user_passes_test(is_student)
def join_course(request,pk):
    course = hmodel.Course.objects.get(id=pk)

    if StudentCourse.objects.filter(course_id=course).filter(user=request.user).exists():
        sweetify.warning(request,'คุณได้ลงทะเบียนคอร์สนี้แล้ว')
        return redirect("/student/course")
    else:    
        StudentCourse.objects.create(user=request.user, course=course)
        sweetify.success(request,'ลงทะเบียนคอร์สเรียบร้อยแล้ว')
        return redirect("/student/enrolled")


# หน้าคอร์สที่ลงทะเบียนแล้ว
@login_required
@user_passes_test(is_student)
def enrolled(request):
    total_course = StudentCourse.objects.all().filter(user=request.user).count() # จำนวนรายวิชา
    courses = StudentCourse.objects.all().filter(user=request.user) # แสดงผลรายวิชาทั้งหมด
    try:
        student_obj = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student_obj = None

    # เข้าร่วมผ่าน code
    if request.method == "POST":
        join_code = request.POST["join_code"]
        try:
            course = hmodel.Course.objects.get(join_code=join_code)
            if hmodel.StudentCourse.objects.filter(course_id=course).filter(user=request.user).exists():
                sweetify.warning(request,'คุณได้ลงทะเบียนคอร์สนี้แล้ว')
                return redirect("/student/enrolled")
            else:    
                StudentCourse.objects.create(user=request.user, course=course)
                sweetify.success(request,'ลงทะเบียนคอร์สเรียบร้อยแล้ว')
                return redirect("/student/enrolled")
        except:
            sweetify.warning(request,'รหัสคอร์สไม่ถูกต้อง')
            return redirect("/student/enrolled")

    # คำนวณ progress bar โดยนับจากการเรียนในแต่ละบท, assignment และ การทำแบบทดสอบ
    for sc in courses:
        total_classes = tmodel.Classroom.objects.filter(course_id=sc.course).count()
        done_classes = ClassroomDone.objects.filter(classroom__course=sc.course, user=request.user).count()

        total_assignments = tmodel.Assignment.objects.filter(course=sc.course).count()
        done_assignments = AssignmentFile.objects.filter(course=sc.course, user=request.user).values('assign').distinct().count()

        total_exams = tmodel.Exam.objects.filter(course=sc.course).count()
        if student_obj:
            done_exams = Result.objects.filter(student=student_obj, exam__course=sc.course).count()
        else:
            done_exams = 0

        total_items = total_classes + total_assignments + total_exams
        done_items = done_classes + done_assignments + done_exams
        if total_items > 0:
            progress_percent = int(round(done_items / total_items * 100))
        else:
            progress_percent = 0

        sc.progress = progress_percent
        sc.total_classes = total_classes
        sc.done_classes = done_classes
        sc.total_assignments = total_assignments
        sc.done_assignments = done_assignments
        sc.total_exams = total_exams
        sc.done_exams = done_exams
        sc.total_items = total_items
        sc.done_items = done_items

    return render(request,'student/enrolled.html',{'courses':courses,'total_course':total_course})


# ยกเลิกการลงทะเบียนเรียน
@login_required
@user_passes_test(is_student)
def delete_enrolled(request,pk):
    course = hmodel.Course.objects.get(id=pk)
    enrolled = StudentCourse.objects.get(course=course,user_id=request.user)
    enrolled.delete()
    sweetify.success(request, 'ยกเลิกการลงทะเบียนเรียบร้อยแล้ว')

    return HttpResponseRedirect('/student/enrolled')


# ดูรายละเอียดภายในคอร์ส
@login_required
@user_passes_test(is_student)
def enrolled_view(request,slug):
    course = hmodel.Course.objects.get(slug=slug)
    student = StudentCourse.objects.all().filter(course_id=course)
    classview = tmodel.Classroom.objects.all().filter(course_id=course)
    assignview = tmodel.Assignment.objects.all().filter(course_id=course)
    classroom_count = classview.count()
    assign_count = assignview.count()

    return render(request,'student/enrolled_view.html',{
        'course':course,
        'student':student,
        'classview':classview,
        'assignview':assignview,
        'classroom_count':classroom_count,
        'assign_count':assign_count
        })


# ดูเอกสารประกอบการเรียนทั้งหมด
@login_required
@user_passes_test(is_student)
def document_view(request,slug):
    course = hmodel.Course.objects.get(slug=slug)
    classview = tmodel.Classroom.objects.all().filter(course_id=course)
    assignview = tmodel.Assignment.objects.all().filter(course_id=course)
    doc = tmodel.DocumentFile.objects.all().filter(course_id=course)

    return render(request,'student/document_view.html',{'course':course,'classview':classview,'assignview':assignview,'doc':doc})


# download เอกสารประกอบการเรียน
def std_download_file(request, pk):
    document_file = tmodel.DocumentFile.objects.get(id=pk)
    filename = os.path.basename(document_file.doc_file.name)
    response = HttpResponse(document_file.doc_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


# เนื้อหาภานในบทเรียน
@login_required
@user_passes_test(is_student)
def classroom_view(request,classroom_id,slug):
    course = hmodel.Course.objects.get(slug=slug)
    classroom = tmodel.Classroom.objects.filter(id=classroom_id)
    all_classroom = list(tmodel.Classroom.objects.filter(course_id=course).order_by('id'))
    current_classroom = tmodel.Classroom.objects.get(id=classroom_id)
    classroom_number = all_classroom.index(current_classroom) + 1

    done = tmodel.Classroom.objects.get(id=classroom_id)
    done_check = ClassroomDone.objects.filter(classroom_id=done,user_id=request.user)

    # ยืนยันว่าเรียนเสร็จแล้ว / บทนั้นๆ
    if request.method == 'POST':
        done = ClassroomDone.objects.create(
            classroom=done,
            user=request.user,
            )
        done.save()
        sweetify.success(request, 'ยืนยันเรียบร้อย')
        return redirect('classroom_view',slug=course.slug,classroom_id=classroom_id)
    
    textboxes = tmodel.TextBox.objects.filter(classroom=done)
    videoboxes = tmodel.VideoBox.objects.filter(classroom=done)
    imageboxes = tmodel.ImageBox.objects.filter(classroom=done)

    # แสดงผลตามลำดับวันที่สร้าง จากก่อนไปหลัง
    content_items = []
    for tb in textboxes:
        content_items.append({'type': 'textbox', 'obj': tb, 'date': tb.date})
    for vb in videoboxes:
        content_items.append({'type': 'videobox', 'obj': vb, 'date': vb.date})
    for ib in imageboxes:
        content_items.append({'type': 'imagebox', 'obj': ib, 'date': ib.date})

    content_items.sort(key=lambda x: x['date'])

    return render(request,'student/classroom_view.html',{
        'course': course,
        'classroom': classroom,
        'classroom_number': classroom_number,
        'done_check': done_check,
        'content_items': content_items
        })


# ดู assignment ทั้งหมด
@login_required
@user_passes_test(is_student)
def assign_view(request,assignment_id,slug):
    course = hmodel.Course.objects.get(slug=slug)
    assign = tmodel.Assignment.objects.filter(id=assignment_id)
    assignment = tmodel.Assignment.objects.get(id=assignment_id)

    # เช็คว่าส่งงานหรือยัง
    assign_check = AssignmentFile.objects.filter(assign_id=assignment,user_id=request.user)

    # ผู้เรียนส่งไฟล์ assignment เข้ามาในระบบ
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = AssignmentFile(assign_file=request.FILES['assign_file'], course_id=course.id , user_id=request.user.id, assign_id=assignment.id)
            instance.save()
            sweetify.success(request, 'ส่งงานเรียบร้อย')
            return redirect('assign_view',slug=course.slug,assignment_id=assignment.id)
    else:
        form = AssignmentForm()
    
    return render(request,'student/assign_view.html',{
        'course':course,
        'assign':assign,
        'form':form,
        'assign_check':assign_check
        })


# ระบบรีวิวิคะแนน
@login_required
@user_passes_test(is_student)
def rate_course(request, course_id):
    if request.method == 'POST':
        course = hmodel.Course.objects.get(id=course_id)
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                rating_val = data.get('rating')
                comment = data.get('comment')
                defaults = {}
                if rating_val is not None:
                    defaults['rating'] = int(rating_val)
                if comment is not None:
                    defaults['comment'] = comment

                Rating.objects.update_or_create(
                    user=request.user,
                    course=course,
                    defaults=defaults
                )
                return JsonResponse({'status': 'success'}, status=200)
            else:
                review = request.POST.get('review', '').strip()
                rating_val = request.POST.get('rating')
                defaults = {}
                if rating_val:
                    defaults['rating'] = int(rating_val)
                defaults['comment'] = review

                Rating.objects.update_or_create(
                    user=request.user,
                    course=course,
                    defaults=defaults
                )
                sweetify.success(request, 'รีวิวถูกบันทึกแล้ว')
                return redirect('result', slug=course.slug)
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            else:
                sweetify.error(request, 'ไม่สามารถบันทึกรีวิวได้: ' + str(e))
                return redirect('result', slug=course.slug)


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# ระบบทำแบบทดสอบ

# หน้ารายละเอียดแบบทดสอบ
@login_required
@user_passes_test(is_student)
def exam_view(request,pk):
    exam = tmodel.Exam.objects.get(id=pk)
    questions = tmodel.Question.objects.all().filter(exam=exam)
    student = Student.objects.get(user=request.user.id)
    total_questions = tmodel.Question.objects.all().filter(exam=exam).count()
    total_marks = 0

    # เช็คเงื่อนไขว่าทำแบบทดสอบแล้วหรือยัง
    if Result.objects.filter(student=student,exam=pk).exists():
        sweetify.warning(request,'ทำแบบทดสอบวิชานี้ไปแล้ว')
        return redirect('result',slug=exam.course.slug)
    
    # คะแนนแบบทดสอบทั้งหมดของคอร์สนั้นๆ
    for q in questions:
        total_marks=total_marks + q.marks

    return render(request,'student/exam_view.html',{'exam':exam,'total_questions':total_questions,'total_marks':total_marks})


# หน้าทำแบบทดสอบ
@login_required
@user_passes_test(is_student)
def start_exam(request,pk):
    exam = tmodel.Exam.objects.get(id=pk)
    questions = tmodel.Question.objects.filter(exam=exam).order_by('id')
    paginator = Paginator(questions, 1) # 1 คำถาม / 1 หน้า

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html', {'exam':exam,'questions':questions,'page_obj': page_obj})
    response.set_cookie('exam_id',exam.id)
    
    return response


# การนับคะแนน
@login_required
@user_passes_test(is_student)
def calculate_score(request):
    if request.COOKIES.get('exam_id') is not None:
        exam_id = request.COOKIES.get('exam_id')
        exam = tmodel.Exam.objects.get(id=exam_id)  
        questions = tmodel.Question.objects.all().filter(exam=exam).order_by('id')
        total_marks = 0
        
        # รวบรวมคะแนนจากแบบทดสอบเพื่อคำนวณคะแนน
        for question in questions:
            question_id = str(question.id)
            selected_ans = request.POST.get(question_id)
            actual_answer = question.answer
            
            if selected_ans == actual_answer:
                total_marks = total_marks + question.marks
        
        student = Student.objects.get(user_id=request.user.id)
        result = Result()
        result.marks = total_marks
        result.exam = exam
        result.student = student
        result.save()

        return redirect('result', slug=exam.course.slug)
    

# สรุปผลการทำแบบทดสอบ
@login_required
@user_passes_test(is_student)
def result(request,slug):
    student = Student.objects.get(user_id=request.user.id)
    course = hmodel.Course.objects.get(slug=slug)
    result = Result.objects.get(exam__course=course, student=student)
    rating_check = Rating.objects.filter(user=request.user, course=course)
    total_marks = calculate_total_marks(result.exam)  

    return render(request,'student/result.html',{
        'result':result, 
        'total_marks':total_marks, 
        'course': course, 
        'course_id': course.id, 
        'rating_check': rating_check
        })


# คำนวณคะแนนเพื่อแสดงผลแผนภูมิ
def calculate_total_marks(exam):
    questions = tmodel.Question.objects.all().filter(exam=exam)
    total = 0
    for question in questions:
        total += question.marks
        
    return total


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
