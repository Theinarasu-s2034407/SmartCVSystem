import os
import shutil
import boto3
import fitz
import urllib.parse
import io
import re
import logging
import re
import datetime
from botocore.exceptions import ClientError
from django.shortcuts           import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from apps.authx.auth_utils      import login_required_custom
from ..authx.auth_utils import SessionRequiredMixin
from ..authx.models     import User, UsersRole
from django.contrib.auth.hashers import check_password, make_password
from django.contrib             import messages
from apps.authx.auth_utils import SessionRequiredMixin
from django.contrib.auth.forms          import PasswordChangeForm
from apps.authx.models    import UserProfile
from .forms               import ProfileForm
from apps.authx.models          import (
    User, UsersRole, UserProfile,
    Company, CompanyUser
)
from .forms import ResumeForm
from .models import ResumeFile, ParsedData 
from apps.jobposts.models import JobPost, UserJob
from django.utils import timezone
from django.conf import settings


def extract_resume_info_from_s3(bucket_name, key, aws_access_key=None, aws_secret_key=None, region='us-east-1'):
    fallback_resume_data = {
        "skills": "",
        "education_level": "Unknown",
        "experience_level": "unknown"
    }
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        s3_object = s3.get_object(Bucket=bucket_name, Key=key)
        file_stream = io.BytesIO(s3_object['Body'].read())
    except Exception as e:
        logging.error(f"[S3 Read Error] {e}")
        return fallback_resume_data

    try:
        doc = fitz.open(stream=file_stream, filetype="pdf")
        full_text = "\n".join(page.get_text() for page in doc)
        full_text_lower = full_text.lower()
    except Exception as e:
        logging.error(f"[PDF Parse Error] {e}")
        return fallback_resume_data

    resume_data = {
        "skills": "",
        "education_level": "Unknown",
        "experience_level": "unknown"
    }

    # --- Skill Extraction ---
    skill_keywords = [
        'javascript', 'python', 'java', 'php', 'react', 'vue', 'html', 'css',
        'node', 'typescript', 'mongodb', 'mysql', 'aws', 'firebase', 'laravel',
        'django', 'flask', 'fastapi', 'bootstrap', 'git', 'docker', 'redis'
    ]
    found_skills = {kw.capitalize() for kw in skill_keywords if re.search(rf'\b{kw}\b', full_text_lower)}
    resume_data["skills"] = ", ".join(sorted(found_skills))

    # --- Education Extraction ---
    if "bachelor" in full_text_lower:
        resume_data["education_level"] = "Bachelor's Degree"
    elif "master" in full_text_lower:
        resume_data["education_level"] = "Master's Degree"
    elif "diploma" in full_text_lower:
        resume_data["education_level"] = "Diploma"
    elif "phd" in full_text_lower or "doctor of philosophy" in full_text_lower:
        resume_data["education_level"] = "PhD"

    # --- Experience Extraction ---
    # Patterns for date ranges: MM/YYYY - MM/YYYY, MM/YYYY - Present, Month YYYY - Month YYYY, etc.
    date_patterns = [
        r'(\d{2}/\d{4})\s*[-–]\s*(\d{2}/\d{4}|present)',
        r'([A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*([A-Za-z]{3,9}\s+\d{4}|present)',
        r'(\d{2}-\d{4})\s*[-–]\s*(\d{2}-\d{4}|present)'
    ]
    matches = []
    for pattern in date_patterns:
        matches += re.findall(pattern, full_text, re.IGNORECASE)

    # Helper to parse date strings
    def parse_date(date_str):
        date_str = date_str.strip().replace('-', '/')
        if date_str.lower() == 'present':
            return datetime.datetime.now()
        for fmt in ("%m/%Y", "%b %Y", "%B %Y", "%m-%Y"):
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    # Collect all periods as (start, end)
    periods = []
    for match in matches:
        start_str, end_str = match
        start = parse_date(start_str)
        end = parse_date(end_str)
        if start and end and end >= start:
            periods.append((start, end))

    # Merge overlapping/adjacent periods
    periods.sort()
    merged = []
    for period in periods:
        if not merged:
            merged.append(period)
        else:
            last_start, last_end = merged[-1]
            curr_start, curr_end = period
            if curr_start <= last_end + datetime.timedelta(days=31):  # allow 1 month gap
                merged[-1] = (last_start, max(last_end, curr_end))
            else:
                merged.append(period)

    # Calculate total experience in years
    total_months = 0
    for start, end in merged:
        months = (end.year - start.year) * 12 + (end.month - start.month)
        if months > 0:
            total_months += months
    total_years = total_months / 12

    # Assign experience level
    if total_years >= 6:
        resume_data["experience_level"] = "senior"
    elif total_years >= 3:
        resume_data["experience_level"] = "mid"
    elif total_years > 0:
        resume_data["experience_level"] = "junior"
    else:
        # Fallback to keyword-based logic if no date ranges found
        experience_patterns = [
            (r"([6-9]|[1-9][0-9]+)\s*(\+)?\s*(years|yrs)", "senior"),
            (r"(3|4)\s*(years|yrs)", "mid"),
            (r"(0|1|2)\s*(years|yrs)", "junior"),
            (r"\bintern(ship)?\b", "junior")
        ]
        for pattern, level in experience_patterns:
            if re.search(pattern, full_text_lower):
                resume_data["experience_level"] = level
                break

    return resume_data

