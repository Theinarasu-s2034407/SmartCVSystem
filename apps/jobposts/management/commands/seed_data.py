from django.core.management.base import BaseCommand
from apps.jobposts.models import JobPost

class Command(BaseCommand):
    help = 'Seed initial data for candidates and job posts'

    def handle(self, *args, **kwargs):
        # Seed JobPosts
        jobposts = [
            JobPost(
                title="Software Engineer",
                description="Develop and maintain web applications.",
                level="entry",
                skills="Python, Django, JavaScript",
                salary_range="4000-6000",
                status="open"
            ),
            JobPost(
                title="DevOps Engineer",
                description="Manage CI/CD pipelines and cloud infrastructure.",
                level="mid",
                skills="Docker, AWS, Nginx, Shell",
                salary_range="6000-9000",
                status="open"
            ),
        ]
        JobPost.objects.bulk_create(jobposts, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Seeded job posts.'))