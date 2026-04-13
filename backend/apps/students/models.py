from django.db import models
from django.contrib.auth.models import User
from apps.exams.models import Exam

class ViolationLog(models.Model):
	student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='violation_logs')
	exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='violation_logs')
	violation_type = models.CharField(max_length=100)
	details = models.TextField(blank=True)
	count = models.PositiveIntegerField(default=1)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.student.username} - {self.exam.name} - {self.violation_type} ({self.timestamp})"