class DetailView(View):
    def get(self, request):
        return render(request, "profile/detailView.html")
class ManageResumesView(SessionRequiredMixin,View):

    def get(self, request):
        user_id = request.session['user_id']
        resume_form = ResumeForm()
        resumes     = ResumeFile.objects.filter(UserID=user_id).order_by('-UploadedAt')
        return render(request, 'profile/resume.html', {
            'resume_form': resume_form,
            'resumes': resumes,
        })

    def post(self, request):
        user_id = request.session['user_id']
        action  = request.POST.get('action')
        print(f"Action: {action}")

        if action == 'upload':
            form = ResumeForm(request.POST, request.FILES)
            if form.is_valid():
                rf = form.save(commit=False)
                rf.UserID_id = user_id 
                rf.Status = 'Uploaded'
                rf.save()

                local_file_path = rf.FilePath.path
                if not settings.DEBUG:
                    # S3 logic
                    with open(local_file_path, 'rb') as resume_file:
                        s3 = boto3.client(
                            's3', 
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name=settings.AWS_S3_REGION_NAME
                        )
                        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                        s3_path = f"resumes/{user_id}/{os.path.basename(local_file_path)}"
                        s3.upload_fileobj(resume_file, bucket_name, s3_path, ExtraArgs={'ContentType': 'application/pdf'})
                        s3_url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_path}"
                        rf.FilePath = s3_url
                        rf.save()
                        # Delete the local file
                        if os.path.exists(local_file_path):
                            os.remove(local_file_path)
                        # Delete the media folder if empty
                        media_root = settings.MEDIA_ROOT
                        if os.path.exists(media_root) and not os.listdir(media_root):
                            shutil.rmtree(media_root)
                        messages.success(request, "Resume uploaded")
                else:
                    messages.success(request, "Resume uploaded.")
            else:
                 return render(request, 'profile/resume.html', {
                    'resume_form': form
                })
        elif action == 'select':
            sel_id = request.POST.get('selected_id')
            # clear previous
            ResumeFile.objects.filter(UserID=user_id, IsSelected=True).update(IsSelected=False)
            # mark new
            ResumeFile.objects.filter(pk=sel_id, UserID=user_id).update(IsSelected=True)
            messages.success(request, "Selected resume updated.")
    
        elif action == 'delete':
            sel_id = request.POST.get('selected_id')
            if sel_id:
                try:
                    resume = ResumeFile.objects.get(pk=sel_id, UserID=user_id)
                     # Delete associated parsed data if exists
                    ParsedData.objects.filter(ResumeID=resume).delete()
                    # Delete only the file in S3 based on id and fileName.pdf, keep the resumes folder
                    if not settings.DEBUG and resume.FilePath and str(resume.FilePath).startswith("http"):
                        s3 = boto3.client(
                            's3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name=settings.AWS_S3_REGION_NAME,
                        )
                        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

                        # Parse the S3 key from the URL
                        parsed_url = urllib.parse.urlparse(str(resume.FilePath))
                        # parsed_url.path: /resumes/1/NurzatilimaniBintiMuhamadAhwanResume.pdf
                        s3_key = parsed_url.path.lstrip('/')  # Remove leading slash

                        try:
                            s3.head_object(Bucket=bucket_name, Key=s3_key)
                            s3.delete_object(Bucket=bucket_name, Key=s3_key)
                        except ClientError as e:
                            if e.response['Error']['Code'] == "404":
                                # Object does not exist, nothing to delete
                                pass
                            else:
                                raise

                    # Optionally, delete local file if exists (for local debug)
                    elif resume.FilePath and hasattr(resume.FilePath, 'path') and os.path.exists(resume.FilePath.path):
                        os.remove(resume.FilePath.path)
                        media_root = settings.MEDIA_ROOT
                        if os.path.exists(media_root) and not os.listdir(media_root):
                            shutil.rmtree(media_root)

                    resume.delete()
                    messages.success(request, "Selected resume deleted.")
                except ResumeFile.DoesNotExist:
                    messages.error(request, "Resume not found.")
                except Exception as e:
                    messages.error(request, f"Error deleting resume: {e}")
            else:
                messages.error(request, "No resume selected for deletion.")

        elif action == 'extract':
            sel_id = request.POST.get('selected_id')
            if sel_id:
                try:
                    resume = ResumeFile.objects.get(pk=sel_id, UserID=user_id)
                    # Only proceed if the file is stored in S3
                    if resume.FilePath and str(resume.FilePath).startswith("http"):
                        parsed_url = urllib.parse.urlparse(str(resume.FilePath))
                        s3_key = parsed_url.path.lstrip('/')  # e.g. resumes/1/filename.pdf
                        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                        aws_access_key = settings.AWS_ACCESS_KEY_ID
                        aws_secret_key = settings.AWS_SECRET_ACCESS_KEY
                        region = getattr(settings, "AWS_S3_REGION_NAME", "us-east-1")
                        resume_info = extract_resume_info_from_s3(
                            bucket_name, s3_key, aws_access_key, aws_secret_key, region
                        )
                        # Store the extracted data in ParsedData model only if not exists
                        if not ParsedData.objects.filter(ResumeID=resume).exists():
                            ParsedData.objects.create(
                                ResumeID=resume,
                                Data=resume_info
                            )
                            messages.success(request, "Resume extracted and data saved successfully.")
                        else:
                            messages.info(request, "Parsed data for this resume already exists.")
                    else:
                        messages.error(request, "Resume file is not available in S3 for extraction.")
                except ResumeFile.DoesNotExist:
                    messages.error(request, "Resume not found.")
                except Exception as e:
                    messages.error(request, f"Error extracting resume: {e}")
            else:
                messages.error(request, "No resume selected for extraction.")

        return redirect('profiles:resume')
    
