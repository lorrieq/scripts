#Script to write kml files from user's Attackpoint log to a file
#Laurence Quinn, lorrieq

import urllib.request
import re
import tkinter
import math

def get_monthly_links(user_id, s_month, s_yr, e_month, e_yr):
	month_days = ("31", "28", "31", "30", "31", "30", "31", "31", "30", "31", "30", "31")
	base_url = "http://attackpoint.org/viewlog.jsp/user_" + user_id + "/period-"
	s_month = int(s_month)
	s_yr = int(s_yr)
	e_month = int(e_month)
	e_yr = int(e_yr)

	month = s_month
	yr = s_yr
	url_list = []

	while not (yr == e_yr and month > e_month):
		url = base_url + month_days[month - 1] + "/enddate-" + str(yr) + "-"

		if(month < 10):
			url += "0"

		url += str(month) + "-" + month_days[month - 1]

		url_list.append(url)

		month += 1

		if(yr == e_yr and month > e_month):
			break

		if(month == 13):
			month = 1
			yr += 1

	return url_list

def get_session_ids(monthly_links):
	pattern = re.compile('sessionid(\d+)')
	ids = []

	for link in monthly_links:
		with urllib.request.urlopen(link) as url:
			html = url.read().decode('utf-8')
			found = re.findall(pattern, html)
			ids += found

	return ids

def write_doc_bounds(file, control):
	beginning_tags = '''<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:xal="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0">
		<Document>
			<Style id="trackStyle">
				<LineStyle>
					<color>7f0000ff</color>
					<width>4.0</width>
				</LineStyle>
			</Style>'''
	ending_tags = '</Document></kml>'
	tags = beginning_tags if (control == 0) else ending_tags
	write_bytes = bytes(tags, 'utf-8')

	file.write(write_bytes)

	return

def write_kml_file(session_ids):
	base_url = 'http://attackpoint.org/sessiondata.jsp?sessionid='
	f = open('tracks.kml', 'wb')

	write_doc_bounds(f, 0)

	coord_pattern = re.compile(r'(?i)(<Placemark>(.|\s)*</Placemark>)')
	for id_num in session_ids:
		url = base_url + str(id_num) + '&format=kml'

		try:
			with urllib.request.urlopen(url) as kml_html:
				pure_html = kml_html.read().decode('utf-8')
				first = pure_html.split('\n', 1)[0]
				if(len(first) < 10):
					continue
				
				coords = re.search(coord_pattern, pure_html)

				f.write(bytes(coords.group(0), 'utf-8'))

		except urllib.error.HTTPError as e:
			1 + 1
			#probably a note, not a training

	write_doc_bounds(f, 1)
	f.close()

	return

def main():
	user_id = idinput_w.get()
	start_date = sdinput_w.get()
	end_date = edinput_w.get()
	start = start_date.split("-")
	end = end_date.split("-")

	if(len(start) != 2 or len(end) != 2):
		return

	try:
		val = int(user_id)
		val = int(start[0])
		val = int(start[1])
		val = int(end[0])
		val = int(end[1])
	except ValueError:
		return

	if(int(start[0]) < 1 or int(start[0]) > 12 or int(end[0]) < 1 or int(end[0]) > 12):
		return
	if(int(start[1]) < 1999):
		start[1] = 1999
	
	monthly_links = get_monthly_links(user_id, start[0], start[1], end[0], end[1])
	session_ids = get_session_ids(monthly_links)
	write_kml_file(session_ids)
	top.quit()

top = tkinter.Tk()
top.geometry('250x150')
idlabel_w = tkinter.Label(top, text="User Id")
idlabel_w.pack()
idinput_w = tkinter.Entry(top)
idinput_w.pack()
sdlabel_w = tkinter.Label(top, text="Start Date")
sdlabel_w.pack()
sdinput_w = tkinter.Entry(top)
sdinput_w.pack()
edlabel_w = tkinter.Label(top, text="End Date")
edlabel_w.pack()
edinput_w = tkinter.Entry(top)
edinput_w.pack()
submit_w = tkinter.Button(top, text="Submit", command=main)
submit_w.pack()
tkinter.mainloop()