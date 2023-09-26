from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='users_avatar', default='default.jpg')
    bio = models.TextField()

    def __str__(self):
        return self.user.username

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)




