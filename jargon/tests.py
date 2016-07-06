from django.test import TestCase
from .models import *
from . import jargon_dictionary
# Create your tests here.
class JargonTextMethodTests(TestCase):
    def test_sanitize_text_removes_bad_chars(self):
        text = JargonText(text='The   quick \n brown \t fox.')
        self.assertEqual(text.sanitize_text(), "The quick brown fox.")

    def test_make_chunk_map(self):
        text = JargonText(text='The fox.')
        chunks=text.make_chunk_map()
        chunk_1 = Chunk(text="The", order="0", tag="0")
        chunk_2 = Chunk(text="fox.", order="1", tag="0")
        self.assertEqual(chunks, [chunk_1,chunk_2])
