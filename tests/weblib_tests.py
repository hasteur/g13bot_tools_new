# -*- coding: utf-8  -*-
"""Weblib test module."""
#
# (C) Pywikibot team, 2014
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals

__version__ = '$Id$'

import sys
if sys.version_info[0] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

import pywikibot.weblib as weblib

from tests.aspects import unittest, TestCase
from tests.utils import PatchedHttp


class TestInternetArchive(TestCase):

    """Test weblib methods to access Internet Archive."""

    sites = {
        'archive.org': {
            'hostname': 'web.archive.org',
        },
    }

    def _test_response(self, response, *args, **kwargs):
        # for later tests this is must be present, and it'll tell us the
        # original content if that does not match
        self.assertIn('closest', response.content)

    def testInternetArchiveNewest(self):
        """Test Internet Archive for newest https://google.com."""
        with PatchedHttp(weblib, False) as p:
            p.after_fetch = self._test_response
            archivedversion = weblib.getInternetArchiveURL('https://google.com')
        parsed = urlparse(archivedversion)
        self.assertIn(parsed.scheme, [u'http', u'https'])
        self.assertEqual(parsed.netloc, u'web.archive.org')
        self.assertTrue(parsed.path.strip('/').endswith('www.google.com'), parsed.path)

    def testInternetArchiveOlder(self):
        """Test Internet Archive for https://google.com as of June 2006."""
        with PatchedHttp(weblib, False) as p:
            p.after_fetch = self._test_response
            archivedversion = weblib.getInternetArchiveURL('https://google.com', '200606')
        parsed = urlparse(archivedversion)
        self.assertIn(parsed.scheme, [u'http', u'https'])
        self.assertEqual(parsed.netloc, u'web.archive.org')
        self.assertTrue(parsed.path.strip('/').endswith('www.google.com'), parsed.path)
        self.assertIn('200606', parsed.path)


class TestWebCite(TestCase):

    """Test weblib methods to access WebCite."""

    sites = {
        'webcite': {
            'hostname': 'www.webcitation.org',
        }
    }

    @unittest.expectedFailure
    def testWebCiteOlder(self):
        """Test WebCite for https://google.com as of January 2013."""
        archivedversion = weblib.getWebCitationURL('https://google.com', '20130101')
        self.assertEqual(archivedversion, 'http://www.webcitation.org/6DHSeh2L0')


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
