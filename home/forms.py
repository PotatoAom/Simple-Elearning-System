from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.safestring import mark_safe
from .models import Course,Contact

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['first_name'].label = ''
        self.fields['last_name'].label = ''
        self.fields['email'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Firstname', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Lastname', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})
        
        self.fields['username'].help_text = mark_safe(
            "<ul style='color: gray;'><li>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</li></ul>"
        )
        self.fields['password1'].help_text = mark_safe(
            "<ul style='color: gray;'><li>Your password can't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can't be a commonly used password.</li><li>Your password can't be entirely numeric.</li></ul>"
        )
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2' )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already exist.")
        return email
    

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = ''
        self.fields['new_password1'].label = ''
        self.fields['new_password2'].label = ''
        self.fields['old_password'].widget.attrs.update({'placeholder': 'Old Password','class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'New Password','class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Comfirm Password','class': 'form-control'})

    
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['title', 'firstname', 'lastname', 'email', 'context']
        

class ImageForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["image"]
