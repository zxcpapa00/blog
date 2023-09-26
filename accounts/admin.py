from django.contrib import admin
from .models import Profile
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Profile)
class ProfileAdmin(SummernoteModelAdmin):
    summernote_fields = ('bio', )
    fields = ('user', 'avatar', 'bio')



