import os
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from apps.resumes.models import Candidate, Application


class ResumeView:
    # Function to get all candidates
    @staticmethod
    def get_candidates(request):
        candidates = Candidate.objects.all().values('first_name', 'last_name', 'email')
        data = []
        for c in candidates:
            data.append({
                'name': f"{c['first_name']} {c['last_name']}",
                'email': c['email'],
            })
        columns = [
            {'key': 'name', 'label': 'Name'},
            {'key': 'email', 'label': 'Email'},
            {
                'label': 'Action',
                'type': 'action',
                'actions': [
                    {
                        'url_name': '',  
                        'label': 'View',
                        'class': 'btn-primary'
                    }
                ]
            }
        ]
        return render(request, 'resumes/candidates/candidates.html', {'columns': columns, 'data': data})

    # Function to get a specific candidate by ID
    @staticmethod
    def get_candidate(request, candidate_id):
        candidate = Candidate.objects.filter(id=candidate_id).values(
            'first_name', 'last_name', 'email', 'phone', 'linkedin_profile', 'nationality', 'notice_period', 'expected_salary'
        ).first()
        if not candidate:
            return render(request, 'resumes/candidate_not_found.html') # TODO: need to create 404 template
        
        data = {
            'name': f"{candidate['first_name']} {candidate['last_name']}",
            'email': candidate['email'],
            'phone': candidate['phone'],
            'linkedin_profile': candidate['linkedin_profile'],
            'nationality': candidate['nationality'],
            'notice_period': candidate['notice_period'],
            'expected_salary': candidate['expected_salary'],
        }
        
        return render(request, 'resumes/candidates/candidate-detail.html', {'data': data})

    # Function to get all applications
    @staticmethod
    def get_applications(request):
        applications = Application.objects.all().values(
            'id', 'candidate__first_name', 'candidate__last_name', 'job__title', 'status'
        )
        data = []
        for app in applications:
            data.append({
                'id': app['id'],
                'candidate_name': f"{app['candidate__first_name']} {app['candidate__last_name']}",
                'job_title': app['job__title'],
                'status': app['status'],
            })
        
        columns = [
            {'key': 'id', 'label': 'ID'},
            {'key': 'candidate_name', 'label': 'Candidate Name'},
            {'key': 'job_title', 'label': 'Job Title'},
            {'key': 'status', 'label': 'Status'},
            {
                'label': 'Action',
                'type': 'action',
                'actions': [
                    {
                        'url_name': '',  
                        'label': 'View',
                        'class': 'btn-primary'
                    },
                    {
                        'url_name': '',  
                        'label': 'Set Interview',
                        'class': 'btn-secondary'
                    }
                ]
            }
        ]

        return render(request, 'resumes/applications/applications.html', {'columns': columns, 'data': data})
    
    # Function to render the application form
    @staticmethod
    def apply(request):
        fieldConfig = [
            {
                'type': 'text',
                'name': 'first_name',
                'id': 'first_name',
                'label': 'First Name',
                'placeholder': 'Enter first name',
                'required': True,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'text',
                'name': 'last_name',
                'id': 'last_name',
                'label': 'Last Name',
                'placeholder': 'Enter last name',
                'required': True,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'email',
                'name': 'email',
                'id': 'email',
                'label': 'Email',
                'placeholder': 'Enter email',
                'required': True,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'text',
                'name': 'phone',
                'id': 'phone',
                'label': 'Phone Number',
                'placeholder': 'Enter phone number',
                'required': False,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'text',
                'name': 'linkedin_profile',
                'id': 'linkedin_profile',
                'label': 'LinkedIn Profile',
                'placeholder': '',
                'required': False,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'text',
                'name': 'nationality',
                'id': 'nationality',
                'label': 'Nationality',
                'placeholder': 'Enter nationality',
                'required': False,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'text',
                'name': 'notice_period',
                'id': 'notice_period',
                'label': 'Notice Period',
                'placeholder': 'Enter notice period',
                'required': False,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'number',
                'name': 'expected_salary',
                'id': 'expected_salary',
                'label': 'Expected Salary',
                'placeholder': 'Enter expected salary',
                'required': False,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
            {
                'type': 'file',
                'name': 'resume_file',
                'id': 'resume_file',
                'label': 'Upload Resume/CV',
                'placeholder': '',
                'required': True,
                'disabled': False,
                'value': '',
                'help_text': '',
            },
        ]

        if request.method == 'POST':
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            linkedin_profile = request.POST.get('linkedin_profile')
            nationality = request.POST.get('nationality')
            resume_file = request.FILES.get('resume_file')

            # Save candidate (get or create by email)
            candidate, created = Candidate.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'linkedin_profile': linkedin_profile,
                    'nationality': nationality,
                }
            )
            # If candidate exists, update fields
            if not created:
                candidate.first_name = first_name
                candidate.last_name = last_name
                candidate.phone = phone
                candidate.linkedin_profile = linkedin_profile
                candidate.nationality = nationality
                candidate.save()
            
            # Create a unique temp folder for the candidate
            job_id = 1  # Hardcoded as requested
            temp_dir = os.path.join(settings.BASE_DIR, 'tmp', f'job_{job_id}', f'candidate_{candidate.email}')
            os.makedirs(temp_dir, exist_ok=True)
            temp_file_path = os.path.join(temp_dir, resume_file.name)

            # Save file to the candidate's temp folder
            with open(temp_file_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)

            # Save application (job_id=1, resume_file path)
            Application.objects.create(
                candidate=candidate,
                job_id=1,  # Hardcoded as requested
                company_name="N/A",  # Placeholder, adjust as needed
                status='applied',
                resume_file=temp_file_path,
                application_date=timezone.now(),
            )

            return render(request, 'resumes/upload-success.html', {'file_path': temp_file_path})

        # Render the application form for GET
        return render(
            request,
            'resumes/applications/application-form.html',
            {
                'fieldConfig': fieldConfig,
                'action': '/resumes/apply',  # Updated form action URL
                'method': 'POST',
                'submit_label': 'Apply',
                'enctype': 'multipart/form-data',
            }
        )
    
   