from celery import Celery
import urllib2
from uuid import uuid4

celery = Celery('tasks', broker = "redis://localhost:6379/0")


@celery.task
def scrap(url,filename):
	print "task param: >>>>>>> ", url
	response = urllib2.urlopen(url)
	html = response.read()
	f = open(filename, "w")
	f.write(html)
	f.close()
	return f
