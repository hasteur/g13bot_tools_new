#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Syntax: python g13_nom_bot.py<F3>

"""

#
# (C) Rob W.W. Hooft, 2004
# (C) Daniel Herding, 2004
# (C) Wikipedian, 2004-2008
# (C) leogregianin, 2004-2008
# (C) Cyde, 2006-2010
# (C) Anreas J Schwab, 2007
# (C) xqt, 2009-2012
# (C) Pywikipedia team, 2008-2012
# (C) Hasteur, 2013
#
__version__ = '$Id$'
#
# Distributed under the terms of the MIT license.
#

import os, re, pickle, bz2, time, datetime, logging
from dateutil.relativedelta import relativedelta
import pywikibot

from pywikibot import i18n, Bot, config, pagegenerators

#DB CONFIG
from db_handle import *
# This is required for the text that is shown when you run this script
# with the parameter -help.
logger = logging.getLogger('g13_nom_bot')
logger.setLevel(logging.DEBUG)
trfh = logging.handlers.TimedRotatingFileHandler('logs/g13_nom', \
    when='D', \
    interval = 1, \
    backupCount = 90, \
)
trfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
trfh.setFormatter(formatter)
logger.addHandler(trfh)
trfh.doRollover()

def add_text(page=None, addText=None, summary=None, regexSkip=None,
             regexSkipUrl=None, always=False, up=False, putText=True,
             oldTextGiven=None, reorderEnabled=True, create=False):
    # When a page is tagged as "really well written" it has a star in the
    # interwiki links. This is a list of all the templates used (in regex
    # format) to make the stars appear.
    starsList = [
        u'bueno',
        u'bom interwiki',
        u'cyswllt[ _]erthygl[ _]ddethol', u'dolen[ _]ed',
        u'destacado', u'destaca[tu]',
        u'enllaç[ _]ad',
        u'enllaz[ _]ad',
        u'leam[ _]vdc',
        u'legătură[ _]a[bcf]',
        u'liamm[ _]pub',
        u'lien[ _]adq',
        u'lien[ _]ba',
        u'liên[ _]kết[ _]bài[ _]chất[ _]lượng[ _]tốt',
        u'liên[ _]kết[ _]chọn[ _]lọc',
        u'ligam[ _]adq',
        u'ligoelstara',
        u'ligoleginda',
        u'link[ _][afgu]a', u'link[ _]adq', u'link[ _]f[lm]', u'link[ _]km',
        u'link[ _]sm', u'linkfa',
        u'na[ _]lotura',
        u'nasc[ _]ar',
        u'tengill[ _][úg]g',
        u'ua',
        u'yüm yg',
        u'רא',
        u'وصلة مقالة جيدة',
        u'وصلة مقالة مختارة',
    ]

    errorCount = 0
    site = pywikibot.getSite()
    pathWiki = site.family.nicepath(site.lang)
    site = pywikibot.getSite()
    if oldTextGiven is None:
        try:
            text = page.get()
        except pywikibot.NoPage:
            if create:
                pywikibot.output(u"%s doesn't exist, creating it!"
                                 % page.title())
                text = u''
            else:
                pywikibot.output(u"%s doesn't exist, skip!" % page.title())
                return (False, False, always)
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"%s is a redirect, skip!" % page.title())
            return (False, False, always)
    else:
        text = oldTextGiven
    # If not up, text put below
    if not up:
        newtext = text
        # Translating the \\n into binary \n
        addText = addText.replace('\\n', '\n')
        if (reorderEnabled):
            # Getting the categories
            categoriesInside = pywikibot.getCategoryLinks(newtext, site)
            # Deleting the categories
            newtext = pywikibot.removeCategoryLinks(newtext, site)
            # Getting the interwiki
            interwikiInside = pywikibot.getLanguageLinks(newtext, site)
            # Removing the interwiki
            newtext = pywikibot.removeLanguageLinks(newtext, site)

            # Adding the text
            newtext += u"\n%s" % addText
            # Reputting the categories
            newtext = pywikibot.replaceCategoryLinks(newtext,
                                                     categoriesInside, site,
                                                     True)
            # Dealing the stars' issue
            allstars = []
            starstext = pywikibot.removeDisabledParts(text)
            for star in starsList:
                regex = re.compile('(\{\{(?:template:|)%s\|.*?\}\}[\s]*)'
                                   % star, re.I)
                found = regex.findall(starstext)
                if found != []:
                    newtext = regex.sub('', newtext)
                    allstars += found
            if allstars != []:
                newtext = newtext.strip() + '\r\n\r\n'
                allstars.sort()
                for element in allstars:
                    newtext += '%s\r\n' % element.strip()
            # Adding the interwiki
            newtext = pywikibot.replaceLanguageLinks(newtext, interwikiInside,
                                                     site)
        else:
            newtext += u"\n%s" % addText
    else:
        newtext = addText + '\n' + text
    if putText and text != newtext:
        pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                         % page.title())
        #pywikibot.showDiff(text, newtext)
    # Let's put the changes.
    while True:
        # If someone load it as module, maybe it's not so useful to put the
        # text in the page
        if putText:
            if always or choice == 'y':
                try:
                    pass
                    if always:
                        page.put(newtext, summary,
                                 minorEdit=False)
                    else:
                        page.put_async(newtext, summary,
                                       minorEdit=False)
                except pywikibot.EditConflict:
                    pywikibot.output(u'Edit conflict! skip!')
                    return (False, False, always)
                except pywikibot.ServerError:
                    errorCount += 1
                    if errorCount < 5:
                        pywikibot.output(u'Server Error! Wait..')
                        time.sleep(5)
                        continue
                    else:
                        raise pywikibot.ServerError(u'Fifth Server Error!')
                except pywikibot.SpamfilterError, e:
                    pywikibot.output(
                        u'Cannot change %s because of blacklist entry %s'
                        % (page.title(), e.url))
                    return (False, False, always)
                except pywikibot.PageNotSaved, error:
                    pywikibot.output(u'Error putting page: %s' % error.args)
                    return (False, False, always)
                except pywikibot.LockedPage:
                    pywikibot.output(u'Skipping %s (locked page)'
                                     % page.title())
                    return (False, False, always)
                else:
                    # Break only if the errors are one after the other...
                    errorCount = 0
                    return (True, True, always)
        else:
            return (text, newtext, always)

def do_nominations(passnum = 0):
    print "Pass %i" % passnum
    change_counter = 0
    nom_cat = pywikibot.Category(
        pywikibot.getSite(),
        'Category:Candidates for speedy deletion as abandoned drafts or AfC submissions' 
    )
    already_nominated_list = set(nom_cat.articles())
    csd_cat_size = len(already_nominated_list)
    max_noms_csd_cat = 50 - csd_cat_size
    print max_noms_csd_cat
    if max_noms_csd_cat <= 0:
        return
    if passnum == 10:
        return
    logger.debug("Max Nominations from cat: %i" % max_noms_csd_cat)
    thirty_days_ago = ( 
      datetime.datetime.now() - \
      datetime.timedelta(days=30)
    )
    bot_recheck_date = (
        datetime.datetime.now() +
        relativedelta(months=-6)
    ).timetuple()
    notification_date = thirty_days_ago.strftime('%Y-%m-%d %H:%M:%S')
    logger.debug("Notification Date: %s" % notification_date)
    cur = conn.cursor()
    sql_string = """SELECT article, editor
       from g13_records
       where notified <= '%s'
         and nominated = '0000-00-00 00:00:00'
       ORDER BY id 
       LIMIT %i""" % (notification_date,max_noms_csd_cat)
    cur.execute( sql_string)
    results = cur.fetchall()
    logger.debug("Results Fetched: %i" % len(results))
    cur = None
    for article_item in results:
        article = None
        try:
            article = pywikibot.Page(
              pywikibot.getSite(),
              article_item[0]
            )
        except:
            logger.critical("Problem with %s" % article_item[0])
            continue
        notify_tuple = datetime.datetime.timetuple(article_item[2])
        article_item = article_item[0:2]
        if False == article.exists():
            #Submission doesn't exisist any more, Remove it from the DB
            curs = conn.cursor()
            sql_string = "DELETE from g13_records" + \
                " WHERE article = %s " + \
                " and editor = %s;"  
            curs.execute(sql_string,article_item)
            conn.commit()
            curs = None
            change_counter = change_counter + 1
            print "Non-exist: %s" % article.title()
            logger.info("Submission %s doesn't exisist." % article_item[0])
            continue
        if True == article.isRedirectPage():
            #Submission is now a redirect.  It's been moved somewhere which
            # invalidates the clock on G13
            curs = conn.cursor()
            sql_string = "DELETE from g13_records" + \
                " WHERE article = %s " + \
                " and editor = %s;"  
            curs.execute(sql_string,article_item)
            conn.commit()
            curs = None
            change_counter = change_counter + 1
            print "Now redirect: %s" % article.title()
            logger.info("Submission %s is now a redirect" % article_item[0])
            continue
        #Re-check date on article for edits (to be extra sure)
        edit_time_api = article.getLatestEditors()[0]['timestamp']
        edit_time = time.strptime( \
            edit_time_api,
            "%Y-%m-%dT%H:%M:%SZ"
        )
        th_d = datetime.datetime.timetuple(thirty_days_ago)
        created_ts = time.strptime(
            article.getCreator()[1],
            "%Y-%m-%dT%H:%M:%SZ"
        )
        if edit_time > th_d:
            #Page has been updated since the nudge, Not valid any more
            curs = conn.cursor()
            sql_string = "DELETE from g13_records" + \
                " WHERE article = %s " + \
                " and editor = %s;"  
            curs.execute(sql_string,article_item)
            conn.commit()
            curs = None
            change_counter = change_counter + 1
            print "Updated: %s" % article.title()
            logger.info("Submission %s has been updated" % article_item[0])
            continue
        elif created_ts > bot_recheck_date:
            #Page has been re-created since t 6 month mark, disqualify
            curs = conn.cursor()
            sql_string = "DELETE from g13_records" + \
                " WHERE article = %s " + \
                " and editor = %s;"  
            curs.execute(sql_string,article_item)
            conn.commit()
            curs = None
            change_counter = change_counter + 1
            print "Recreated: %s" % article.title()
            logger.info("Submission %s has been created in past 6 months" % article_item[0])
            continue
        elif edit_time > bot_recheck_date:
            #Page isn't quite eligible for G13, move along
            logger.info("Submission %s isn't ripe yet" % article_item[0])
            continue

        add_text( \
          page = article, \
          addText = '{{db-g13|ts=%s}}' % edit_time_api , 
          summary = '[[User:HasteurBot]]:Nominating for [[WP:G13|CSD:G13]]', \
          always = True, \
          reorderEnabled=False, \
          up = True
        )
        logger.info("Nominated: %s" % article_item[0])
        creator = article_item[1]
        curs = conn.cursor()
        sql_string = "UPDATE g13_records" + \
          " set nominated = current_timestamp" + \
          "  where " + \
          "   article = %s " + \
          "     and" + \
          "   editor = %s; " 
        curs.execute(sql_string, article_item)
        conn.commit()
        curs = None
        logger.debug('Updated nominated timestamp')
        user_talk_page = pywikibot.Page(
          pywikibot.getSite(),
          'User talk:%s' % creator
        )
        up_summary = '[[User:HasteurBot]]: Notification of '+\
          '[[WP:G13|CSD:G13]] nomination on [[%s]]' % (article.title())
        add_text( \
          page = user_talk_page, \
          summary = up_summary, \
          addText = '{{subst:db-afc-notice|%s}}~~~~\n' % (article.title()), \
          always = True, \
          up = False, \
          reorderEnabled=False, \
          create = True\
        )
        logger.info("Notified %s for %s" % (creator, article_item[0]))
        change_counter = change_counter + 1
    if change_counter > 0:
        do_nominations(passnum + 1)
    else:
        print "No eligible submissions to nominate. Terminate"



def main():
    do_nominations(0)    

if __name__ == "__main__":
    #TODO: Short Circuiting this untill the bot is more acceptable to the
    # community
    main()
