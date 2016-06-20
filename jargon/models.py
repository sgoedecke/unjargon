from __future__ import unicode_literals

from django.db import models

#dictionary sample - maybe split this off later
# 1 is mild code, 2 is serious
jargon_dict = {
    "adduce" : 1,
    "adumbrate" : 1,
    "a fortiori" : 1,
    "ceteris paribus" : 1,
    "prima facie" : 1,
    "on this view" : 1,
    "defeasible" : 1,
    "de re" : 1,
    "de dicto" : 1,
    "etiology" : 1,
    "enthymeme" : 1,
    "ostensive" : 1,
    "intension" : 1,
    "possible world" : 1,
    "synchronic" : 1,
    "diachronic" : 1,
    "conception" : 1,
    "on this view" : 1,
    "agen" : 1,

    "deontolog" : 2, #deliberately just left the root here
    "consequential" : 2,
    "obtains" : 2,
    "utilitarian" : 2,
    "dialectic" : 2,
    "emotiv" : 2,
    "existential" : 2,
    "induct" : 2,
    "metaphysic" : 2,
    "modal" : 2,
    "epistem" : 2,
    "meta-ethic" : 2,
    }

# Create your models here.
class Chunk(models.Model):

    text = models.TextField()
    order = models.IntegerField(default=0)
    tag = models.IntegerField(default=0)

    def __str__(self):
        return self.text

class JargonText(models.Model):
    author = models.ForeignKey('auth.User', null=True) #allows for no author
    text = models.TextField()
#    tagged_text = models.ManyToManyField(Chunk, related_name='+')

    def __str__(self):
		return self.text

    def sanitize_text_alt(self): #removes whitespace, line breaks, etc, since these desync the chunk map from the split text (b/c cnt only moves 1 space per chunk)
        dirty_text = self.text
        clean_text = dirty_text.replace('\n',' ').replace('\r',' ').replace('  ',' ')

    def sanitize_text(self):
        clean_text = " ".join(self.text.split()) #split text and join it with spaces
        self.text = clean_text
        self.save()

    def break_into_chunks_alt(self):    #WARNING: this won't work with multi-word tags! deprecated
        print "Breaking into chunks..."
        chunks = self.text.split()
        cnt = 0
        for chunk in chunks:    #markup chunk list with tags
            if chunk in jargon_dict: #if the chunk matches a dict key
                chunks[cnt] = [jargon_dict[chunk], chunk]   #make the chunk list [tag, text]
            else:
                chunks[cnt] = [0, chunk]
                cnt = cnt+1
        print chunks
        #this function returns the text as a list of lists with format [tag, word]
        return chunks

    def make_chunk_map(self):    #this function builds a map. WARNING: will trigger inside words
        #clear chunks
        Chunk.objects.all().delete()
        print "deleted chunks"
        print Chunk.objects.all()

        print "Breaking into chunks, alternative method..."
        chunk_map = []
        for key in jargon_dict:
            loc = 0
            while loc >= 0:
                loc = self.text.lower().find(key, loc, len(self.text)) #find - need lower() in here to match capital letter versions
                if loc == -1:
                    break
                chunk_map.append([loc, loc + len(key), jargon_dict[key]]) #each entry in the chunk map is [start_logcation, end_location, location_tag]
                loc = loc + len(key)
        print chunk_map

        #now apply the chunk map to the text

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

            cnt = cnt + len(chunk) + 1 #move the counter along in spu
            chunk_cnt = chunk_cnt + 1
            tagged = False #this makes sure chunks don't get marked true if they fail to match one element in the map
        cnt = 0

        #note: if no matches, the above code will pass 'chunks' unchanged from self.text.split()
        #now make Chunk objects per chunk

        for chunk in chunks:
            new_chunk = Chunk()
            if str(chunk[0]).isalpha(): #if the above code hasn't found anything, this will return True
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
