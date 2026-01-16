from django.shortcuts import render, redirect
from django.db.models import Avg, Max, Min, Sum, Q, F
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User,auth,Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import logout, login
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.urls import path,reverse
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from urllib.request import urlopen
from .utils import generate_class_code, delete_directory
from .forms import UpdateUserForm, UpdateTeacherForm, CourseForm, DocumentForm, CourseContentForm, AssignmentForm, ExamForm
from .models import *
from home import models as hmodel
from student import models as smodel
import sweetify

# เช็คว่า user ปัจจุบันเป็นผู้สอนใช่ไหม
def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

# หน้า Profile
@login_required
@user_passes_test(is_teacher)
def teacher_profile(request):
    user = User.objects.get(id=request.user.id)
    teacher = Teacher.objects.filter(user=request.user)
    # แก้ไข profile ปัจจุบัน
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        teacher_form = UpdateTeacherForm(request.POST, request.FILES, instance=request.user.teacher)

        if user_form.is_valid() and teacher_form.is_valid():
            user_form.save()
            teacher_form.save()
            sweetify.success(request, 'แก้ไขโปรไฟล์เรียบร้อยแล้ว')
            return redirect('/teacher/profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        teacher_form = UpdateTeacherForm(instance=request.user.teacher)

    return render(request, 'teacher/teacher_profile.html',{'user':user, 'teacher': teacher,'user_form': user_form, 'teacher_form': teacher_form})

def success(request):
    return HttpResponse('successfully uploaded')


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# ระบบห้องเรียน

# หน้ารวมคอร์สเรียน (ดูได้เฉพาะวิชาที่ User คนนั้นสร้างเท่านั้น)
@login_required
@user_passes_test(is_teacher)
def teacher_course(request):
    course = hmodel.Course.objects.filter(owner=request.user)
    
    # ค้นหาจากชื่อคอร์ส
    search_query = request.GET.get('search', '')
    if search_query:
        course = course.filter(course_name__icontains=search_query)

    total_course = course.count()
    
    if request.method == 'POST':
        course_name=request.POST['course_name']
        commit=request.POST['commit']
        subject=request.POST['subject']
        existing_codes=[]
        join_code = generate_class_code(6,existing_codes)

        if hmodel.Course.objects.filter(course_name=course_name).exists():
            sweetify.warning(request,f"ชื่อคอร์สเรียนนี้ถูกใช้ไปแล้ว")
            return redirect('/teacher/course')
        
        else :
            course = hmodel.Course.objects.create(
                course_name=course_name,
                commit=commit,
                subject=subject,
                owner=request.user,
                join_code=join_code
                )
            create_course = Exam.objects.create(
                owner=request.user,
                course=course
                )
            teacher=TeacherCourse.objects.create(user=request.user, course=course)
            course.save()
            create_course.save()
            teacher.save()
            sweetify.success(request,f"สร้างคอร์สเรียบร้อย")
            return HttpResponseRedirect('/teacher/course')

    return render(request, 'teacher/teacher_course.html', {'course':course,'total_course':total_course})


# หน้าจัดการคอร์สเรียน
@login_required
@user_passes_test(is_teacher)
def manage_course(request, slug):
    course = hmodel.Course.objects.get(slug=slug)

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        commit = request.POST.get('commit')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # อัปเดตข้อมูลใน Object
        course.course_name = course_name
        course.commit = commit
        course.description = description
        if image:
            course.image = image
        course.save()
        sweetify.success(request, 'แก้ไขรายละเอียดเรียบร้อยแล้ว')
        return redirect('manage_course', slug=course.slug)

    return render(request, 'teacher/manage_course.html', {'course':course})


# upload เอกสารประกอบการเรียนเข้าระบบ
@login_required
@user_passes_test(is_teacher)
def document_upload(request,slug):
    course = hmodel.Course.objects.get(slug=slug)
    doc = DocumentFile.objects.filter(course=course)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = DocumentFile(doc_file=request.FILES['doc_file'], course_id=course.id , user_id=request.user.id)
            instance.save()
            sweetify.success(request, 'อัปโหลดไฟล์เอกสารเรียบร้อยแล้ว')
            return redirect('document_upload',slug=course.slug)
    else:
        form = DocumentForm()

    return render(request, 'teacher/document_upload.html', {'form': form, 'doc':doc, 'course':course})


# ลบเอกสารออก
@login_required
@user_passes_test(is_teacher)
def delete_doc(request,pk):
    doc=DocumentFile.objects.get(id=pk)
    doc.delete()
    sweetify.success(request, 'ลบไฟล์เอกสารเรียบร้อยแล้ว')

    return redirect('document_upload',slug=doc.course.slug)


# หน้าเนื้อหาภายในคอร์สเรียน
@login_required
@user_passes_test(is_teacher)
def manage_course_content(request,slug):
    course = hmodel.Course.objects.get(slug=slug)
    
    classroom = Classroom.objects.filter(course=course)
    total_classroom = classroom.count()

    if request.method == 'POST':
        title = request.POST.get('title')
        
        if total_classroom >= 15:
            sweetify.error(request, "บทเรียนเต็มแล้ว (มากสุด 15 บท)")
            return redirect('manage_course_content', slug=course.slug)

        if classroom.filter(title=title).exists():
            sweetify.warning(request, "ชื่อบทนี้ถูกใช้ไปแล้ว")
            return redirect('manage_course_content', slug=course.slug)
        
        else :
            classroom=Classroom.objects.create(
                title=title,
                course=course,
                )
            classroom.save()
            sweetify.success(request,f"เพิ่มบทเรียนเรียบร้อยแล้ว")
            return redirect('manage_course_content',slug=course.slug)

    return render(request, 'teacher/manage_course_content.html', {'course':course, 'classroom':classroom, 'total_classroom':total_classroom})


# แก้ไขเนื้อหาภายในคอร์สเรียน
@login_required
@user_passes_test(is_teacher)
def edit_course_content(request,pk,slug):
    course = hmodel.Course.objects.get(slug=slug)
    classroom = Classroom.objects.get(id=pk)

    if request.method == 'POST':
        form = CourseContentForm(request.POST, instance=classroom)

        if form.is_valid() :
            form.save()
            sweetify.success(request, 'แก้ไขเนื้อหาภายในเรียบร้อยแล้ว')
            return redirect('manage_course_content',slug=course.slug)
    else:
        form = CourseContentForm(request.POST, instance=classroom)

    return render(request, 'teacher/edit_course_content.html', {'course':course,'classroom':classroom,'form':form})


# การสร้างเนื้อหาภายในคอร์สเรียน
@login_required
@user_passes_test(is_teacher)
def get_course_classrooms(request, slug):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            course = hmodel.Course.objects.get(slug=slug)
            classrooms = Classroom.objects.filter(course=course)
            
            # นับจำนวน content ของเนื้อหาบทนั้นๆ ไม่เกิน 10 อย่าง
            classrooms_data = []
            for classroom in classrooms:
                box_count = (TextBox.objects.filter(classroom=classroom).count() +
                           VideoBox.objects.filter(classroom=classroom).count() +
                           ImageBox.objects.filter(classroom=classroom).count())
                
                classrooms_data.append({
                    'id': classroom.id,
                    'title': classroom.title,
                    'box_count': box_count
                })
            
            return JsonResponse({
                'success': True,
                'classrooms': classrooms_data
            })
        except hmodel.Course.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'ไม่พบคอร์สเรียน'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# สร้างกล่องข้อความ
@login_required
@user_passes_test(is_teacher)
def create_textbox(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            classroom_id = request.POST.get('classroom_id')
            context = request.POST.get('context')
            classroom = Classroom.objects.get(id=classroom_id)
            
            total_boxes = (TextBox.objects.filter(classroom=classroom).count() +
                          VideoBox.objects.filter(classroom=classroom).count() +
                          ImageBox.objects.filter(classroom=classroom).count())
            
            # เกิน 10 แล้วเพิ่มต่อไม่ได้
            if total_boxes >= 10:
                return JsonResponse({'success': False, 'message': 'บทเรียนนี้เต็มแล้ว (สูงสุด 10 อัน)'})
            
            if not context:
                return JsonResponse({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบ'})
            
            textbox = TextBox.objects.create(
                context=context,
                classroom=classroom
            )
            
            return JsonResponse({
                'success': True,
                'message': 'เพิ่มบทความเรียบร้อย',
                'box_id': textbox.id,
                'box_type': 'textbox'
            })
        except Classroom.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'ไม่พบบทเรียน'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# แปะลิงค์ url สำหรับ video
@login_required
@user_passes_test(is_teacher)
def create_videobox(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            classroom_id = request.POST.get('classroom_id')
            video = request.POST.get('video')
            classroom = Classroom.objects.get(id=classroom_id)

            total_boxes = (TextBox.objects.filter(classroom=classroom).count() +
                          VideoBox.objects.filter(classroom=classroom).count() +
                          ImageBox.objects.filter(classroom=classroom).count())
            
            if total_boxes >= 10:
                return JsonResponse({'success': False, 'message': 'บทเรียนนี้เต็มแล้ว (สูงสุด 10 อัน)'})
            
            if not video:
                return JsonResponse({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบ'})
            
            videobox = VideoBox.objects.create(
                video=video,
                classroom=classroom
            )
            
            return JsonResponse({
                'success': True,
                'message': 'เพิ่มวิดีโอเรียบร้อย',
                'box_id': videobox.id,
                'box_type': 'videobox'
            })
        except Classroom.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'ไม่พบบทเรียน'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# ใส่รูปภาพประกอบ
@login_required
@user_passes_test(is_teacher)
def create_imagebox(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            classroom_id = request.POST.get('classroom_id')
            image = request.FILES.get('image')
            classroom = Classroom.objects.get(id=classroom_id)
            
            total_boxes = (TextBox.objects.filter(classroom=classroom).count() +
                          VideoBox.objects.filter(classroom=classroom).count() +
                          ImageBox.objects.filter(classroom=classroom).count())
            
            if total_boxes >= 10:
                return JsonResponse({'success': False, 'message': 'บทเรียนนี้เต็มแล้ว (สูงสุด 10 อัน)'})
            
            if not image:
                return JsonResponse({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบ'})
            
            imagebox = ImageBox.objects.create(
                image=image,
                classroom=classroom
            )
            
            return JsonResponse({
                'success': True,
                'message': 'เพิ่มรูปภาพเรียบร้อย',
                'box_id': imagebox.id,
                'box_type': 'imagebox'
            })
        except Classroom.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'ไม่พบบทเรียน'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# ลบ box ออก (textbox, imagebox, videobox)
@login_required
@user_passes_test(is_teacher)
def delete_box(request, box_type, box_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if box_type == 'textbox':
                box = TextBox.objects.get(id=box_id)
            elif box_type == 'videobox':
                box = VideoBox.objects.get(id=box_id)
            elif box_type == 'imagebox':
                box = ImageBox.objects.get(id=box_id)
            else:
                return JsonResponse({'success': False, 'message': 'Invalid box type'})
            
            box.delete()
            return JsonResponse({'success': True, 'message': 'ลบเนื้อหาเรียบร้อยแล้ว'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# แสดงผลเนื้อหาภายในบทเรียน
@login_required
@user_passes_test(is_teacher)
def get_classroom_boxes(request, classroom_id):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            classroom = Classroom.objects.get(id=classroom_id)
            
            textboxes = list(TextBox.objects.filter(classroom=classroom).values('id', 'context', 'date'))
            videoboxes = list(VideoBox.objects.filter(classroom=classroom).values('id', 'video', 'date'))
            imageboxes_qs = ImageBox.objects.filter(classroom=classroom)
            imageboxes = []
            for img in imageboxes_qs:
                imageboxes.append({
                    'id': img.id,
                    'image': img.image.url if img.image else '',
                    'date': img.date
                })
            
            for box in textboxes:
                box['box_type'] = 'textbox'
            for box in videoboxes:
                box['box_type'] = 'videobox'
            for box in imageboxes:
                box['box_type'] = 'imagebox'
            
            # เรียงจากวันที่สร้างก่อนไปหลัง
            all_boxes = sorted(
                textboxes + videoboxes + imageboxes,
                key=lambda b: b['date'],
                reverse=False
            )
            
            return JsonResponse({
                'success': True,
                'boxes': all_boxes,
                'box_count': len(all_boxes),
                'remaining': 10 - len(all_boxes)
            })
        except Classroom.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'ไม่พบบทเรียน'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# หน้าจัดการ Assignment
@login_required
@user_passes_test(is_teacher)
def manage_assignment(request,slug):
    course = hmodel.Course.objects.get(slug=slug)
    assign = Assignment.objects.all().filter(course=course.id)
    student = smodel.AssignmentFile.objects.all().filter(course=course.id)
    total_assign = Assignment.objects.all().filter(course=course.id).count()

    if request.method == 'POST':
        title=request.POST['title']
        context=request.POST['context']
        
        assign=Assignment.objects.create(
            title=title,
            context=context,
            course=course,
            )
        assign.save()
        sweetify.success(request,f"สร้าง Assignment เรียบร้อย")
        return redirect('manage_assignment',slug=course.slug)

    return render(request, 'teacher/manage_assignment.html', {'course':course, 'assign':assign, 'student':student, 'total_assign':total_assign})


# แก้ไข Assignment
@login_required
@user_passes_test(is_teacher)
def edit_assignment(request, pk, slug):
    course = hmodel.Course.objects.get(slug=slug)
    assign_edit = Assignment.objects.get(id=pk)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assign_edit)

        if form.is_valid() :
            form.save()
            sweetify.success(request, 'แก้ไข assignments เรียบร้อยแล้ว')
            return redirect('manage_assignment',slug=course.slug)
    else:
        form = AssignmentForm(instance=assign_edit)

    return render(request, 'teacher/manage_assignment.html', {'course':course,'assign':assign_edit,'form':form})


# download ไฟล์ assignment ของผู้เรียน
def download_file(request, pk):
    assignment_file = smodel.AssignmentFile.objects.get(id=pk)
    filename = os.path.basename(assignment_file.assign_file.name)
    response = HttpResponse(assignment_file.assign_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


# ลบคอร์สเรียน
@login_required
@user_passes_test(is_teacher)
def delete_course(request,pk):
    course=hmodel.Course.objects.get(id=pk)
    delete_directory(f"{course.slug}")
    course.delete()
    sweetify.success(request, 'ลบคอร์สร้อยแล้ว')

    return HttpResponseRedirect('/teacher/course')


# ลบเนื้อหาภายในบทเรียน
@login_required
@user_passes_test(is_teacher)
def delete_content(request,pk):
    classroom = Classroom.objects.get(id=pk)
    course_slug = classroom.course.slug
    classroom.delete()
    sweetify.success(request, 'ลบเนื้อหาบทเรียนเรียบร้อยแล้ว')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'ลบเนื้อหาบทเรียนเรียบร้อยแล้ว'})
    
    return redirect('manage_course_content',slug=course_slug)


# ลบ assignment
@login_required
@user_passes_test(is_teacher)
def delete_assign(request,pk):
    assignment = Assignment.objects.get(id=pk)
    assignment.delete()
    sweetify.success(request, 'ลบ assignment เรียบร้อยแล้ว')

    return redirect('manage_assignment',slug=assignment.course.slug)


#-------------------------------------------------------------------------------------------------------------------------------------------------------#
# ระบบแบบทดสอบ

# หน้าจัดการ/สร้างแบบทดสอบ
@login_required
@user_passes_test(is_teacher)
def manage_exam(request,pk):
    course = hmodel.Course.objects.get(id=pk)
    exam = Exam.objects.get(course=pk)
    student = smodel.StudentCourse.objects.filter(course=pk)
    question = Question.objects.all().filter(exam=exam.id)
    total_question = Question.objects.all().filter(exam=exam).count()
    total_marks=0

    if request.method == 'POST':
        question=request.POST['question']
        option1=request.POST['option1']
        option2=request.POST['option2']
        option3=request.POST['option3']
        option4=request.POST['option4']
        answer=request.POST['answer']
        if question  == '' or option1 == '' or option2 == '' or option3 == '' or option4 == '' or answer == '':
            sweetify.warning(request,f"กรุณากรอกข้อมูลให้ครบถ้วน")  
            return redirect('manage_exam',pk=exam.id)
        else :
            create_question = Question.objects.create(
                question=question,
                marks=1,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                answer=answer,
                exam_id=exam.id,
            )
            create_question.save()
            sweetify.success(request,f"สร้างแบบทดสอบเรียบร้อย")  
            return redirect('manage_exam',pk=exam.id)

    for q in question:
        total_marks=total_marks + q.marks

    return render(request,'teacher/manage_exam.html',{
        'student':student,
        'exam':exam,
        'course':course,
        'question':question,
        'total_question':total_question,
        'total_marks':total_marks
        })


# แก้ไขแบบทดสอบ
@login_required
@user_passes_test(is_teacher)
def edit_exam(request,pk,course_id):
    course = hmodel.Course.objects.get(id=course_id)
    exam = Exam.objects.get(course=course)
    question = Question.objects.get(id=pk)

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=question)

        if form.is_valid() :
            form.save()
            sweetify.success(request, 'แก้ไขแบบทดสอบเรียบร้อยแล้ว')
            return redirect('manage_exam',pk=exam.id)
    else:
        form = ExamForm(request.POST, instance=question)

    return render(request, 'teacher/manage_exam.html', {'course':course,'question':question,'form':form})


# ลบแบบทดสอบ
@login_required
@user_passes_test(is_teacher)
def delete_exam(request,pk):
    exam = Exam.objects.get(id=pk)
    exam.delete()
    sweetify.success(request, 'ลบแบบทดสอบเรียบร้อยแล้ว')

    return HttpResponseRedirect('/teacher/exam')


# ลบคำถามแบบทดสอบ
@login_required
@user_passes_test(is_teacher)
def delete_question(request,pk):
    question = Question.objects.get(id=pk)
    question.delete()
    sweetify.success(request, 'ลบคำถามเรียบร้อยแล้ว')

    return redirect('manage_exam',pk=question.exam.id)


# ดูคะแนนรวมของผู้เรียน
@login_required
@user_passes_test(is_teacher)
def manage_score(request,slug):
    course = hmodel.Course.objects.get(slug=slug)
    exam = Exam.objects.filter(course=course, owner=request.user.id)
    results= smodel.Result.objects.all().filter(exam__in=exam)
    question = Question.objects.all().filter(exam__in=exam)
    total_result = smodel.Result.objects.all().filter(exam__in=exam).count()
    total=0

    sum = smodel.Result.objects.filter(exam__in=exam).aggregate(sum=Sum("marks"))['sum'] 
    average = smodel.Result.objects.filter(exam__in=exam).aggregate(avg=Avg("marks"))['avg']
    max = smodel.Result.objects.filter(exam__in=exam).aggregate(max=Max("marks"))['max']
    min = smodel.Result.objects.filter(exam__in=exam).aggregate(min=Min("marks"))['min']

    for q in question:
        total=total + q.marks

    return render(request,'teacher/manage_score.html',{
        'results':results,
        'sum':sum,
        'average':average,
        'max':max,
        'min':min,
        'total_result':total_result,
        'course':course,
        'total':total
        })


#-------------------------------------------------------------------------------------------------------------------------------------------------------#