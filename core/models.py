from django.db import models

# base classes required to overwrite default django user models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    """Manager for Users. Creating a manager to handle the model because as default Django
    requires Username and Password Field to create a user but we've changed this to Email field"""
    
    def create_user(self, email, first_name, last_name, password=None):
        """Create a new user"""
        if not email:
            raise ValueError('User must have an email address')

        # normalizing email for standarization
        email = self.normalize_email(email)  
        # creating user model that user manager is representing
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        # Encrypting password using method of AbstractBaseUserClass
        user.set_password(password)
        # self._db to save to any database 
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, first_name, last_name, password):
        """create and save new superuser with given details"""
        user = self.create_user(email, first_name, last_name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=125)
    last_name = models.CharField(max_length=125)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        """Retrieve full name of user"""
        return self.first_name+" "+self.last_name

    def get_short_name(self):
        """Retrieve short name of user"""
        return self.first_name
    
    def ___str__(self):
        """Return string representation of our user"""
        return self.email
