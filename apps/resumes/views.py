from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ResumeForm
from . import models
from .models import Resume
from .forms import ResumeFilterForm


class ResumeSearchView(ListView):
    model = Resume
    template_name = 'resumes/list.html'
    paginate_by = 10
    context_object_name = 'resumes'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ResumeFilterForm(self.request.GET)

        if form.is_valid():

            skills = form.cleaned_data['skills']
            tags = form.cleaned_data['tags']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            keyword = form.cleaned_data['keyword']

            if skills:
                query = Q()
                for skill in skills:
                    query |= Q(skills__icontains=skill)
                queryset = queryset.filter(query)

            if tags:
                queryset = queryset.filter(tags__contains=tags)

            if start_date and end_date:
                queryset = queryset.filter(
                    upload_date__date__range=(start_date, end_date)
                )
            elif start_date:
                queryset = queryset.filter(
                    upload_date__date__gte=start_date
                )
            elif end_date:
                queryset = queryset.filter(
                    upload_date__date__lte=end_date
                )

            if keyword:
                queryset = queryset.filter(
                    Q(skills__icontains=keyword) |
                    Q(tags__icontains=keyword)
                )

        return queryset.select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ResumeFilterForm(self.request.GET)
        return context

class ResumeListView(ListView):
    model = Resume
    template_name = 'resumes/list.html'
    paginate_by = 10
    context_object_name = 'resumes'
    def get_queryset(self):
        queryset = models.Resume.objects.all()
        return queryset


@login_required
def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            form.save_m2m()


            if tags := form.cleaned_data.get('tags'):
                resume.tags = ','.join([t.strip() for t in tags.split(',')])
                resume.save()

            return redirect('dashboard')
    else:
        form = ResumeForm()

    return render(request, 'resumes/add_resume.html', {'form': form})


from django.shortcuts import render, redirect
from .models import Skill
from .forms import SkillForm


def skill_management(request):
    skills = Skill.objects.all().order_by('name')

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('resumes:add_skill')
    else:
        form = SkillForm()

    return render(request, 'resumes/add_new_skill.html', {
        'skills': skills,
        'form': form
    })