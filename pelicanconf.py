#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'geek42'
SITENAME = u'geek42'
SITEURL = 'http://yunfan.github.io'
SITESUBTITLE = u'虽千万人，吾往矣'

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'cn'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (
	('google', 'http://www.google.com/'),
)

# Social widget
SOCIAL = (
	('twitter', 'http://twitter.com/jyf1987'),
)

DEFAULT_PAGINATION = 10

STATIC_PATHS = ['images', 'files']

# customized configure by manual
THEME = './themes/blueidea'
OUTPUT_SOURCES = True
DISQUS_SITENAME = 'geek42'

# Uncomment following line if you want document-relative URLs when developing
##RELATIVE_URLS = True
