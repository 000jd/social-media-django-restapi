from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
import random
import string


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, name, is_admin=False, password=None):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            is_admin=is_admin
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, is_admin=True, password=None):
        """
        Creates and saves a Superuser with the given email, name and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            name=name,
            is_admin=is_admin
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    # Fields from auth_user entity
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=255)
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.CharField(max_length=100, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups'  # Change to a unique name
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions'  # Change to a unique name
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=['name', 'is_admin']

    class Meta:
        indexes = [
            models.Index(fields=['name']),  # Index on frequently queried field
            models.Index(fields=['created_at']),  # Index on created_at
            models.Index(fields=['updated_at']),  # Index on updated_at
        ]

    def generate_avatar(self):
        # Generate an avatar based on the first two characters of the user's name
        if len(self.name) >= 2:
            return self.name[:2].upper()
        else:
            return self.name.upper()

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.name

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
class Profile(models.Model):
    # Fields from users_profile entity
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=1500)
    avatar = models.CharField(max_length=2, default='', editable=False)
    bio = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['is_verified']), 
        ]

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.user.avatar
        super().save(*args, **kwargs)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)