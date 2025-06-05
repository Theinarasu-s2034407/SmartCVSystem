from django.core.management.base import BaseCommand
from apps.resumes.models import Candidate
from apps.jobposts.models import JobPost

class Command(BaseCommand):
    help = 'Seed initial data for candidates and job posts'

    def handle(self, *args, **kwargs):
        # Seed Candidates
        candidates = [
            Candidate(
                first_name="Jane Doe",
                last_name="Jane Doe",
                email="janedoe@example.com",
                phone="0123456789",
                linkedin_profile="https://linkedin.com/in/janedoe",
                nationality="Malaysian",
                notice_period="1 month",
                expected_salary=5000.00
            ),
            Candidate(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="0198765432",
                linkedin_profile="https://linkedin.com/in/johndoe",
                nationality="Malaysian",
                notice_period="Immediate",
                expected_salary=6000.00
            ),
        ]
        Candidate.objects.bulk_create(candidates, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Seeded candidates.'))

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