from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

CustomUser = get_user_model()

class SignUpForm(forms.ModelForm):
  password = forms.CharField(
    widget=forms.PasswordInput(attrs={
      'class': 'form-control',
      'placeholder': '••••••••'
    }),
    label='Create Password'
  )
  confirm_password = forms.CharField(
    widget=forms.PasswordInput(attrs={
      'class': 'form-control',
      'placeholder': '••••••••'
    }),
    label='Verify Password'
  )
  
  class Meta:
    model = CustomUser
    fields = ('student_id',)
    widgets = {
      'student_id': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. 232022',
        'maxlength': '6'
      })
    }
    labels = {
      'student_id': 'Student ID Number'
    }
  
  def clean_student_id(self):
    student_id = self.cleaned_data.get('student_id')
    if not student_id.isdigit() or len(student_id) != 6:
      raise ValidationError('Student ID must be exactly 6 digits.')
    if CustomUser.objects.filter(student_id=student_id).exists():
      raise ValidationError('This Student ID is already registered.')
    return student_id
  
  def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')
    
    if password and confirm_password and password != confirm_password:
      raise ValidationError('Passwords do not match.')
    
    if password and len(password) < 6:
      raise ValidationError('Password must be at least 6 characters long.')
    
    return cleaned_data
  
  def save(self, commit=True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data['password'])
    if commit:
      user.save()
    return user


class LoginForm(forms.Form):
  student_id = forms.CharField(
    max_length=6,
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'e.g. 232022',
      'maxlength': '6'
    }),
    label='Student ID Number'
  )
  password = forms.CharField(
    widget=forms.PasswordInput(attrs={
      'class': 'form-control',
      'placeholder': '••••••••'
    }),
    label='Password'
  )