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

# Create your views here.
def home(request):
    return render(request, "home.html")

def login_view(request):
    if request.method == 'POST':
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
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'auth/register.html', {'form': form})

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
    recent_exams_qs = Exam.objects.order_by('-date')[:5]
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

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_exams': total_exams,
        'active_exams': active_exams,
        'recent_exams': recent_exams,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required(login_url='login')
def manage_students(request):
    students = User.objects.filter(profile__role='student')
    context = {
        'students': students
    }
    return render(request, 'admin_panel/manage_students.html', context)

@login_required(login_url='login')
def manage_teachers(request):
    teachers = User.objects.filter(profile__role='teacher')
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
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    role = user.profile.role
    user.delete()
    messages.success(request, f"User deleted successfully.")
    return redirect('manage_teachers' if role == 'teacher' else 'manage_students')

@login_required(login_url='login')
def delete_exam_admin(request, exam_id):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    from apps.exams.models import Exam
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
    active_exams_count = teacher_exams.filter(date__gte=date.today()).count()

    # NOTE: Enrolled students count requires a relationship between teachers and students
    # (e.g., via course enrollment). This is currently a placeholder.
    students_count = 0

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
        'recent_exams': recent_exams,
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
        # Authorization: Only admin can view other profiles directly via ID
        if not request.user.is_superuser and request.user.id != profile_owner.id:
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

    # Security: Only allow admins to edit others. Non-admins can only edit themselves.
    if not request.user.is_superuser and request.user.id != user_to_edit.id:
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
            return redirect('manage_teachers' if user_to_edit.profile.role == 'teacher' else 'manage_students') if request.user.is_superuser else redirect('my_profile')
    else:
        u_form = UserUpdateForm(instance=user_to_edit)
        p_form = ProfileUpdateForm(instance=user_to_edit.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'editing_user': user_to_edit
    }
    return render(request, 'teacher/edit_profile.html', context)
