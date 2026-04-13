from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('exams/', views.available_exams_view, name='available_exams'),
    path('my-results/', views.my_results_view, name='my_results'),
    path('exam/<int:exam_id>/take/', views.take_exam_view, name='take_exam'),
    path('exam/result/<int:result_id>/', views.exam_result_view, name='exam_result'),
    path('exam/report/<int:result_id>/', views.result_report_view, name='result_report'),
    path('exam/<int:exam_id>/guidelines/', views.exam_guidelines_view, name='exam_guidelines'),

]