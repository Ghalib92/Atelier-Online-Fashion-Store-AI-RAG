from django.shortcuts import render
from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponse
from django .contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required




def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Login successful! Welcome back.')
            return redirect('home')  # Redirect to homepage or dashboard
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')

    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']   
        last_name = request.POST['last_name'] 
        username = request.POST['username'] 
        password1 = request.POST['password1'] 
        password2 = request.POST['password2']  # Fixed the typo
        email = request.POST['email']

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')  # Redirect back to the signup page

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')  # Redirect to login page after successful signup

    return render(request, 'signup.html')  # Show signup form if request is not POST
def logout(request):
    auth.logout(request)
    return redirect('login') 
# Create your views here.
