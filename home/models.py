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
from student.models import *
import os
import uuid

# Create your models here.
user = models.ForeignKey(get_user_model(),on_delete=models.DO_NOTHING,null=True)

# ตารางประกาศข่าวสาร
def news_upload(instance, filename):
    ext = filename.split('.')[-1]
    return f'news/{uuid.uuid4()}.{ext}'

class Notify(models.Model):
    title= models.CharField(max_length=60)
    announce= models.CharField(max_length=200)
    img = models.ImageField(upload_to=news_upload, null=True, blank=True)
    date =  models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return '{} (id={})'.format(self.title, self.id)
    

# ตาราง Contact
class Contact(models.Model):
    title = models.CharField(max_length=60)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField()
    context = models.TextField(max_length=1024)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


#-------------------------------------------------------------------------------------------------------#
# ตารางสร้างวิชา
def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f'courses/{instance.slug}/teacher/images/{new_filename}'

class Course(models.Model):
    course_name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,default='', null=True, blank=True)
    image = models.ImageField(default='default/classroom.jpg', upload_to=upload_to, null=True, blank=True)
    join_code = models.CharField(max_length=6, default='000000')
    commit = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(24)])
    description = models.TextField(max_length=300, null=True, blank=True, default='No description')
    slug = models.SlugField(allow_unicode=True, unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    SUBJECT_CHOICES = [   
        ('math', 'การคำนวณ'),
        ('data', 'การวิเคราะห์ข้อมูล'),
        ('it', 'เทคโนโลยีสารสนเทศ'),
        ('programming', 'การเขียนโปรแกรม'),
        ('development', 'การพัฒนาซอฟต์แวร์'),
        ('ai', 'ปัญญาประดิษฐ์'),
        ('design', 'การออกแบบ'),
        ('economics', 'การเงิน/การลงทุน'),
        ('marketing', 'การตลาด'),
        ('philosophy', 'ปรัชญา'),
        ('language', 'ภาษา'),
        ('health', 'สุขภาพ'),
        ('selfdev', 'การพัฒนาตนเอง'),
        ('other', 'อื่นๆ'),
    ]
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='other')
 
    def __str__(self):
        return self.course_name
        
    def get_teacher_url(self):
        return reverse('manage_course', kwargs={'slug': self.slug})

    def get_enrolled_url(self):
        return reverse('enrolled_view', kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return reverse('course_view', kwargs={'slug': self.slug})
    
    def average_rating(self) -> float:
        return Rating.objects.filter(course=self).aggregate(Avg("rating"))["rating__avg"] or 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())[:8]
        super(Course, self).save(*args, **kwargs)


#-------------------------------------------------------------------------------------------------------#
