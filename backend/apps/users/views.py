from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from .models import Profile
from apps.exams.models import Exam
from apps.questions.models import Question
from apps.results.models import Result
from datetime import date
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import threading
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


# Create your views here.
def home(request):
    return render(request, "home.html")

def login_view(request):
    if request.method == 'POST':
        
         # 🔹 CAPTCHA validation
        user_input = request.POST.get('captchaInput')
        generated = request.POST.get('generatedCaptcha')

        if user_input != generated:
            messages.error(request, 'Invalid CAPTCHA')
            return redirect('login')
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Determine the user's actual role from the database
            actual_role = None
            if hasattr(user, 'profile'):
                actual_role = user.profile.role

            # Superusers are treated as Admins
            if user.is_superuser:
                actual_role = 'admin'

            # Validate that the selected role matches the user's actual role
            if selected_role and selected_role != actual_role:
                messages.error(request, f"Role mismatch. You are registered as '{actual_role}'.")
                logout(request)
                return redirect('login')

            # Redirect based on the validated role
            if actual_role == 'student':
                return redirect('students:dashboard')
            elif actual_role == 'teacher':
                return redirect('teacher_dashboard')
            elif actual_role == 'admin':
                return redirect('admin_dashboard')
            
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            username = form.cleaned_data.get('username')
            email = user.email

            try:
                print("🚀 Sending email via SendGrid API...")

                message = Mail(
                    from_email='yusufali2235@gmail.com',  # verified sender
                    to_emails=email,
                    subject='Welcome to Digital Assessment Platform',
                    html_content=f"""
                        <h2>Welcome {username} 🎉</h2>
                        <p>Your account has been created successfully.</p>
                        <p>You can now login and start your exams.</p>
                    """
                )
                print("API KEY:", os.getenv('EMAIL_HOST_PASSWORD'))
                sg = SendGridAPIClient(os.getenv('EMAIL_HOST_PASSWORD'))
                response = sg.send(message)

                print("✅ Email sent successfully:", response.status_code)

            except Exception as e:
                print("❌ Email error:", str(e))

            messages.success(request, f'Account created successfully for {username}!')
            return redirect('login')

    else:
        form = SignUpForm()

    return render(request, 'auth/register.html', {'form': form})

# ✅ FORGOT PASSWORD FUNCTIONALITY

