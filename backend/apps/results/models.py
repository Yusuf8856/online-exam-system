from django.db import models
from django.contrib.auth.models import User
from apps.exams.models import Exam

class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    score = models.FloatField()
    total_marks = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False, help_text="Determines if the student can view the detailed report")

    def __str__(self):
        return f"{self.student.username} - {self.exam.name}"