from __future__ import unicode_literals

from django.db import models
from . import jargon_dictionary
import re

class Chunk(models.Model):
	text = models.TextField()
	order = models.IntegerField(default=0)
	tag = models.IntegerField(default=0)

	def __str__(self):
		return self.text

class JargonText(models.Model):
	author = models.ForeignKey('auth.User', null=True) #allows for no author
	text = models.TextField()

	def __str__(self):
		return self.text

	def sanitize_text(self):
		#removes whitespace, line breaks, etc, since these desync the chunk map from the split text (b/c cnt only moves 1 space per chunk)
		clean_text = " ".join(self.text.split()) #split text and join it with spaces
		#remove non-ASCII characters
		clean_text = re.sub(r'[^\x00-\x7F]+','', clean_text)
		self.text = clean_text
		self.save()
		return clean_text

	def make_chunk_map(self):
		#this function builds a map of where the chunks ought to go
		print "Breaking into chunks..."
		chunk_map = []
		for key in jargon_dictionary.jargon_dict:
			loc = 0
			while loc >= 0:
				loc = self.text.lower().find(key, loc, len(self.text)) #find - need lower() in here to match capital letter versions
				if loc == -1:
					break
				chunk_map.append([loc, loc + len(key), jargon_dictionary.jargon_dict[key]])
				#each entry in the chunk map is formatted as [start_location, end_location, location_tag]
				loc = loc + len(key)
		return chunk_map

	def make_chunks_from_map(self,chunk_map):
		#this function takes the chunk map and builds chunks from it
		# first, build each chunk from text.split
		chunks = self.text.split()
		cnt = 0 #character counter
		chunk_cnt = 0 #chunk counter
		tagged = False
		for chunk in chunks:
			for map in chunk_map: #check if the chunk matches an area of the chunk map
				if cnt >= map[0] - 1 and cnt <= map[1] and tagged == False: #if the counter's in the chunk. [the -1 here is to prevent an initial character(like ") breaking the match)]
					chunks[chunk_cnt] = [map[2], chunk]
					tagged = True

				elif tagged == False:
					chunks[chunk_cnt] = [0,chunk]

			cnt = cnt + len(chunk) + 1 #move the counter along in word-sized blocks
			chunk_cnt = chunk_cnt + 1
			tagged = False #this makes sure chunks don't get marked true if they fail to match one element in the map
		#note: if no matches, the above code will pass the result of self.text.split()

		# now make the Chunk objects
		Chunk.objects.all().delete() # clear previous chunks
		cnt = 0
		for chunk in chunks:
			new_chunk = Chunk()
			if not is_integer(chunk[0]): # if it's got no tag (since no matches were found)
				new_chunk.text = chunk
				new_chunk.order = cnt
				new_chunk.tag = 0
			else:
				new_chunk.text = chunk[1]
				new_chunk.order = cnt
				new_chunk.tag = chunk[0]
			new_chunk.save()
			cnt = cnt + 1
		return Chunk.objects.order_by('order')

	def find_jargon_percentage(self, chunks):
		jargon_counter = 0
		for chunk in chunks:
			if chunk.tag != 0:
				jargon_counter = jargon_counter + 1
		jargon_percentage = (jargon_counter * 100) / len(chunks) #gotta watch out for integer truncation here
		return jargon_percentage



def is_integer(value):
	# check if something is an integer
	try:
		int(value)
		return True
	except ValueError:
		return False
