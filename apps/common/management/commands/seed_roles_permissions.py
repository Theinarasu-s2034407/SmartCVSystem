from django.core.management.base import BaseCommand
from django.db import transaction, connection
from apps.authx.models import Role, Permission, RolePermission

class Command(BaseCommand):
    help = "Seed Roles, Permissions, and RolePermission mappings"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # 0) Truncate all three tables (use raw SQL for truncate and reset auto-increment)
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE RolePermission;")
            cursor.execute("TRUNCATE TABLE Permission;")
            cursor.execute("TRUNCATE TABLE Roles;")
            cursor.execute("ALTER TABLE RolePermission AUTO_INCREMENT = 1;")
            cursor.execute("ALTER TABLE Permission AUTO_INCREMENT = 1;")
            cursor.execute("ALTER TABLE Roles AUTO_INCREMENT = 1;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # 1) Insert Roles
        roles = [
            {"name": "candidate", "desc": "Job seeker / candidate"},
            {"name": "recruiter", "desc": "Individual recruiter"},
            {"name": "Company HR", "desc": "Company HR user"},
        ]
        role_objs = {}
        for r in roles:
            obj = Role.objects.create(role_name=r["name"], role_description=r["desc"])
            role_objs[r["name"]] = obj

        # 2) Insert Permissions
        permissions = [
            # Candidate perms
            ("job.detailview",      "See job details"),
            ("job.search",          "Search and filter job listings"),
            ("job.apply",           "Apply to a job"),
            ("job.save",            "Save/bookmark a job for later"),
            ("application.view_own","View your submitted applications"),
            ("resume.upload",       "Upload a new resume file"),
            ("resume.select",       "Select one resume as active profile"),
            ("profile.change",      "Edit your own user profile"),
            ("auth.password_change","Change your password while logged in"),
            ("auth.password_reset", "Request a password reset email"),
            # Recruiter + Company HR perms
            ("job.view",            "See all job listings"),
            ("job.create",          "Post a new job opening"),
            ("job.update",          "Edit a job you have posted"),
            ("job.delete",          "Delete or archive a job you posted"),
            ("application.view_all","View all applicants for your jobs"),
            # Company HR only
            ("company.view",        "View your company profile"),
            ("company.update",      "Update your company profile"),
            ("talent.onboard",      "Onboard a candidate to your company"),
        ]
        perm_objs = {}
        for codename, desc in permissions:
            obj = Permission.objects.create(permission_name=codename, Description=desc)
            perm_objs[codename] = obj

        # 3) Map Permissions → Roles
        candidate_perms = [
            'job.detailview','job.search','job.apply','job.save',
            'application.view_own','resume.upload','resume.select',
            'profile.change','auth.password_change','auth.password_reset'
        ]
        recruiter_perms = [
            'job.view','job.create','job.update','job.delete',
            'application.view_all','auth.password_change','auth.password_reset'
        ]
        companyhr_perms = [
            'job.view','job.create','job.update','job.delete',
            'application.view_all','company.view','company.update','talent.onboard',
            'auth.password_change','auth.password_reset'
        ]

        for codename in candidate_perms:
            RolePermission.objects.create(
                role=role_objs["candidate"],
                permission=perm_objs[codename]
            )
        for codename in recruiter_perms:
            RolePermission.objects.create(
                role=role_objs["recruiter"],
                permission=perm_objs[codename]
            )
        for codename in companyhr_perms:
            RolePermission.objects.create(
                role=role_objs["Company HR"],
                permission=perm_objs[codename]
            )

        self.stdout.write(self.style.SUCCESS("Seeded Roles, Permissions, and RolePermission mappings!"))