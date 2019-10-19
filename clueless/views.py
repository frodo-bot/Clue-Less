# Create your views here.
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse

num = 0

def index(request):
    return render(request, 'index.html', {})

class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def getGameState(request):
    global num
    num += 1
    data = {
        "messages" : ["Example Message 1", "Example Message 2"],
        "num" : num
    }
    return JsonResponse(data)
