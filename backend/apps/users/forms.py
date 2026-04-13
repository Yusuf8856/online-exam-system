from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class SignUpForm(UserCreationForm):
    full_name = forms.CharField(label="Full Name", max_length=100)
    email = forms.EmailField(label="Email Address")
    phone_number = forms.CharField(label="Phone Number", max_length=15)
    role = forms.ChoiceField(
        label="Select Role",
        choices=[('', 'Select Role'), ('student', 'Student'), ('teacher', 'Teacher')]
    )
    student_reg_number = forms.CharField(label="Student Registration Number", required=False)
    teacher_id = forms.CharField(label="Teacher ID", required=False)
    qualification = forms.CharField(label="Qualification", required=False)
    trained_at = forms.CharField(label="Training Institute", required=False)
    gender = forms.ChoiceField(choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=False)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date of Birth", required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    class Meta:
        model = User
        # We include username to ensure unique login identifiers
        fields = ('full_name', 'username', 'email', 'phone_number', 'role', 'student_reg_number', 'teacher_id', 'qualification', 'trained_at', 'gender', 'dob', 'address')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Add 'form-control' class to all fields for Bootstrap styling
        teacher_only = ['teacher_id', 'qualification', 'trained_at']
        student_only = ['student_reg_number', 'gender', 'dob', 'address']

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            
            if field_name in teacher_only:
                field.widget.attrs['data-role'] = 'teacher'
            elif field_name in student_only:
                field.widget.attrs['data-role'] = 'student'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        student_reg = cleaned_data.get("student_reg_number")
        teacher_id = cleaned_data.get("teacher_id")
        qualification = cleaned_data.get("qualification")
        gender = cleaned_data.get("gender")
        dob = cleaned_data.get("dob")
        address = cleaned_data.get("address")

        if role == "student":
            if not student_reg:
                self.add_error('student_reg_number', "Student Registration Number is required for students.")
            if not gender:
                self.add_error('gender', "Gender is required for students.")
            if not dob:
                self.add_error('dob', "Date of Birth is required for students.")
            if not address:
                self.add_error('address', "Address is required for students.")
        
        if role == "teacher" and not teacher_id:
            self.add_error('teacher_id', "Teacher ID is required for teachers.")
        
        if role == "teacher" and not qualification:
            self.add_error('qualification', "Qualification is required for teachers.")
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('full_name')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        
        # Save the profile information
        profile = user.profile
        profile.phone_number = self.cleaned_data.get('phone_number')
        profile.role = self.cleaned_data.get('role')
        if profile.role == 'student':
            profile.registration_id = self.cleaned_data.get('student_reg_number')
            profile.gender = self.cleaned_data.get('gender')
            profile.dob = self.cleaned_data.get('dob')
            profile.address = self.cleaned_data.get('address')
        elif profile.role == 'teacher':
            profile.registration_id = self.cleaned_data.get('teacher_id')
            profile.qualification = self.cleaned_data.get('qualification')
            profile.trained_at = self.cleaned_data.get('trained_at')
        
        if commit:
            profile.save()

        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'qualification', 'trained_at', 'image', 'gender', 'dob', 'address']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'image':
                field.widget.attrs['class'] = 'form-control'
        
        # Specific widget updates
        self.fields['image'].widget.attrs['class'] = 'form-control-file mt-2'
        self.fields['dob'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['address'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})