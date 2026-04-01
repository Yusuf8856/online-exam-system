from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('create/', views.create_exam, name='create_exam'),
    path('question-bank/', views.teacher_question_bank, name='teacher_question_bank'),
    path('submissions/', views.teacher_submissions, name='teacher_submissions'),
    path('<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('<int:exam_id>/results/', views.exam_results, name='exam_results'),
    path('<int:exam_id>/add-question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('<int:result_id>/publish/', views.publish_result, name='publish_result'),
    path('<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),


]