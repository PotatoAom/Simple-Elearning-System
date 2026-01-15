from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.urls import reverse
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db.models import Avg
from home.models import *
from teacher.models import *
import os
import uuid

# Create your models here.
user = models.ForeignKey(get_user_model(),on_delete=models.DO_NOTHING,null=True)

# ตารางข้อมูลส่วนตัว
def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f'profiles/{instance.user.username}/{new_filename}'

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='', max_length=512, blank=True)
    profile_pic = models.ImageField(default='default/profile.jpg', upload_to=upload_to, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"profile of {self.user.username}"
    

# ตารางวิชาที่ลงทะเบียนไว้ (ผู้เรียน)
class StudentCourse(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default='')
    course=models.ForeignKey('home.Course',on_delete=models.CASCADE,default='')
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)


#-------------------------------------------------------------------------------------------------------#

# ตารางให้คะแนนบทเรียน
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('home.Course', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=512, default='', null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.course_name}: {self.rating}"
    

# เช็คเงื่อนไขว่าเรียนจบคลาสหรือไม่
class ClassroomDone(models.Model):
    feedback = models.CharField(max_length=1024,default='')
    classroom = models.ForeignKey('teacher.Classroom',on_delete=models.CASCADE,default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='', null=True, blank=True)
    completed = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True)


def upload_assignment(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f'courses/{instance.course.slug}/student/{instance.user.username}/assignments/{new_filename}'

class AssignmentFile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default='')
    course=models.ForeignKey('home.Course',on_delete=models.CASCADE,default='')
    assign=models.ForeignKey('teacher.Assignment',on_delete=models.CASCADE,default='')
    assign_file = models.FileField(upload_to=upload_assignment)
    date = models.DateTimeField(auto_now=True)

    def filename(self):
        return os.path.basename(self.assign_file.name)
    

# ตารางคะแนนสอบ
class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey('teacher.Exam',on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)


#-------------------------------------------------------------------------------------------------------#
