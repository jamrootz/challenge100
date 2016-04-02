#!/usr/bin/python3

'''
Program to parse the beer standings table.
Should categorize beers into a dictionary or other data structure.
Add some new categories: Distribution Regions, Season, Rarity
'''

from html.parser import HTMLParser
import json

beerList = []		#Will contain all the the beer objects
extra_categories = ("Distribution", "Establishments", "Dates", "Availability")

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
				# Display the most recent two beers added to the list. They should be different!!!
			self.index += 1

class Beer():
	def __init__(self, catList, bList): # pass in list of categories from table headers
		self.details = {}
		for cat, element in zip(catList, bList): 
			self.details[cat] = element
		for cat in extra_categories:
			if cat not in list(self.details.keys()):
				self.details[cat] = ""
		if self.details["Checkin"]:
			self.details["Checkin"]= "True"
		else: self.details["Checkin"]= "False"
	def showDetails(self):
		for d in list(self.details.keys()): print(d,": ", self.details[d])
		print('\n\n')


'''
# If progress.json does not exist, create it from html input

'''
# If progress.json already exists, read and then overwrite it
try:
	brewfile = open("progress.json" , 'r' )
	# The entries have been separated by |, do not use this character in any string objects
	brews = brewfile.read().split('|')
	for brew in brews[:-1]:			# The last element is a null string, omit
		jBeer = json.loads(brew)
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

for brew in beerList: brew.showDetails()

# Write the updated progress to our json file
brewfile = open("progress.json", "w")
#json.JSONEncoder().encode(beerList)
for brew in beerList:
	json.dump(brew.details, brewfile)
	brewfile.write("|")
brewfile.close()
