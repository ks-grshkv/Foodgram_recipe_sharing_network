# from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Recipy, Tag


def index(request):
    recipies = Recipy.objects.order_by('-pub_date')[:10]
    return HttpResponse(str(recipies))


def recipy_detail(request, id):
    return HttpResponse('recipy_detail')


def get_recipies_by_tag(request, tag):
    tag = get_object_or_404(Tag, title=tag)
    recipies = Recipy.objects.filter(tag=tag).order_by('-pub_date')[:10]
    return HttpResponse(str(recipies))