class DashboardView(SessionRequiredMixin, View):
    """
    Shows the logged-in user’s info and roles.
    """
    def get(self, request):
        user_id = request.session['user_id']
        user    = User.objects.get(users_id=user_id)

        # Fetch all Roles assigned to this user
        roles = [ur.role.role_name.lower() for ur in UsersRole.objects.filter(user_id=user_id).select_related('role')]

        context = {
            'user':  user,
            'roles': roles,
        }
        print(roles)
        if 'candidate' in roles:
            # Candidate metrics
            resumes_qs     = ResumeFile.objects.filter(UserID_id=user_id)
            context.update({
                'resume_count':  resumes_qs.count(),
                'has_active':    resumes_qs.filter(IsSelected=True).exists(),
                'applied_count': UserJob.objects.filter(User_id=user_id, IsApplied=True).count(),
                'saved_count':   UserJob.objects.filter(User_id=user_id, IsSaved=True).count(),
            })

        if 'company hr' in roles or 'recruiter' in roles:
            # Company HR / Recruiter metrics
            context.update({
                'total_jobs':   JobPost.objects.filter(Recruiter_id=user_id).count(),
                'expired_jobs': JobPost.objects.filter(
                    Recruiter_id=user_id,
                    ApplicationDeadline__lt=timezone.now()
                ).count(),
                'total_apps':   UserJob.objects.filter(
                    JobPost__Recruiter_id=user_id,
                    IsApplied=True
                ).count(),
            })
        print(context)
        return render(request, 'dashboard.html', context)

