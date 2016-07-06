# Unjargon

Unjargon is a Django app for identifying how jargon-y a block of text is.

## Installation/Usage

All the work is done in the 'jargon' app. Check the views.py for how to do it: you need to collect the text as JargonText from a ModelForm, then run it through the relevant functions from models.py. It'll output the text as a list of Chunk objects, which you can then loop through in a template.
