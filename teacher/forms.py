from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.models import User
from .models import Teacher, Classroom, Assignment, Question, DocumentFile
from home.models import Course

class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UpdateTeacherForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control', 'placeholder': 'ประวัติโดยสังเขป...'}),
        required=False,
        )

    class Meta:
        model = Teacher
        fields = ['profile_pic', 'bio']


class CourseForm(forms.ModelForm):
    image = forms.ImageField(label='image',required=False,widget=forms.ClearableFileInput(attrs={'style': 'color: grey;','id': 'image','accept': 'image/*',}))
    class Meta:
        model = Course
        fields = ['course_name', 'commit', 'image', 'description']
        widgets = {
            'course_name': forms.TextInput(attrs={'style': 'display: block; color: grey;', 'class': 'form-control'}),
            'commit': forms.NumberInput(attrs={'style': 'display: block; color: grey;'}),
            'description': forms.Textarea(attrs={"rows":"5", 'style': 'color: grey;', 'maxlength': '300'}),
        }
        

class DocumentForm(forms.ModelForm):
    doc_file = forms.FileField()
    class Meta:
        model = DocumentFile
        fields = ['doc_file']


class CourseContentForm(forms.ModelForm):
    context = forms.CharField(
        widget=forms.Textarea(attrs={"rows":"5"}),
        required=False
        )
    video = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
        )
    
    class Meta:
        model = Classroom
        fields = ['context','video']


class AssignmentForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    context = forms.CharField(
        widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control'}),
        required=False
        )
    
    class Meta:
        model = Assignment
        fields = ['title','context']  


class ExamForm(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['question','option1','option2','option3','option4','answer']   