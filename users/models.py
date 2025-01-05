from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        # Check if the user is a superuser
        if self.is_superuser:
            self.role = 'admin'  # Ensure superusers always have the admin role
            super().save(*args, **kwargs)

            # Assign the superuser to both 'admin' and 'student' groups
            admin_group, _ = Group.objects.get_or_create(name='admin')
            student_group, _ = Group.objects.get_or_create(name='student')
            self.groups.add(admin_group, student_group)

            return
        
        # Save the user instance first
        super().save(*args, **kwargs)

        # Remove the user from all existing groups
        self.groups.clear()

        # Assign the user to the group corresponding to their role
        if self.role not in ['admin', 'student']:
            raise ValueError("Invalid role")
        if self.role:
            group, _ = Group.objects.get_or_create(name=self.role)
            self.groups.add(group)

        # Set is_staff to True for admins and False otherwise
        self.is_staff = self.role == 'admin'

        # Save the changes to the user instance
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email