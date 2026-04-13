from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from .models import Exam
from apps.questions.models import Question
from apps.results.models import Result
from .forms import ExamForm
from apps.questions.forms import QuestionForm

@login_required(login_url='login')
def create_exam(request):
    # Authorize teacher access
    is_teacher = hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'
    if not is_teacher and not request.user.is_superuser:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, f"Exam '{exam.name}' created successfully!")
            return redirect('teacher_dashboard')
    else:
        form = ExamForm()

    context = {
        'form': form
    }
    return render(request, 'teacher/create_exam.html', context)

@login_required(login_url='login')
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Authorization: Only the creator or an admin can edit
    if exam.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f"Exam '{exam.name}' updated successfully!")
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = ExamForm(instance=exam)

    context = {
        'form': form,
        'exam': exam,
        'edit_mode': True
    }
    return render(request, 'teacher/create_exam.html', context)

@login_required(login_url='login')
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Ensure only the creator or admin can manage the exam
    if exam.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('teacher_dashboard')
        
    questions = exam.questions.all()
    context = {
        'exam': exam,
        'questions': questions
    }
    return render(request, 'teacher/exam_detail.html', context)

@login_required(login_url='login')
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if exam.created_by != request.user and not request.user.is_superuser:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            messages.success(request, "Question added successfully!")
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = QuestionForm()

    context = {'form': form, 'exam': exam, 'title': 'Add Question'}
    return render(request, 'teacher/question_form.html', context)

@login_required(login_url='login')
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.exam.created_by != request.user and not request.user.is_superuser:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully!")
            return redirect('exams:exam_detail', exam_id=question.exam.id)
    else:
        form = QuestionForm(instance=question)

    context = {'form': form, 'exam': question.exam, 'title': 'Edit Question'}
    return render(request, 'teacher/question_form.html', context)

@login_required(login_url='login')
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.exam.id
    if question.exam.created_by == request.user or request.user.is_superuser:
        question.delete()
        messages.success(request, "Question deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this question.")
    
    return redirect('exams:exam_detail', exam_id=exam_id)

@login_required(login_url='login')
def exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if exam.created_by != request.user and not request.user.is_superuser:
        return redirect('teacher_dashboard')
        
    # Fetch results for this exam
    results = Result.objects.filter(exam=exam).select_related('student')
    
    context = {
        'exam': exam,
        'results': results
    }
    return render(request, 'teacher/exam_results.html', context)

@login_required(login_url='login')
def publish_result(request, result_id):
    # Logic for teacher to toggle publication status
    result = get_object_or_404(Result, id=result_id)
    if result.exam.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect('teacher_dashboard')
    
    result.is_published = not result.is_published
    result.save()
    return redirect('exams:exam_results', exam_id=result.exam.id)

@login_required(login_url='login')
def teacher_question_bank(request):
    is_teacher = hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'
    if not is_teacher and not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    query = request.GET.get('q')
    # Order by subject for regrouping in the template
    questions = Question.objects.filter(exam__created_by=request.user).select_related('exam').order_by('exam__subject', 'text')

    if query:
        questions = questions.filter(text__icontains=query)

    total_questions = questions.count()

    context = {
        'questions': questions,
        'total_questions': total_questions
    }
    return render(request, 'teacher/question_bank.html', context)

@login_required(login_url='login')
def teacher_submissions(request):
    is_teacher = hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'
    if not is_teacher and not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    results = Result.objects.filter(exam__created_by=request.user).select_related('student', 'exam').order_by('-date_taken')
    return render(request, 'teacher/submissions.html', {'results': results})