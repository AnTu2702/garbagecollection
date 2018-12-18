# -*- coding: utf-8 -*-

import os
import re
import pytz
import lxml
import requests
import urllib
import HTMLParser
import pytz
import json
import boto3

from datetime import datetime as dt
from datetime import timedelta as td

from lxml import etree

def lambda_handler(event, context):

	streetName = os.environ['STREET_NAME']
	streetId = os.environ['STREET_ID']
	houseNumber = os.environ['HOUSE_NUMBER']

	url = 'https://stadtreinigung.giessen.de/akal/akal1.php?von=B&bis=C'
	response = requests.post(url, data={u'strasse': streetId, u'hausnr': houseNumber})

	copyright = "<meta name='author' content='Durth Roos Consulting GmbH, Darmstadt'>"
	logo = "<br><img src='icons/logo.gif'>"
	headerBegin = "<table width=100%> <tr><th><H2 align=left>"+streetName+" "+houseNumber
	headerEnd = "</H2></th></tr></table>"

	regex = r'(.*)' + re.escape(copyright) + r'(.?)' + re.escape(headerBegin) + r'(.*)' + re.escape(headerEnd) + r'(.*)' + re.escape(logo) + r'.*'

	collectionsHtml = re.sub(' +',' ', response.text.replace("\r\n","").replace("\t"," "))

	matchObj = re.match(regex, collectionsHtml)
	#print matchObj
	
	collectionsXml = HTMLParser.HTMLParser().unescape(matchObj.group(4).replace("<br>",", ").replace("%","").replace("<b>"," ").replace("</b>"," "))

	messageDict = dict()

	table = etree.HTML(collectionsXml).find("body/table")
	rows = iter(table)

	for row in rows:
		date = ''
		if row[1].text.rstrip(", ") == u"Restmüll 4-wöchentlich":
			sort = u"Restmüll"
			date += row[2].text
		elif row[1].text.rstrip(", ") == u"Altpapier 4-wöchentlich":
			sort = u"Altpapier"
			date += row[2].text
			firstDate = dt.strptime("2017-01-11","%Y-%m-%d")
			date += firstDate.strftime('%d.%m.%Y') + ", "
			while True:
				fourWeeks = td(weeks = 4)
				nextDate = firstDate+fourWeeks
				if nextDate > dt.strptime("2025-12-31","%Y-%m-%d"):
					break
				date += str(nextDate.strftime('%d.%m.%Y')) + ", "
				firstDate = nextDate

		elif row[1].text.rstrip(", ") == u"Biotonne":
			sort = u"Biomüll"
			date += row[2].text
		elif row[1].text.rstrip(", ") == u"Gelber Sack":
			sort = u"Gelber Sack"
			date += row[2].text
		elif row[1].text.rstrip(", ") == u"Gelbe Tonne":
			sort = u"Gelbe Tonne"
			date += row[2].text
		elif row[1].text.rstrip(", ") == u"Sperrmüll auf Abruf":
			sort = u"Sperrmüll"
			date += row[2].text
		elif row[1].text.rstrip(", ") == u"Mobile Schadstoffsammlung":
			sort = u"Schadstoffe"
			date += row[2].text	
		else:
			continue

		date = date.rstrip(", ")	
		messageDict[sort]=date

	today = dt.now(pytz.utc)

	oneDay = td(days = 1)
	tomorrow = today+oneDay

	message = ''

	for sort, date in messageDict.iteritems():
		if tomorrow.strftime('%d.%m.%Y') in date:
			message += sort + ", "

	if message == '':
		pass
	else:
		message = tomorrow.strftime('%d.%m.%Y') + ": " + message
		print message.rstrip(", ")

		client = boto3.client('sns')
		response = client.publish(
		    TargetArn='arn:aws:sns:eu-central-1:985033182960:'+streetName.upper()+houseNumber+'_ABFALL',
		    Message=message.rstrip(", "),
		    Subject=u'Müllabfuhr'
		)

lambda_handler('', '')
