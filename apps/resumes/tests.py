from django.test import TestCase, Client
from django.urls import reverse
from apps.resumes.models import Candidate, Application
from apps.jobposts.models import JobPost

class ResumeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.candidate = Candidate.objects.create(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            phone="0123456789",
            linkedin_profile="https://linkedin.com/in/testuser",
            nationality="Testland",
            notice_period="1 month",
            expected_salary=5000.00
        )
        self.job = JobPost.objects.create(
            title="Software Engineer",
            description="Develop stuff",
            level="entry",
            skills="Python, Django",
            salary_range="4000-6000",
            status="open"
        )
        self.application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            company_name="Test Company",
            status="applied"
        )

    def test_get_candidates(self):
        response = self.client.get(reverse('candidates_list'))  # Update with your actual URL name
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")
        self.assertTemplateUsed(response, 'resumes/candidates/candidates.html')

    def test_get_candidate_detail(self):
        response = self.client.get(reverse('candidate_detail', args=[self.candidate.id]))  # Update with your actual URL name
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")
        self.assertTemplateUsed(response, 'resumes/candidates/candidate-detail.html')

    def test_get_candidate_not_found(self):
        response = self.client.get(reverse('candidate_detail', args=[9999]))  # Non-existent ID
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/candidate_not_found.html')

    def test_get_applications(self):
        response = self.client.get(reverse('applications_list'))  # Update with your actual URL name
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")
        self.assertContains(response, "Software Engineer")
        self.assertTemplateUsed(response, 'resumes/applications/applications.html')