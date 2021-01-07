from .sitemaps import (
    BlogPostSitemap,
    StaticViewSitemap,
)
from django.contrib.sitemaps.views import sitemap,index
from django.views import generic
from django.shortcuts import redirect
site = {
    'top': BlogPostSitemap,
    'about': StaticViewSitemap,
}
import boto3
from django.conf import settings


def SiteMap(request):

    return redirect('https://smash-match.s3-ap-northeast-1.amazonaws.com/site_map.xml')
