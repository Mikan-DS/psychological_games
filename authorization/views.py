from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def confirmation_token(request):
    return HttpResponse('see you :)')