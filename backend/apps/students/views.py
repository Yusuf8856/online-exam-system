from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from apps.exams.models import Exam
from apps.results.models import Result

@login_required(login_url='login')
def student_dashboard(request):
    student = request.user
    
    # Authorization
    is_student = hasattr(student, 'profile') and student.profile.role == 'student'
    if not is_student:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    # Fetch data
    all_results = Result.objects.filter(student=student)
    # Only count exams that have been officially graded/published as "Completed"
    completed_exams_count = all_results.filter(is_published=True).count()
    
    # Upcoming exams are those with a future date that the student has NOT taken yet
    taken_exam_ids = all_results.values_list('exam_id', flat=True)
    upcoming_exams = Exam.objects.filter(date__gte=timezone.now().date()).exclude(id__in=taken_exam_ids).order_by('date', 'start_time')
    
    # Only include published results in the average score calculation
    # This prevents unpublished/pending results from affecting the student's dashboard stats
    stats = all_results.filter(is_published=True).aggregate(
        total_earned=Sum('score'),
        total_possible=Sum('total_marks')
    )

    total_possible = stats.get('total_possible') or 0
    average_score = (stats.get('total_earned') or 0) / total_possible * 100 if total_possible > 0 else 0
    
    context = {
        'completed_exams': completed_exams_count,
        'upcoming_exams_count': upcoming_exams.count(),
        'average_score': f"{average_score:.2f}",
        'upcoming_exams': upcoming_exams[:5],
        'recent_results': all_results.order_by('-date_taken')[:5]
    }
    return render(request, 'student/dashboard.html', context)

@login_required(login_url='login')
def available_exams_view(request):
    exams = Exam.objects.filter(date__gte=timezone.now().date()).order_by('date', 'start_time')
    taken_exam_ids = Result.objects.filter(student=request.user).values_list('exam_id', flat=True)
    context = {
        'exams': exams,
        'taken_exam_ids': taken_exam_ids
    }
    return render(request, 'student/available_exams.html', context)

@login_required(login_url='login')
def exam_guidelines_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Authorization: Ensure student is logged in and exam is available
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')
    
    # Check if the exam date has passed or if the student has already taken it
    if exam.date < timezone.now().date() or Result.objects.filter(student=request.user, exam=exam).exists():
        messages.warning(request, "This exam is no longer available or you have already completed it.")
        return redirect('students:available_exams')

    # Calculate total possible marks for this specific exam
    total_marks = exam.questions.aggregate(total=Sum('marks'))['total'] or 0

    context = {
        'exam': exam,
        'total_marks': total_marks
    }
    return render(request, 'student/exam_guidelines.html', context)


@login_required(login_url='login')
def take_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all().order_by('?') # Randomize question order

    if Result.objects.filter(student=request.user, exam=exam).exists():
        messages.warning(request, "You have already completed this exam.")
        return redirect('students:available_exams')

    # Record start time in session if not present to track duration
    session_key = f'exam_start_{exam.id}'
    if session_key not in request.session:
        request.session[session_key] = timezone.now().isoformat()

    # Calculate remaining time for the frontend timer
    start_time = timezone.datetime.fromisoformat(request.session.get(session_key))
    elapsed_seconds = (timezone.now() - start_time).total_seconds()
    total_seconds = exam.duration * 60
    time_left = max(0, int(total_seconds - elapsed_seconds))

    if request.method == 'POST':
        # Server-side duration validation
        start_time_str = request.session.get(session_key)
        if start_time_str:
            start_time = timezone.datetime.fromisoformat(start_time_str)
            elapsed_time = (timezone.now() - start_time).total_seconds() / 60
            # Allow a small buffer (e.g., 2 minutes) for network latency
            if elapsed_time > (exam.duration + 2):
                messages.error(request, "Submission rejected: Time limit exceeded.")
                return redirect('students:available_exams')

        score = 0
        total_marks = 0
        for question in questions:
            total_marks += question.marks
            selected_answer = request.POST.get(f'question_{question.id}', '').strip()
            if selected_answer == question.answer.strip():
                score += question.marks
        
        new_result = Result.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            total_marks=total_marks,
            is_published=False # Explicitly ensure it is pending approval
        )
        
        # Clean up session
        del request.session[session_key]
        
        messages.success(request, f"Exam '{exam.name}' submitted successfully. Your results will be available once approved by the teacher.")
        # Redirect to the result page using the new result's ID to avoid race conditions
        return redirect('students:exam_result', result_id=new_result.id)

    context = {
        'exam': exam, 
        'questions': questions,
        'time_left': time_left
    }
    return render(request, 'student/take_exam.html', context)

@login_required(login_url='login')
def exam_result_view(request, result_id):
    result = get_object_or_404(Result, id=result_id, student=request.user)
    
    percentage = 0
    # Only calculate percentage if the result has been published by the teacher
    if result.is_published and result.total_marks > 0:
        percentage = (result.score / result.total_marks) * 100
    
    context = {
        'result': result, 
        'percentage': percentage,
        'is_published': result.is_published
    }
    return render(request, 'student/exam_result.html', context)

@login_required(login_url='login')
def result_report_view(request, result_id):
    result = get_object_or_404(Result, id=result_id, student=request.user)
    
    if not result.is_published:
        messages.warning(request, "This report has not been published yet.")
        return redirect('students:my_results')

    percentage = 0
    if result.total_marks > 0:
        percentage = (result.score / result.total_marks) * 100

    grade = 'F'
    status = 'Fail'
    if percentage >= 90:
        grade = 'A+'
        status = 'Pass'
    elif percentage >= 80:
        grade = 'A'
        status = 'Pass'
    elif percentage >= 70:
        grade = 'B'
        status = 'Pass'
    elif percentage >= 60:
        grade = 'C'
        status = 'Pass'
    elif percentage >= 50:
        grade = 'D'
        status = 'Pass'

    context = {
        'result': result, 
        'percentage': percentage,
        'grade': grade,
        'status': status,
        'student': request.user
    }
    return render(request, 'student/report_card.html', context)

@login_required(login_url='login')
def my_results_view(request):
    results = Result.objects.filter(student=request.user).select_related('exam').order_by('-date_taken')
    context = {'results': results}
    return render(request, 'student/my_results.html', context)