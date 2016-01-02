# -*- coding: utf-8  -*-
#
# (C) Pywikibot team, 2008-2014
# (C) Hasteur 2016 (Fork of listpages script)
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#


import pywikibot
from pywikibot.pagegenerators import GeneratorFactory, parameterHelp
import pdb

docuReplacements = {'&params;': parameterHelp}


class Formatter(object):

    """Structure with Page attributes exposed for formatting from cmd line."""

    fmt_options = {
        '1': u"{num:4d} {page.title}",
        '2': u"{num:4d} [[{page.title}]]",
        '3': u"{page.title}",
        '4': u"[[{page.title}]]",
        '5': u"{num:4d} \03{{lightred}}{page.loc_title:<40}\03{{default}}",
        '6': u"{num:4d} {page.loc_title:<40} {page.can_title:<40}",
        '7': u"{num:4d} {page.loc_title:<40} {page.trs_title:<40}",
    }

    # Identify which formats need outputlang
    fmt_need_lang = [k for k, v in fmt_options.items() if 'trs_title' in v]

    def __init__(self, page, outputlang=None, default='******'):
        """
        Constructor.

        @param page: the page to be formatted.
        @type page: Page object.
        @param outputlang: language code in which namespace before title should
            be translated.

            Page namespace will be searched in Site(outputlang, page.site.family)
            and, if found, its custom name will be used in page.title().

        @type outputlang: str or None, if no translation is wanted.
        @param default: default string to be used if no corresponding namespace
            is found when outputlang is not None.

        """
        self.site = page._link.site
        self.title = page._link.title
        self.loc_title = page._link.canonical_title()
        self.can_title = page._link.ns_title()
        self.outputlang = outputlang
        if outputlang is not None:
            # Cache onsite in case of tranlations.
            if not hasattr(self, "onsite"):
                self.onsite = pywikibot.Site(outputlang, self.site.family)
            try:
                self.trs_title = page._link.ns_title(onsite=self.onsite)
            # Fallback if no corresponding namespace is found in onsite.
            except pywikibot.Error:
                self.trs_title = u'%s:%s' % (default, page._link.title)

    def output(self, num=None, fmt=1):
        """Output formatted string."""
        fmt = self.fmt_options.get(fmt, fmt)
        # If selected format requires trs_title, outputlang must be set.
        if (fmt in self.fmt_need_lang or
                'trs_title' in fmt and
                self.outputlang is None):
            raise ValueError(
                u"Required format code needs 'outputlang' parameter set.")
        if num is None:
            return fmt.format(page=self)
        else:
            return fmt.format(num=num, page=self)


def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: list of unicode
    """
    gen = None
    notitle = False
    fmt = '1'
    outputlang = None
    page_get = False

    # Process global args and prepare generator args parser
    local_args = pywikibot.handle_args(args)
    genFactory = GeneratorFactory()
    local_args.append("-titleregex .*?Dungeons & Dragons.*?")
    for arg in local_args:
        if arg == '-notitle':
            notitle = True
        elif arg.startswith("-format:"):
            fmt = arg[len("-format:"):]
            fmt = fmt.replace(u'\\03{{', u'\03{{')
        elif arg.startswith("-outputlang:"):
            outputlang = arg[len("-outputlang:"):]
        elif arg == '-get':
            page_get = True
        else:
            genFactory.handleArg(arg)

    gen = genFactory.getCombinedGenerator()
    this_site = pywikibot.Site()
    page_text = "#REDIRECT [[%s]]\n\n{{Redr|unprintworthy}}"
    if gen:
        for i, page in enumerate(gen, start=1):
            replace_title = page.title().replace('Dungeons & Dragons',
                'Dungeons and Dragons')
            dest_page =  pywikibot.Page(this_site,replace_title)
            if not dest_page.exists():
                target_redirect = page.title()
                if page.isRedirectPage():
                    target_redirect = page.getRedirectTarget().title()
                dest_text = page_text % target_redirect
                pdb.set_trace()
                dest_page.text = dest_text
                #dest_page.save(
                #    comment=u'Hasteurbot task N: Dungeons and Dragons',
                #    watch = False,
                #    botflag = True,
                #    force = True
                #)
                    


    else:
        pywikibot.showHelp()


if __name__ == "__main__":
    main()
