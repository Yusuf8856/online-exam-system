from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    total_marks = models.IntegerField(default=100)
    instructions = models.TextField(blank=True, null=True, help_text="Enter specific rules or guidelines for this exam.")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams')

    @property
    def open_time(self):
        """
        Returns a datetime.time object representing the time when the exam page can be opened (20 minutes before start_time).
        """
        from datetime import datetime, timedelta
        dt = datetime.combine(self.date, self.start_time) - timedelta(minutes=20)
        return dt.time()

    def __str__(self):
        return self.name