class ChangePasswordView(SessionRequiredMixin,View):
    def get(self, request):
        user = User.objects.get(users_id=request.session['user_id'])
        form = PasswordChangeForm(user=user)
        return render(request, 'profile/password_change_form.html', {'form': form})

    def post(self, request):
        user = User.objects.get(users_id=request.session['user_id'])
        form = PasswordChangeForm(user=user, data=request.POST)

        if not form.is_valid():
            # errors will show in the template
            return render(request, 'profile/password_change_form.html', {'form': form})

        # This will hash and save the new password for us:
        form.save()
        messages.success(request, "Your password has been updated.")
        return redirect('profiles:dashboard')

class ProfileEditView(SessionRequiredMixin,View):
    def get(self, request):
        user_id = request.session['user_id']
        # load user & profile
        profile = UserProfile.objects.get(user_id=user_id)
        # detect company role
        role_names = UsersRole.objects.filter(user_id=user_id) \
                                     .values_list('role__role_name', flat=True)
        print(role_names)
        print(role_names)
        has_company_role = any(r.lower() in ('company hr','recruiter') for r in role_names)
        print(has_company_role)
        # load or init company
        company = None
        if has_company_role:
            cu = CompanyUser.objects.filter(user_id=user_id).first()
            if cu:
                company = cu.company
            else:
                company = None
        print(company)
        # build initial data
        initial = {
            'phone':    profile.phone,
            'location': profile.location,
        }
        if company:
            initial.update({
                'company_name':    company.name,
                'company_address': company.address,
                'company_website': company.website,
            })

        form = ProfileForm(initial=initial)
        return render(request, 'profile/profile_edit.html', {
            'form':             form,
            'profile':          profile,
            'has_company_role': has_company_role,
        })

    def post(self, request):
        user_id = request.session['user_id']
        profile = UserProfile.objects.get(user_id=user_id)

        # detect company role same as above
        role_names = UsersRole.objects.filter(user_id=user_id) \
                                     .values_list('role__role_name', flat=True)
        has_company_role = any(r.lower() in ('company hr','recruiter') for r in role_names)

        form = ProfileForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'profile/profile_edit.html', {
                'form':             form,
                'profile':          profile,
                'has_company_role': has_company_role,
            })

        # save profile fields
        profile.phone    = form.cleaned_data['phone']
        profile.location = form.cleaned_data['location']
        avatar = form.cleaned_data.get('avatar')
        if avatar:
            profile.avatar = avatar
        profile.save()

        # save company if needed
        if has_company_role:
            # find or create company & link
            cu = CompanyUser.objects.filter(user_id=user_id).first()
            if cu:
                company = cu.company
            else:
                company = Company.objects.create(
                    name    = form.cleaned_data['company_name'],
                    address = form.cleaned_data['company_address'],
                    website = form.cleaned_data['company_website'],
                )
                CompanyUser.objects.create(
                    user_id    = user_id,
                    company_id = company.id,
                )

            # update existing company
            company.name    = form.cleaned_data['company_name']
            company.address = form.cleaned_data['company_address']
            company.website = form.cleaned_data['company_website']
            company.save()

        messages.success(request, "Your profile has been updated.")
        return redirect('profiles:profile_edit')
