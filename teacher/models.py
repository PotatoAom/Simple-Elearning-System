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
from embed_video.fields import EmbedVideoField
from home.models import *
import os
import uuid

# Create your models here.
user = models.ForeignKey(get_user_model(),on_delete=models.DO_NOTHING,null=True)

# ตารางข้อมูลส่วนตัว
def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f'profiles/{instance.user.username}/{new_filename}'

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='', max_length=512, blank=True)
    profile_pic = models.ImageField(default='default/profile.jpg', upload_to=upload_to, null=True, blank=True)
    status= models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"profile of {self.user.username}"
    

# ตารางวิชาที่สร้างไว้ (ผู้สอน)
class TeacherCourse(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default='')
    course=models.ForeignKey('home.Course',on_delete=models.CASCADE,default='')
    

#-------------------------------------------------------------------------------------------------------#

# ตารางสร้างบทเรียนในวิชา
class Classroom(models.Model):
    title = models.CharField(max_length=50)
    course = models.ForeignKey('home.Course',on_delete=models.CASCADE,default='')
    slug = models.SlugField(allow_unicode=True, unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{} (id={})'.format(self.title, self.course)

    def get_classroom_url(self):
        return reverse('classroom_view', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())[:8]
            super(Classroom, self).save(*args, **kwargs)


def upload_imagebox(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f'courses/{instance.classroom.course.slug}/teacher/images/{new_filename}'

# การสร้างเนื้อหาในบทเรียน
class TextBox(models.Model):
    context = models.CharField(max_length=2048,null=True, blank=True)
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE,default='')
    date = models.DateTimeField(auto_now=True)

class VideoBox(models.Model):
    video = EmbedVideoField(null=True, blank=True)
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE,default='')
    date = models.DateTimeField(auto_now=True)

class ImageBox(models.Model):
    image = models.ImageField(upload_to=upload_imagebox, null=True, blank=True)
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE,default='')
    date = models.DateTimeField(auto_now=True)
    

# ตารางสร้าง Assignments
class Assignment(models.Model):
    title = models.CharField(max_length=50)
    context = models.CharField(max_length=2048,null=True, blank=True,default='ไม่มีรายละเอียดประกอบ')
    course = models.ForeignKey('home.Course',on_delete=models.CASCADE,default='')
    date = models.DateTimeField(auto_now=True)


def upload_document(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f'courses/{instance.course.slug}/teacher/document/{new_filename}'

class DocumentFile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default='')
    course=models.ForeignKey('home.Course',on_delete=models.CASCADE,default='')
    date = models.DateTimeField(auto_now=True)
    doc_file = models.FileField(upload_to=upload_document, validators=[FileExtensionValidator(
        allowed_extensions=['pdf', 'ppt', 'docx', 'txt']
    )])

    def filename(self):
        return os.path.basename(self.doc_file.name)
    

# ตารางสร้างแบบทดสอบ
class Exam(models.Model):
   owner = models.ForeignKey(User, on_delete=models.CASCADE,default='')
   course= models.ForeignKey('home.Course',on_delete=models.CASCADE,default='')
   join_code = models.CharField(max_length=6, default='000000')
   

# ตารางสร้างคำถาม
class Question(models.Model):
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE,default='')
    marks=models.PositiveIntegerField(default=1)
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    choice=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=choice)


#-------------------------------------------------------------------------------------------------------#
