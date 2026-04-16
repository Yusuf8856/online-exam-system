from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from datetime import date
import json

from .utils import extract_text_from_pdf, parse_mcqs_from_text, extract_text_from_scanned_pdf
from .models import Exam
from apps.questions.models import Question
from apps.results.models import Result
from .forms import ExamForm
from apps.questions.forms import QuestionForm
from django.core.mail import send_mail

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
@require_POST
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    # Only a teacher or superuser can delete
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if user_role == 'teacher' or request.user.is_superuser:
        exam.delete()
        messages.success(request, "Exam deleted successfully.")
        return redirect('teacher_dashboard')
    else:
        messages.error(request, "You do not have permission to delete this exam.")
        return redirect('exams:exam_detail', exam_id=exam_id)

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
        # ✅ SEND EMAIL ONLY WHEN PUBLISHED
    if result.is_published:
        student = result.student
        user_email = student.email

        percentage = (result.score / result.total_marks) * 100 if result.total_marks > 0 else 0

        if user_email:
            send_mail(
                'Your Exam Result is Published',
                f"""Dear {student.first_name or student.username},

                    Your result for the exam "{result.exam.name}" has been published.

                    Marks Obtained: {result.score}
                    Total Marks: {result.total_marks}
                    Percentage: {percentage:.2f}%

                    You can now log in and view your detailed result.

                    Best Regards,  
                    Online Examination System
                    """,
                                    'samee89mohammed@gmail.com',
                                    [user_email],
                                    fail_silently=False,
            )
        else:
            print("WARNING: No email for student")

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

@login_required(login_url='login')
def upload_questions_pdf(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # 🔐 Authorization
    if exam.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('teacher_dashboard')

    # -------------------------------
    # 📌 HANDLE POST REQUEST
    # -------------------------------
    if request.method == 'POST':

        # =============================
        # 🔹 STEP 1: PARSE PDF
        # =============================
        if request.FILES.get('pdf_file'):
            pdf_file = request.FILES['pdf_file']

            # Validate file type
            if not pdf_file.name.endswith('.pdf'):
                return JsonResponse(
                    {'error': 'Invalid file format. Please upload a PDF.'},
                    status=400
                )

            try:
                # Reset pointer
                pdf_file.seek(0)

                # Try normal extraction
                raw_text = extract_text_from_pdf(pdf_file)

                # Auto fallback to OCR if needed
                if len(raw_text.strip()) < 50:
                    pdf_file.seek(0)
                    raw_text = extract_text_from_scanned_pdf(pdf_file)

                # Clean + normalize text
                from .utils import clean_ocr_text, normalize_text
                raw_text = clean_ocr_text(raw_text)
                raw_text = normalize_text(raw_text)

                # Debug (important)
                print("🔍 TEXT PREVIEW:\n", raw_text[:1000])

                # Parse MCQs
                parsed_questions = parse_mcqs_from_text(raw_text)

                if not parsed_questions:
                    return JsonResponse(
                        {'error': 'No questions found. Check PDF format.'},
                        status=400
                    )

                return JsonResponse({
                    'questions': parsed_questions,
                    'count': len(parsed_questions)
                })

            except Exception as e:
                return JsonResponse(
                    {'error': f"Processing Error: {str(e)}"},
                    status=500
                )

        # =============================
        # 🔹 STEP 2: SAVE QUESTIONS
        # =============================
        elif request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                questions_data = data.get('questions', [])

                valid_questions = []

                # Validate questions
                for q in questions_data:
                    if all([
                        q.get('question'),
                        q.get('option_a'),
                        q.get('option_b'),
                        q.get('option_c'),
                        q.get('option_d'),
                        q.get('correct_answer') in ['A', 'B', 'C', 'D']
                    ]):
                        valid_questions.append(q)

                if not valid_questions:
                    return JsonResponse(
                        {'error': 'No valid questions to save.'},
                        status=400
                    )

                # Bulk insert
                with transaction.atomic():
                    Question.objects.bulk_create([
                        Question(
                            exam=exam,
                            text=q['question'],
                            option1=q['option_a'],
                            option2=q['option_b'],
                            option3=q['option_c'],
                            option4=q['option_d'],
                            answer=q['correct_answer'],
                            marks=q.get('marks', 1)
                        )
                        for q in valid_questions
                    ])

                messages.success(
                    request,
                    f"Successfully imported {len(valid_questions)} questions."
                )

                return JsonResponse({
                    'status': 'success',
                    'count': len(valid_questions),
                    'redirect_url': reverse('exams:exam_detail', args=[exam.id])
                })

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    # -------------------------------
    # 📌 GET REQUEST (PAGE LOAD)
    # -------------------------------
    return render(request, 'teacher/upload_questions.html', {'exam': exam})