from .sitemaps import (
    BlogPostSitemap,
    StaticViewSitemap,
)
from django.contrib.sitemaps.views import sitemap,index
from django.views import generic
from django.shortcuts import redirect,render




def robot(request):
    return render(request, 'match/robot.html')
