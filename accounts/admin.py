from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group

# Register your models here.
admin.site.site_header = 'Zfunds Admin'
admin.site.site_title = 'Zfunds Admin Portal'
admin.site.index_title = 'Welcome to Zfunds Admin Portal'

class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mobile_number",
        "name",
        "user_type",
    )
    fields = (
        "mobile_number",
        "name",
        "user_type",
    )

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)