from django.db import models
from apps.exams.models import Exam

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    text = models.TextField(verbose_name="Question Text")
    marks = models.PositiveIntegerField(default=1)
    option1 = models.CharField(max_length=255, verbose_name="Option A")
    option2 = models.CharField(max_length=255, verbose_name="Option B")
    option3 = models.CharField(max_length=255, verbose_name="Option C")
    option4 = models.CharField(max_length=255, verbose_name="Option D")
    answer = models.CharField(max_length=255, help_text="Enter the correct option text exactly", verbose_name="Correct Answer")

    def __str__(self):
        return self.text