from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=10, choices=[('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')], blank=True)
    registration_id = models.CharField(max_length=50, blank=True, help_text='Student Registration No. or Teacher ID')
    qualification = models.CharField(max_length=100, blank=True)
    trained_at = models.CharField(max_length=100, blank=True, verbose_name="Training Institute")

    # Student-specific fields
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    address = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Check if the object is already in the database to get the old instance
        if self.pk:
            try:
                old_instance = Profile.objects.get(pk=self.pk)
                # Check if the image has been changed and if the old image is not the default one
                if old_instance.image != self.image and old_instance.image.name != 'profile_pics/default.jpg':
                    old_instance.image.delete(save=False)
            except Profile.DoesNotExist:
                pass  # Should not happen if self.pk is set, but good practice to handle
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()