from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import DSAQuestionForm ,UserAnswerForm
from .models import DSAQuestion, UserAnswer
import openai
import google.generativeai as genai
import requests
from django.conf import settings

# Create your views here.
def index(request):
    
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    
    return render(request, 'about.html')

# login function
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/dashboard/')
            else:
                return redirect('/user/dashboard/')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to access this page.")
    return render(request, 'dashboard/index.html')

# register function
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                messages.success(request, 'User created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def editor(request):
    return render(request, 'editor.html')

# def admin_dashboard(request):
#     return render(request, 'dashboard/index.html')
@login_required(login_url='login')
def add_questions(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        difficulty = request.POST.get('difficulty')
        topic = request.POST.get('topic')
        answer = request.POST.get('answer')
        DSAQuestion.objects.create(
            question_text=question_text,
            difficulty=difficulty,
            topic=topic,
            answer=answer
        )
        messages.success(request, 'Question added successfully!')
        return redirect('view_questions')
    return render(request, 'dashboard/add_questions.html')

@login_required(login_url='login')
def edit_questions(request, question_id):
    question = get_object_or_404(DSAQuestion, id=question_id)
    if request.method == 'POST':
        question.question_text = request.POST.get('question_text')
        question.difficulty = request.POST.get('difficulty')
        question.topic = request.POST.get('topic')
        question.answer = request.POST.get('answer')
        question.save()
        messages.success(request, 'Question updated successfully!')
        return redirect('view_questions')
    return render(request, 'dashboard/edit_questions.html', {'question': question})

@login_required(login_url='login')
def delete_questions(request, question_id):
    question = get_object_or_404(DSAQuestion, id=question_id)
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('view_questions')

@login_required(login_url='login')
def view_questions(request):
    questions = DSAQuestion.objects.all()
    return render(request, 'dashboard/view_questions.html', {'questions': questions})

@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            messages.success(request, 'Profile updated successfully.')

    return render(request, 'dashboard/profile.html')

@login_required(login_url='login')
def user_dashboard(request):
    if request.user.is_superuser:
        return HttpResponseForbidden("Admin cannot access user dashboard.")
    user = request.user
    answers = UserAnswer.objects.filter(user=user)
    total = answers.count()
    passed = answers.filter(is_correct=True).count()
    failed = answers.filter(is_correct=False).count()
    return render(request, 'user/user_dashboard.html', {
        'answers': answers,
        'total': total,
        'passed': passed,
        'failed': failed,
    })

def check_with_openai(user_code, question_title):
    try:
        openai.api_key = settings.OPENAI_API_KEY
        prompt = f"Does the following Python code correctly solve the problem: '{question_title}'?\n\n{user_code}\n\nAnswer with only 'Yes' or 'No'."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip().lower()
        return "Pass" if "yes" in answer else "Fail"
    except Exception as e:
        return None

def check_with_gemini(user_code, question_title):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Does the following Python code correctly solve the problem: '{question_title}'?\n\n{user_code}\n\nAnswer with only 'Yes' or 'No'."
        response = model.generate_content(prompt)
        answer = response.text.strip().lower()
        return "Pass" if "yes" in answer else "Fail"
    except Exception as e:
        return None
    
def check_with_deepseek(user_code, question_title):
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"}
        data = {
            "model": "deepseek-coder",
            "messages": [
                {"role": "user", "content": f"Does the following Python code correctly solve the problem: '{question_title}'?\n\n{user_code}\n\nAnswer with only 'Yes' or 'No'."}
            ]
        }
        response = requests.post(url, json=data, headers=headers)
        answer = response.json()['choices'][0]['message']['content'].strip().lower()
        return "Pass" if "yes" in answer else "Fail"
    except Exception as e:
        return None

def check_answer_with_multiple_ais(user_code, question_title):
    for checker in [check_with_openai, check_with_gemini, check_with_deepseek]:
        result = checker(user_code, question_title)
        if result is not None:
            return result
    return "Unable to check answer (all AI limits reached or error occurred)"


@login_required(login_url='login')
def solve_questions(request):
    if request.user.is_superuser:
        return HttpResponseForbidden("Admin cannot access user dashboard.")
    questions = DSAQuestion.objects.all()
    return render(request, 'user/solve_questions.html', {'questions': questions})

@login_required(login_url='login')
def solve_question(request, question_id):
    if request.user.is_superuser:
        return HttpResponseForbidden("Admin cannot access user dashboard.")
    question = get_object_or_404(DSAQuestion, id=question_id)
    result = None
    if request.method == 'POST':
        form = UserAnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['user_answer'].strip().lower()
            correct_answer = (question.answer or '').strip().lower()
            is_correct = user_answer == correct_answer
            UserAnswer.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={'user_answer': form.cleaned_data['user_answer'], 'is_correct': is_correct}
            )
            result = "Pass" if is_correct else "Fail"
            messages.success(request, f'Answer submitted! Result: {result}')
            return render(request, 'user/solve_question.html', {
                'question': question,
                'form': form,
                'result': result,
            })
    else:
        form = UserAnswerForm()
    return render(request, 'user/solve_question.html', {
        'question': question,
        'form': form,
        'result': result,
    })

@login_required(login_url='login')
def user_profile(request):
    if request.user.is_superuser:
        return HttpResponseForbidden("Admin cannot access user dashboard.")
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Profile updated successfully!')
    return render(request, 'user/user_profile.html')