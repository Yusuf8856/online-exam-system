from django.contrib import admin
from .models import Exam
from apps.questions.models import Question

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3  # Provides 3 empty slots to add questions immediately

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'date', 'duration', 'total_marks', 'created_by')
    list_filter = ('subject', 'date', 'created_by')
    search_fields = ('name', 'subject')
    date_hierarchy = 'date'
    inlines = [QuestionInline]