def forgot_password_view(request):
    """Send password reset link to user's email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')
            
            # Send email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f5f5f5;
                        margin: 0;
                        padding: 20px;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: #ffffff;
                        padding: 40px 20px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 600;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .reset-button {{
                        display: inline-block;
                        background-color: #667eea;
                        color: #ffffff;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 4px;
                        font-weight: 600;
                        margin: 20px 0;
                    }}
                    .reset-button:hover {{
                        background-color: #764ba2;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffc107;
                        padding: 15px;
                        border-radius: 4px;
                        margin: 20px 0;
                        color: #856404;
                        font-size: 14px;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px 30px;
                        border-top: 1px solid #e9ecef;
                        text-align: center;
                        color: #666666;
                        font-size: 12px;
                    }}
                    .code-box {{
                        background-color: #f0f4ff;
                        border-left: 4px solid #667eea;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 4px;
                        word-break: break-all;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                        <p style="margin: 10px 0 0 0; font-size: 14px;">Reset your Digital Assessment Platform password</p>
                    </div>
                    
                    <div class="content">
                        <p>Hi <strong>{user.username}</strong>,</p>
                        <p>We received a request to reset your password for the Digital Assessment Platform. Click the button below to create a new password.</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_url}" class="reset-button">🔗 Reset Password</a>
                        </div>
                        
                        <p style="font-size: 14px; color: #666;">Or copy and paste this link in your browser:</p>
                        <div class="code-box">
                            {reset_url}
                        </div>
                        
                        <div class="warning">
                            <strong>⏰ Important:</strong> This password reset link will expire in 24 hours. If you didn't request a password reset, please ignore this email or contact support immediately.
                        </div>
                        
                        <div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; border-radius: 4px; margin: 20px 0;">
                            <p style="margin: 0; color: #0d47a1; font-size: 14px;">
                                <strong>🔒 Security Tip:</strong> We will never ask you for your password via email. Always reset your password through our secure platform.
                            </p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p style="margin: 0 0 10px 0;">
                            © 2026 Digital Assessment Platform. All rights reserved.
                        </p>
                        <p style="margin: 0;">
                            This is an automated email. Please do not reply directly to this address.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            email_message = EmailMessage(
                subject='🔐 Password Reset Request - Digital Assessment Platform',
                body=html_content,
                from_email='yusufali2235@gmail.com',
                to=[email],
            )
            email_message.content_subtype = 'html'
            email_message.send(fail_silently=False)
            
            messages.success(request, '📧 Password reset link has been sent to your email. Please check your inbox and follow the instructions.')
            return redirect('password_reset_done')
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            messages.success(request, '📧 If an account exists with this email, password reset instructions have been sent.')
            return redirect('password_reset_done')
        except Exception as e:
            print(f"Error sending reset email: {e}")
            messages.error(request, '❌ Error sending password reset email. Please try again later.')
    
    return render(request, 'auth/forgot_password.html')


def password_reset_confirm(request, uidb64, token):
    """Verify token and allow user to set new password"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Verify token
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password2:
                if password1 != password2:
                    messages.error(request, '❌ Passwords do not match!')
                    return render(request, 'auth/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
                
                if len(password1) < 6:
                    messages.error(request, '❌ Password must be at least 6 characters long!')
                    return render(request, 'auth/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
                
                # Set new password
                user.set_password(password1)
                user.save()
                
                messages.success(request, '✅ Password reset successfully! You can now log in with your new password.')
                return redirect('password_reset_complete')
            else:
                messages.error(request, '❌ Please fill in all password fields!')
        
        return render(request, 'auth/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, '❌ Invalid or expired password reset link!')
        return redirect('forgot_password')


def password_reset_done(request):
    """Show confirmation that reset email was sent"""
    return render(request, 'auth/password_reset_done.html')


def password_reset_complete(request):
    """Show confirmation that password was reset"""
    return render(request, 'auth/password_reset_complete.html')

@login_required(login_url='login')
def admin_dashboard(request):
    # Authorization check
    is_admin = (hasattr(request.user, 'profile') and request.user.profile.role == 'admin') or request.user.is_superuser
    if not is_admin:
        messages.error(request, "You are not authorized to view the admin dashboard.")
        return redirect('home')

    # Fetch real-time statistics from the database
    total_students = User.objects.filter(profile__role='student').count()
    total_teachers = User.objects.filter(profile__role='teacher').count()
    total_exams = Exam.objects.count()
    active_exams = Exam.objects.filter(date__gte=date.today()).count()

    # Fetch recent exams and determine status dynamically
    recent_exams_qs = Exam.objects.select_related('created_by').order_by('-date')[:5]
    recent_exams = []
    for exam in recent_exams_qs:
        status = 'Completed'
        if exam.date > date.today():
            status = 'Scheduled'
        elif exam.date == date.today():
            status = 'Active'
        
        recent_exams.append({
            'name': exam.name,
            'instructor': exam.created_by.get_full_name() or exam.created_by.username,
            'date': exam.date,
            'status': status
        })

    # Fetch recent student registrations
    recent_students = User.objects.filter(profile__role='student').select_related('profile').order_by('-date_joined')[:5]

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_exams': total_exams,
        'active_exams': active_exams,
        'recent_exams': recent_exams,
        'recent_students': recent_students,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required(login_url='login')
def manage_students(request):
    # Authorization: Allow both admins and teachers to view student registrations
    is_authorized = (hasattr(request.user, 'profile') and request.user.profile.role in ['admin', 'teacher']) or request.user.is_superuser
    if not is_authorized:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    students = User.objects.filter(profile__role='student').select_related('profile').order_by('-date_joined')
    context = {
        'students': students
    }
    return render(request, 'admin_panel/manage_students.html', context)

@login_required(login_url='login')
def manage_teachers(request):
    teachers = User.objects.filter(profile__role='teacher').select_related('profile').order_by('-date_joined')
    context = {
        'teachers': teachers
    }
    return render(request, 'admin_panel/manage_teachers.html', context)

@login_required(login_url='login')
def manage_exams(request):
    exams = Exam.objects.all()
    context = {
        'exams': exams
    }
    return render(request, 'admin_panel/manage_exams.html', context)

@login_required(login_url='login')
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    role = user_to_delete.profile.role

    # Authorization: Admins can delete anyone. Teachers can only delete students.
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    is_teacher = hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'
    
    if not (is_admin or (is_teacher and role == 'student')):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    user_to_delete.delete()
    messages.success(request, f"User deleted successfully.")
    return redirect('manage_teachers' if role == 'teacher' else 'manage_students')

@login_required(login_url='login')
def add_student_view(request):
    # Authorization: Allow admins and teachers
    is_authorized = (hasattr(request.user, 'profile') and request.user.profile.role in ['admin', 'teacher']) or request.user.is_superuser
    if not is_authorized:
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # If a teacher is adding, enforce the student role for the new account
            if not request.user.is_superuser and request.user.profile.role == 'teacher':
                if form.cleaned_data.get('role') != 'student':
                    messages.error(request, "Teachers can only add students.")
                    return render(request, 'auth/register.html', {'form': form, 'title': 'Add Student'})
            
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect('manage_students')
    else:
        form = SignUpForm(initial={'role': 'student'})
    return render(request, 'auth/register.html', {'form': form, 'title': 'Add Student'})

@login_required(login_url='login')
def delete_exam_admin(request, exam_id):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    exam = get_object_or_404(Exam, id=exam_id)
    exam.delete()
    messages.success(request, "Exam deleted successfully.")
    return redirect('manage_exams')

@login_required(login_url='login')
def question_bank(request):
    query = request.GET.get('q')
    questions = Question.objects.select_related('exam').order_by('exam__subject')
    
    if query:
        questions = questions.filter(text__icontains=query)
    
    total_questions = questions.count()
    
    context = {
        'questions': questions,
        'total_questions': total_questions
    }
    return render(request, 'admin_panel/question_bank.html', context)

@login_required(login_url='login')
def view_results(request):
    # Placeholder for results view
    return render(request, 'admin_panel/results.html')

@login_required(login_url='login')
def admin_settings(request):
    # Placeholder for settings view
    return render(request, 'admin_panel/settings.html')

@login_required(login_url='login')
def teacher_dashboard(request):
    # Authorize teacher access
    is_teacher = hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'
    if not is_teacher and not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    teacher = request.user
    
    # Fetch data for the dashboard
    teacher_exams = Exam.objects.filter(created_by=teacher)
    my_exams_count = teacher_exams.count()
    
    # Count results waiting for approval for this teacher's exams
    pending_approvals_count = Result.objects.filter(exam__created_by=teacher, is_published=False).count()
    active_exams_count = teacher_exams.filter(date__gte=date.today()).count()

    students_count = User.objects.filter(profile__role='student').count()
    
    # Fetch recent students for the teacher dashboard
    recent_students = User.objects.filter(profile__role='student').select_related('profile').order_by('-date_joined')[:5]

    # Prepare recent exams list with dynamic status
    recent_exams_qs = teacher_exams.order_by('-date')[:5]
    recent_exams = []
    for exam in recent_exams_qs:
        if exam.date > date.today():
            status = 'Scheduled'
        elif exam.date == date.today():
            status = 'Active'
        else:
            status = 'Completed'
        
        recent_exams.append({
            'name': exam.name,
            'subject': exam.subject,
            'date': exam.date,
            'status': status,
            'id': exam.id
        })

    context = {
        'my_exams_count': my_exams_count,
        'active_exams_count': active_exams_count,
        'students_count': students_count,
        'pending_approvals_count': pending_approvals_count,
        'recent_exams': recent_exams,
        'recent_students': recent_students,
    }
    return render(request, 'teacher/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def profile_view(request, user_id=None):
    if user_id:
        # If user_id is provided, fetch that user's profile
        profile_owner = get_object_or_404(User, id=user_id)
        
        # Authorization: Admins can view all. Teachers can view students. Users can view themselves.
        is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
        is_teacher = hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'
        target_is_student = hasattr(profile_owner, 'profile') and profile_owner.profile.role == 'student'

        if not is_admin and request.user.id != profile_owner.id and not (is_teacher and target_is_student):
            messages.error(request, "You are not authorized to view this profile.")
            return redirect('home')
    else:
        # If no user_id, show the logged-in user's profile
        profile_owner = request.user
    
    return render(request, 'teacher/profile.html', {'user': profile_owner})

@login_required(login_url='login')
def edit_profile_view(request, user_id):
    # Fetch the user we want to edit
    user_to_edit = get_object_or_404(User, id=user_id)

    # Authorization: Admins can edit all. Teachers can edit students. Users can edit themselves.
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    is_teacher = hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'
    target_is_student = hasattr(user_to_edit, 'profile') and user_to_edit.profile.role == 'student'

    if not is_admin and request.user.id != user_to_edit.id and not (is_teacher and target_is_student):
        messages.error(request, "You are not authorized to edit this profile.")
        return redirect('home')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user_to_edit)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=user_to_edit.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Profile for {user_to_edit.username} has been updated!')
            
            if is_admin or is_teacher:
                return redirect('manage_teachers' if user_to_edit.profile.role == 'teacher' else 'manage_students')
            return redirect('my_profile')
    else:
        u_form = UserUpdateForm(instance=user_to_edit)
        p_form = ProfileUpdateForm(instance=user_to_edit.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'editing_user': user_to_edit
    }
    return render(request, 'teacher/edit_profile.html', context)

from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='your_email@gmail.com',
            password='admin123'
        )
        return HttpResponse("✅ Superuser created successfully!")
    return HttpResponse("⚠️ Superuser already exists!")
