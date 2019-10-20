# Create your views here.
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse

suggestions = []
accusations = {}

def index(request):
    return render(request, 'index.html', {})

class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def gameState(request):
    global suggestions
    global accusations
    name = request.GET.get('name', '')
    if name in accusations:
        userAccusations = accusations[name]
    else:
        userAccusations = []
    data = {
        "suggestions" : suggestions,
        "accusations" : userAccusations
    }
    return JsonResponse(data)

def makeAccusation(request):
    global accusations
    if request.method == 'POST':
        name = request.POST.get('name', '')
        if name:
            character = request.POST.get('character', '')
            weapon = request.POST.get('weapon', '')
            room = request.POST.get('room', '')
            accusationStr = name + " made an accusation: " + character + ", " + weapon + ", " + room
            if name in accusations:
                accusations[name].append(accusationStr)
            else:
                accusations[name] = [accusationStr]
    data = {
        "accusations" : accusations[name]
    }
    return JsonResponse(data)

def makeSuggestion(request):
    global suggestions
    if request.method == 'POST':
        name = request.POST.get('name', '')
        character = request.POST.get('character', '')
        weapon = request.POST.get('weapon', '')
        room = request.POST.get('room', '')
        suggestions.append(name + " made a suggestion: " + character + ", " + weapon + ", " + room)
    data = {
        "suggestions" : suggestions
    }
    return JsonResponse(data)

def clearState(request):
    global suggestions
    global accusations
    if request.method == 'POST':
        suggestions.clear()
        accusations.clear()
    data = {
        "suggestions" : [],
        "accusations" : []
    }
    return JsonResponse(data)
