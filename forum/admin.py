from django.contrib import admin
from .models import Department
from .models import Course
from .models import Prof
from .models import Post

admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Prof)
admin.site.register(Post)

# Register your models here.
