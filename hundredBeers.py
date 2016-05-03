#!/usr/bin/python3

'''
Program to parse the beer standings table.
Should categorize beers into a dictionary or other data structure.
Add some new categories: Distribution Regions, Season, Rarity
'''

from html.parser import HTMLParser
import json
import math

beerList = []		#Will contain all the the beer objects
extra_categories = ("Distribution", "Establishments", "Dates", "Availability", "highlight")

class MyHTMLParser(HTMLParser):
	inTable = False			# Indicates whether data falls within a table
	inHeader = False			# Indicates whether data falls within a tracked table element
	inData = False			# Indicates whether data falls within a tracked table element
	categories = []
	index = 0				# Running count of data elements accessed to be indexed mod len(categories)
	beer = []
	def __init__(self):
		super(MyHTMLParser,self).__init__(convert_charrefs=True)
	def handle_starttag(self, tag, attrs):
		if "table" == tag:
			self.inTable = True
			print("Starting Table")
		elif tag == "th":
			#print("Start header Tag: ", tag)
			self.inHeader = True
		elif tag == "td": 
			#print("Start data Tag: ", tag)
			self.inData = True
	def handle_endtag(self, tag):
		if tag == "table":
			self.inTable = False
			print("Ending Table")
		elif tag == "th":
			#print("End header Tag: ", tag)
			self.inHeader = False
		elif tag == "td":
			#print("End data Tag: ", tag)
			self.inData = False
	def handle_data(self, data):
		#print("In tag: %d, In table: %d" % (self.inTag, self.inTable) )
		if self.inHeader and self.inTable:
			#print("Category: ", data)
			self.categories.append(data.strip())
		elif self.inData and self.inTable:
			#print("Data: ", data)
			self.beer.append(data.strip())
			# after appending the last trait for a beer, create a new beer object
			if self.index % len(self.categories) == len(self.categories) -1:
				#print("Adding: ", self.beer[(self.index+1)-len(self.categories):self.index+1])
				beerList.append( Beer(self.categories, self.beer[(self.index+1)-len(self.categories):self.index+1]) )
			self.index += 1

class Beer():
	def __init__(self, catList, bList): # pass in list of categories from table headers
		self.details = {}
		for cat, element in zip(catList, bList): 
			self.details[cat] = element
		for cat in extra_categories:
			if cat not in list(self.details.keys()):
				self.details[cat] = ""
		if self.details["Checkin"] in ("True", "\u2713"):
			self.details["Checkin"]= "True"
		else: self.details["Checkin"]= "False"
	def showDetails(self):
		for d in list(self.details.keys()): print(d,": ", self.details[d])
		print('\n\n')

def add_beer(sample):
	clear_screen()
	print("Adding a beer\n\n\n")
	categories = list(sample.details.keys())
	values = [ input("Enter %s: " % cat) for cat in categories ]
	beer = Beer(categories, values)
	return beer

def create_webpage(beer2find):
	page = open("gh-pages/index.html","w")
	page.write("<html>\n<head><title>Beer Challenge</title></head>\n")
	page.write("<body><h2 align=center>Beers left to find: %d</h2>\n<table width=100%% align=center border=1px>\n" % len(beer2find) )
	for index, beer in enumerate(beer2find):
		if beer.details["highlight"] == "True":
			page.write("<tr bgcolor=yellow>\n")
		else:
			page.write("<tr>\n")
		page.write("<td>%2d</td>" % (index+1))
		page.write("<td> <em>%s</em> <br> <b>%s</b> </td>" % (beer.details["Beer"], beer.details["Brewery"]) )
		page.write("<td> %s <br> <b>%s</b> </td>" % (beer.details["Style"], beer.details["State"]) )
		page.write("<td width=35%%> Where: %s <br> When: %s </td>" % (beer.details["Distribution"], beer.details["Dates"]) )
		page.write("<td width=35%%> Found: %s <br> %s </td>" % (beer.details["Establishments"], beer.details["Availability"]) )
		page.write("</tr>\n")
	page.write("</table>\n</body>\n</html>")
	page.close()

