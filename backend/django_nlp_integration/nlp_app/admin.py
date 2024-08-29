from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Add any other fields you want to display in the admin

# Check if the permission exists before creating it
content_type = ContentType.objects.get_for_model(YourModel)
if not Permission.objects.filter(codename='can_view_model', content_type=content_type).exists():
    Permission.objects.create(
        codename='can_view_model',
        name='Can View Model',
        content_type=content_type,
    )
