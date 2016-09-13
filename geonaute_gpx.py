# get gpx files from decathlon coach
# Laurence Quinn

import getpass
import mechanicalsoup
import json
from datetime import datetime
from datetime import timedelta

class Activity:
	def __init__(self, link, date):
		self.link = link
		self.date = date

	@property
	def link(self):
		return self._link
	@link.setter
	def link(self, value):
		self._link = value
	@property
	def date(self):
		return self._date
	@date.setter
	def date(self, value):
		self._date = value

def date_cmp(cmp_date, start, end):
	if(cmp_date < start):
		return 0
	elif(end < cmp_date):
		return 1
	else:
		return 2

def getActivityIdFrom(path):
	arr = path.split("/")
	return arr[len(arr) - 1].split(".")[0]

def write_gpx_start(file, name):
	text = '<?xml version="1.0" encoding="utf-8"?>\n'
	text += '<gpx version="1.1" creator="Laurence Quinn"\n'
	text += '  xsi:schemaLocation="http://www.topografix.com/GPX/1/1\n'
	text += 'http://www.topografix.com/GPX/1/1/gpx.xsd\n'
	text += 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1\n'
	text += 'http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"\n'
	text += '  xmlns="http://www.topografix.com/GPX/1/1"\n\n'
	text += 'xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"\n'
	text += '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
	text += '    <trk>'
	text += '    <name>Decathlon Coach to GPX - '
	text += name
	text += '</name>\n<trkseg>'
	text_bytes = bytes(text, 'utf-8')
	file.write(text_bytes)
	return

def write_gpx_end(file):
	text = '</trkseg></trk></gpx>'
	text_bytes = bytes(text, 'utf-8')
	file.write(text_bytes)
	return

def write_gpx(location, points, elevations, timestamp):
	activity_id = getActivityIdFrom(location)
	f = open(location, 'wb')
	write_gpx_start(f, activity_id)

	start_timestamp = timestamp
	for i in range(0, len(points)):
		point_str = '<trkpt lat="'
		point_str += str(points[i][0])
		point_str += '" lon="'
		point_str += str(points[i][1])
		point_str += '"><ele>'
		point_str += str(elevations[i][1])
		point_str += '</ele>'
		point_str += '<time>' + str(timestamp.year) + '-' + str(timestamp.month).zfill(2)
		point_str += '-' + str(timestamp.day).zfill(2) + 'T' + str(timestamp.hour).zfill(2)
		point_str += ':' + str(timestamp.minute).zfill(2) + ':' + str(timestamp.second).zfill(2)
		point_str += 'Z</time>'
		point_str += '</trkpt>'
		point_bytes = bytes(point_str, 'utf-8')
		f.write(point_bytes)
		timestamp = start_timestamp + timedelta(0, points[i][2])

	write_gpx_end(f)
	return

user = input("Decathlon coach username: ")
passw = getpass.getpass("Decathlon coach password: ")
start_d_str = input("From: ").split('/')
end_d_str = input("To: ").split('/')

start_d = datetime(int(start_d_str[0]), int(start_d_str[1]), int(start_d_str[2]), 0, 0, 0)
end_d = datetime(int(end_d_str[0]), int(end_d_str[1]), int(end_d_str[2]), 23, 59, 59)

dc_home = 'http://www.decathloncoach.com/en-FR/portal'
out = 'C:/Users/lorrieq/Desktop/'

# login to decathlon coach
browser = mechanicalsoup.Browser()
login = browser.get(dc_home)
form = login.soup.select('form')[0]
form.select('#email')[0]['value'] = user
form.select('#password')[0]['value'] = passw

home = browser.submit(form, login.url)

# get activity ids between dates
timeline = home.soup.select('#activity-timeline')[0]['data-activities']

activities = json.loads(timeline)
activity_count = len(activities)
activity_list = []

for i in range(activity_count - 1, 0, -1):
	activity = activities[i]
	date_str = activity['startDate'].split(',')
	activity_datetime = datetime(int(date_str[0]), int(date_str[1]), int(date_str[2]), int(date_str[3]), int(date_str[4]), int(date_str[5]))
	date_status = date_cmp(activity_datetime, start_d, end_d)
	
	if(date_status == 0):
		break	# date before start of range - no more activities in range
	elif(date_status == 1):
		continue	# date after end of range - could be more activities
	else:
		# date in range
		activity_list.append(Activity(activity['asset']['media'], activity_datetime))

base = dc_home + '/activities/'
for i in range(0, len(activity_list)):
	activity = activity_list[i]
	link = base + activity.link
	page = browser.get(link)
	points = json.loads(page.soup.select('.gmap-canvas')[0]['data-path'])
	elevs = json.loads(page.soup.select('li[data-name="elevation"]')[0].string)
	out_loc = out + activity.link + '.gpx'
	write_gpx(out_loc, points, elevs, activity.date)