def clear_screen():
	print("\n"*60)

def show_options(beer2find):
	clear_screen()
	print("Which beer do you wish to modify?"+"\n"*3)
	for index in range(math.ceil(len(beer2find)/2)):
		print( str(index).rjust(15) + ". %(Brewery)-25s - %(Beer)-50s" % beer2find[index].details , end='')
		if index + math.ceil(len(beer2find)/2) < len(beer2find):
			print( str(index + math.ceil(len(beer2find)/2) ).rjust(15) + ". %(Brewery)-25s - %(Beer)s" % beer2find[(index+ math.ceil(len(beer2find)/2))].details )
	opt = input("\n"*5 + "Enter the number of the beer (q=quit, a=add, u=uncheck, c=clear highlights, b=brewery sort, s=state sort): ")
	return opt.lower()

def edit_beer(beer):
	clear_screen()
	print("Selected %(Brewery)s (%(Beer)s) " % beer.details)
	print("\n\n\n\tOptions:\n")
	print("\t\t1. Check in")
	print("\t\t2. Add Distribution Details")
	print("\t\t3. Add Dates of availability")
	print("\t\t4. Add Establishments carrying the beer")
	print("\t\t5. Describe abundance of the beer")
	print("\t\t6. Toggle Highlight (%(highlight)s)" % beer.details)
	print("\t\t7. Done")
	choice = input("\n\n\nWhat would you like to do? ")
	if choice == "1":
		beer.details["Checkin"] = "True"
	elif choice == "6":
		if beer.details["highlight"] == "True":
			beer.details["highlight"] = ""
		else: beer.details["highlight"] = "True"

def clear_highlights(beers):
	# Set 'highlight' key of each beer detail to "" to clear state
	for beer in beers:
		beer.details["highlight"] = ""

'''
# If progress.json does not exist, create it from html input

'''
# If progress.json already exists, read and then overwrite it
try:
	brewfile = open("progress.json" , 'r' )
	brews = brewfile.readlines()
	for brew in brews:
		jBeer = json.loads(brew)
		#keys = ["highlight"]
		#values = [""]
		keys = []
		values = []
		for key in jBeer:
			keys.append(key)
			values.append(jBeer[key])
		beerList.append( Beer(keys, values) )
	brewfile.close()
except FileNotFoundError:
	brewfile = open("beerTable.html" , 'r' )
	parser = MyHTMLParser()
	parser.feed("".join(brewfile.readlines() ) )
	brewfile.close()

#for brew in beerList: brew.showDetails()

opt=None
while not opt == 'q':
	# Create list of beers yet to be found
	beer2find = [ beer for beer in beerList if beer.details["Checkin"] == "False" ]
	opt = show_options(beer2find)
	try:
		num = int(opt)
		if num in range(len(beer2find)):
			# edit that beer
			edit_beer(beer2find[num])
		else:
			# Give a warning and/or quit
			pass
	except ValueError:
		# It was not a number so should be a control character
		if opt == 'a':
			# Add beer routine
			beerList.append( add_beer(beer2find[0]) )
		elif opt == 'u':
			# Uncheck beer routine
			pass
		elif opt == 'c':
			# Unhighlight all selections
			clear_highlights(beerList)
		elif opt == 'b':
			# Sort by brewery routine
			beerList = sorted(beerList, key=lambda k: k.details['Brewery'])
		elif opt == 's':
			# Sort by state routine
			beerList = sorted(beerList, key=lambda k: k.details['State'])
		elif opt == 'q':
			# Quit routine
			pass
create_webpage(beer2find)

# Write the updated progress to our json file
brewfile = open("progress.json", "w")
#json.JSONEncoder().encode(beerList)
for brew in beerList:
	json.dump(brew.details, brewfile)
	brewfile.write("\n")
brewfile.close()
