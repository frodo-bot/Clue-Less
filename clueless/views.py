# Create your views here.
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse

messages = []

def index(request):
    return render(request, 'index.html', {})

class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def gameState(request):
    global messages
    if request.method == 'POST':
        name = request.POST.get('name', '')
        if name:
            messages.append(name + " sent a message!")
    data = {
        "messages" : messages
    }
    return JsonResponse(data)

def clearState(request):
    global messages
    if request.method == 'POST':
        messages.clear()
    data = {
        "messages" : messages
    }
    return JsonResponse(data)
