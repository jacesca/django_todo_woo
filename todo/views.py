from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    context = {'form': UserCreationForm()}

    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', context)

    else:
        # Create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'].strip(), password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')

            except IntegrityError:
                context['error'] = "That username has already been taken. Please choose a new username."
                return render(request, 'todo/signupuser.html', context)
        else:
            # Tell the user the password didn't match
            context['error'] = "Password did not match"
            return render(request, 'todo/signupuser.html', context)


def loginuser(request):
    context = {'form': AuthenticationForm()}

    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', context)

    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            context['error'] = 'Username and password did not match.'
            return render(request, 'todo/loginuser.html', context)
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    context = {'form': TodoForm()}

    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', context)
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            context['error'] = 'Bad data pass in! Try again.'
            return render(request, 'todo/createtodo.html', context)

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    context = {'todos': todos}
    return render(request, 'todo/currenttodos.html', context)

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    context = {'todos': todos}
    return render(request, 'todo/completedtodos.html', context)

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    context = { 'todo': todo }

    if request.method == 'GET':
        context['form'] = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', context)
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            context['error'] = 'Bad data pass in! Try again.'
            return render(request, 'todo/viewtodo.html', context)

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')