from django import forms
from django.contrib.auth.models import User
from .models import Student,AssignmentFile


class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UpdateStudentForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={"rows":"5", 'class': 'form-control' , 'placeholder': 'ประวัติโดยสังเขป...'}),
        required=False,
        )

    class Meta:
        model = Student
        fields = ['profile_pic', 'bio']


class AssignmentForm(forms.ModelForm):
    assign_file = forms.FileField()
    class Meta:
        model = AssignmentFile
        fields = ['assign_file']