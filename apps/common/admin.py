from django.contrib import admin

# Register your models here.
from apps.authx.models    import User, Role, Permission, RolePermission
from apps.resumes.models import Candidate, Application
from apps.jobposts.models import JobPost


admin.site.register(User)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(Candidate)
admin.site.register(Application)
admin.site.register(JobPost)