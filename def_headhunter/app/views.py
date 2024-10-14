from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .decorators import IsOwnerResumeOrVacancy, IsStaff, IsOwnerResumeOrStaff
from .models import Vacancy, Resume, Request
from .forms import ResumeForm, VacancyForm

def start_page(request):
    return render(request, 'app/start_page.html')
@login_required
def vacancy_list(request):
    user_requests = Request.objects.filter(resume__user=request.user).values_list('vacancy_id', flat=True)
    vacancies = Vacancy.objects.exclude(id__in=user_requests)

    search_query = request.GET.get('search', '')
    if search_query:
        vacancies = vacancies.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(
            skills__name__icontains=search_query)).distinct()

    return render(request, 'app/vacancy_list.html', {'vacancies': vacancies})
@login_required
def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    return render(request, 'app/vacancy_detail.html', {'vacancy': vacancy})
@IsStaff
def resume_create(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            form.save_m2m()
            return redirect('profile_page')
    else:
        form = ResumeForm()
    return render(request, 'app/resume_form.html', {'form': form})
@IsOwnerResumeOrVacancy
def resume_update(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('profile_page')
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'app/resume_form.html', {'form': form})
@IsOwnerResumeOrVacancy
def resume_delete(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == 'POST':
        resume.delete()
        return redirect('profile_page')
    return render(request, 'app/resume_confirm_delete.html', {'resume': resume})
@login_required
def vacancy_create(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.created_by = request.user
            vacancy.save()
            form.save_m2m()
            return redirect('vacancy_detail', vacancy_id=vacancy.id)
    else:
        form = VacancyForm()
    return render(request, 'app/vacancy_form.html', {'form': form})
@IsOwnerResumeOrVacancy
def vacancy_update(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, created_by=request.user)
    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            form.save()
            return redirect('vacancy_list')
    else:
        form = VacancyForm(instance=vacancy)
    return render(request, 'app/vacancy_form.html', {'form': form})
@IsOwnerResumeOrVacancy
def vacancy_delete(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, created_by=request.user)
    if request.method == 'POST':
        vacancy.delete()
        return redirect('vacancy_list')
    return render(request, 'app/vacancy_confirm_delete.html', {'vacancy': vacancy})
@IsStaff
def resume_list(request):
    resumes = Resume.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        resumes = resumes.filter(Q(name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(
            skills__name__icontains=search_query)).distinct()
    return render(request, 'app/resume_list.html', {'resumes': resumes})
@IsOwnerResumeOrStaff
def resume_detail(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    return render(request, 'app/resume_detail.html', {'resume': resume})

