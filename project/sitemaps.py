# myproject/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from match.models import Message, Char, User


class BlogPostSitemap(Sitemap):
    """
    ブログ記事のサイトマップ
    """
    changefreq = "always"
    priority = 0.8

    def items(self):
        return ['match:top']

    # モデルに get_absolute_url() が定義されている場合は不要
    def location(self, item):


        return reverse(item)



class StaticViewSitemap(Sitemap):
    """
    静的ページのサイトマップ
    """
    changefreq = "always"
    priority = 0.4

    def items(self):
        return ['match:about']

    def location(self, item):
        return reverse(item)
