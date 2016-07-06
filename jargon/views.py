from django.shortcuts import render
from .forms import JargonForm

def main_app(request):
	if request.method == "POST":
		form = JargonForm(request.POST)
		if form.is_valid():
			jargon_text = form.save()
			jargon_text.sanitize_text() #remove whitespace, line breaks, non-ASCII characters
			chunk_map = jargon_text.make_chunk_map() # find out where the tagged chunks ought to be
			chunks = jargon_text.make_chunks_from_map(chunk_map) #build list of tagged Chunk objects
			jargon_percentage =jargon_text.find_jargon_percentage(chunks)
			return render(request, './jargon/main_app.html', {'form': form,'chunks': chunks, 'jargon_percentage': jargon_percentage})
	else: # if the user hasn't submitted any text
		form = JargonForm()
	return render(request, './jargon/main_app.html', {'form': form})
