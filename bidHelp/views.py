#coding=utf-8

from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render

def index(request):
    return render(request,'bidHelp/test1.html')

