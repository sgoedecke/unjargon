from django.shortcuts import render
from .forms import JargonForm

# Create your views here.

def main_app(request):
	if request.method == "POST":
		form = JargonForm(request.POST)
		if form.is_valid():
			jargon_text = form.save(commit=False)
			jargon_text.save()
			jargon_text.sanitize_text() #remove whitespace and line breaks
			chunk_map = jargon_text.make_chunk_map()
			return render(request, './jargon/main_app.html', {'form': form,'chunks': chunk_map})
	else:
		form = JargonForm()
	return render(request, './jargon/main_app.html', {'form': form})
