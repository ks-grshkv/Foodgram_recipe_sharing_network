# from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Recipy, Tag


# def index(request):
#     recipes = Recipy.objects.order_by('-pub_date')[:10]
#     return HttpResponse(str(recipes))


# def recipy_detail(request, id):
#     return HttpResponse('recipy_detail')


# def get_recipes_by_tag(request, tag):
#     tag = get_object_or_404(Tag, title=tag)
#     recipes = Recipy.objects.filter(tag=tag).order_by('-pub_date')[:10]
#     return HttpResponse(str(recipes))
