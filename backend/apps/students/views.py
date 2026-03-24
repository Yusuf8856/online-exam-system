from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
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
    completed_exams_count = all_results.count()
    
    # Upcoming exams are those with a future date that the student has NOT taken yet
    taken_exam_ids = all_results.values_list('exam_id', flat=True)
    upcoming_exams = Exam.objects.filter(date__gte=timezone.now().date()).exclude(id__in=taken_exam_ids).order_by('date', 'start_time')
    
    # Calculate average score
    total_score = 0
    total_possible_marks = 0
    for res in all_results:
        total_score += res.score
        total_possible_marks += res.total_marks
    
    average_score = 0
    if total_possible_marks > 0:
        average_score = (total_score / total_possible_marks) * 100

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
def take_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all().order_by('?') # Randomize question order

    if Result.objects.filter(student=request.user, exam=exam).exists():
        messages.warning(request, "You have already completed this exam.")
        return redirect('students:available_exams')

    if request.method == 'POST':
        score = 0
        total_marks = 0
        for question in questions:
            total_marks += question.marks
            selected_answer = request.POST.get(f'question_{question.id}')
            if selected_answer and selected_answer.strip() == question.answer.strip():
                score += question.marks
        
        new_result = Result.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            total_marks=total_marks
        )
        messages.success(request, f"You have successfully submitted the exam '{exam.name}'.")
        # Redirect to the result page using the new result's ID to avoid race conditions
        return redirect('students:exam_result', result_id=new_result.id)

    context = {'exam': exam, 'questions': questions}
    return render(request, 'student/take_exam.html', context)

@login_required(login_url='login')
def exam_result_view(request, result_id):
    result = get_object_or_404(Result, id=result_id, student=request.user)
    
    # If not published, pass a flag to the template to show a "Pending" message
    # unless it's an immediate redirect from the exam (optional logic, but typically reports need approval)
    # For this implementation, we allow the basic view but hide details if strict approval is needed,
    # or we rely on the template to show "Awaiting Approval".
    
    percentage = 0
    if result.total_marks > 0:
        percentage = (result.score / result.total_marks) * 100
    
    context = {'result': result, 'percentage': percentage}
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