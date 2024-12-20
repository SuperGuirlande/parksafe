from project import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    birth_date = models.DateField(_('Date de naissance'))
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    waiting_gains = models.DecimalField(_('Total des gains'), decimal_places=2, max_digits=10, default=0.00, blank=True)
    total_gains = models.DecimalField(_('Total des gains'), decimal_places=2, max_digits=10, default=0.00, blank=True)

    # AJOUT ULTERIEUR
    phone = models.CharField(_('phone number'), max_length=16, blank=True, null=True, unique=True)
    profil_pic = models.ImageField(_('Profile Picture'), upload_to="user/profilpics/", default="user/profilpics/default-avatar.png")

    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date']

    @property
    def average_rating(self):
        """
        Calcule la moyenne des étoiles pour cet utilisateur
        Retourne 0 si aucun avis
        """
        average = self.avis_recus.aggregate(Avg('stars'))['stars__avg']
        return average or 0

    def __str__(self):
        return f"{self.id} : {self.first_name} {self.last_name} - {self.email}"