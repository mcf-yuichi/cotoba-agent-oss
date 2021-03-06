"""
Copyright (c) 2020 COTOBA DESIGN, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import unittest

from programy.dialog.splitter.splitter import SentenceSplitter
from programy.config.bot.splitter import BotSentenceSplitterConfiguration


class SentenceSplitterTests(unittest.TestCase):

    def test_initiate_spellchecker(self):

        config = BotSentenceSplitterConfiguration()
        self.assertIsNotNone(config)

        splitter = SentenceSplitter.initiate_sentence_splitter(config)
        self.assertIsNotNone(splitter)
        self.assertIsInstance(splitter, SentenceSplitter)

    def test_initiate_no_class(self):

        config = BotSentenceSplitterConfiguration()
        self.assertIsNotNone(config)
        config._classname = None

        splitter = SentenceSplitter.initiate_sentence_splitter(config)
        self.assertIsNone(splitter)

    def test_split(self):

        config = BotSentenceSplitterConfiguration()
        self.assertIsNotNone(config)
        config._classname = 'programy.dialog.splitter.splitter.SentenceSplitter'

        splitter = SentenceSplitter.initiate_sentence_splitter(config)
        self.assertIsNotNone(splitter)
        self.assertIsInstance(splitter, SentenceSplitter)

        with self.assertRaises(NotImplementedError):
            splitter.split("Thi is a pen")

    def test_remove_punctuation(self):

        config = BotSentenceSplitterConfiguration()
        self.assertIsNotNone(config)

        splitter = SentenceSplitter.initiate_sentence_splitter(config)
        self.assertIsNotNone(splitter)

        self.assertEquals("", splitter.remove_punctuation(""))
        self.assertEquals("", splitter.remove_punctuation("()"))
        self.assertEquals("Hello world", splitter.remove_punctuation("(Hello, world)"))
