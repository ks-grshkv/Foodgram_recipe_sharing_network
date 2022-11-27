# from django.shortcuts import render
from django.http import HttpResponse


def create_user(request):
    return HttpResponse('create_user')


def sign_in(request):
    return HttpResponse('authorize_user')
