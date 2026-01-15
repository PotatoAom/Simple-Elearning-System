from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import *
from .forms import *
from student.models import *
from teacher.models import *

#-------------------------------------------------------------------------------------------------------------------------------------------------------#

### home ###

# Custom Admin Site
class MyAdminSite(admin.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'student': Student.objects.count(),
            'teacher': Teacher.objects.count(),
            'course': Course.objects.count(),
        })
        return context

admin.site = MyAdminSite()
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)


# Course
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name', 'get_first_name', 'date')
    list_display_links = ('id', 'course_name')
    @admin.display(ordering='owner__first_name', description='Owner')
    def get_first_name(self, obj):
        return obj.owner.first_name
admin.site.register(Course, CourseAdmin)


# Notification
class NotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date')
    list_display_links = ('id', 'title')
admin.site.register(Notify, NotifyAdmin)


# Contact
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'firstname', 'email', 'date')
    list_display_links = ('id', 'title')
admin.site.register(Contact, ContactAdmin)


#-------------------------------------------------------------------------------------------------------------------------------------------------------#

### student ###

# Student Profile
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'date')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(Student, StudentAdmin)


# Student Courses
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'completed', 'date')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(StudentCourse, StudentCourseAdmin)


# เช็คว่าเรียนจบแล้ว 1 บท หรือยัง
class ClassroomDoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'classroom', 'completed', 'date')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(ClassroomDone, ClassroomDoneAdmin)


# Student Assignment file
class AssignmentFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'assign_file', 'date')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(AssignmentFile, AssignmentFileAdmin)


# Rating
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'course', 'rating', 'comment', 'date')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(Rating, RatingAdmin)


# Result
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'date', 'marks')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='student__user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.student.user.first_name
admin.site.register(Result, ResultAdmin)


#-------------------------------------------------------------------------------------------------------------------------------------------------------#

### teacher ###

# Teacher
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'date')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(Teacher, TeacherAdmin)


# Teacher Courses
class TeacherCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'course')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(TeacherCourse, TeacherCourseAdmin)


# Question
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'exam', 'marks')
    list_display_links = ('id', 'question')
admin.site.register(Question, QuestionAdmin)


# Classroom
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'date')
    list_display_links = ('id', 'title')
admin.site.register(Classroom, ClassroomAdmin)


# Textbox
class TextBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'classroom', 'date')
    list_display_links = ('id', 'classroom')
admin.site.register(TextBox, TextBoxAdmin)


# Imagebox
class ImageBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'classroom', 'date')
    list_display_links = ('id', 'classroom')
admin.site.register(ImageBox, ImageBoxAdmin)


# Videobox
class VideoBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'classroom', 'date')
    list_display_links = ('id', 'classroom')
admin.site.register(VideoBox, VideoBoxAdmin)


# การอัปโหลดไฟล์เอกสาร
class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'doc_file', 'date')
    list_display_links = ('id', 'get_first_name')
    @admin.display(ordering='user__first_name', description='Student')
    def get_first_name(self, obj):
        return obj.user.first_name
admin.site.register(DocumentFile, DocumentFileAdmin)


# Assignment
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'date')
    list_display_links = ('id', 'title')
admin.site.register(Assignment, AssignmentAdmin)


# Exam
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'course')
    list_display_links = ('id', 'course')
admin.site.register(Exam, ExamAdmin)
