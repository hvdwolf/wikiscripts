#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version 0.1, 2015-05-15, Harry van der Wolf
# This file contains some language specific strings and can easily be expanded by others
# for their own languages if necessary

# English is our default code so we initiate everything as English
LANGUAGE_CODE = 'en'
ARTICLE_URL = "Article url: "
WIKI_PAGE_URL = "Wikipedia: "
# In the function below we set some language specific comments. This needs to be made a separate include file
# so people can easily add their own language statement
def language_specifics(lang_code):
	WIKI_PAGE_URL = "Wikipedia: "
	# Adapt out fail safe english defaults to the correct ones
	if lang_code == "nl":
		LANGUAGE_CODE = 'nl'
		ARTICLE_URL = "Artikel url: "
	elif lang_code == "de":
		LANGUAGE_CODE = 'de'
		ARTICLE_URL = "Artikel url: "
	elif lang_code == "fr":
		LANGUAGE_CODE = 'fr'
		ARTICLE_URL = "URL de l'article: "
	elif lang_code == "no":
		LANGUAGE_CODE = 'no'
		ARTICLE_URL = "artikkelen url: "
	elif lang_code == "cs":
		LANGUAGE_CODE = 'cs'
		ARTICLE_URL = "článek url: "
	elif lang_code == "pl":
		LANGUAGE_CODE = 'pl'
		ARTICLE_URL = "artykuł url: "
	elif lang_code == "ja":
		LANGUAGE_CODE = "ja"
		ARTICLE_URL = "記事のURL: "
		WIKI_PAGE_URL = "ウィキペディア"
	elif lang_code == "ru":
		LANGUAGE_CODE = "ru"
		ARTICLE_URL = "Статья URL: "
		WIKI_PAGE_URL = "Википедия"
		# If you want to add your own country, copy (not change) below remarks
# and adapt for your language
#	elif lang_code == "your 2 digit code":
#		LANGUAGE_CODE = 'your 2 digit code'
#		ARTICLE_URL = "article url: "
	else:
		LANGUAGE_CODE = 'en'
		ARTICLE_URL = "Article url: "
		WIKI_PAGE_URL = "Wikipedia: "

	return LANGUAGE_CODE, ARTICLE_URL, WIKI_PAGE_URL

