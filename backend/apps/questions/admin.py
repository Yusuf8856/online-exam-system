from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'marks', 'answer')
    list_filter = ('exam',)
    search_fields = ('text', 'answer')
