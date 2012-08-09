#!/usr/bin/python
# -*- coding: utf-8 -*-

# importing modules
# requires that pywikipediabot modules be in your PYTHONPATH
import sys
from wikipedia import *
from add_text import * #for method writeEntireTemplate
from replace import * #for method writeVIAFaramOnly
 
# global variables
enwp = getSite('en','wikipedia')
dewp = getSite('de','wikipedia')
wikilinks = open("wikilinksforbot.out")
wikilinks = wikilinks.readlines()
viafbotrun = ("viafbotrun.log", 'w+')
same = 0
total = 0
nopage = 0


def pageValidate(nameOfPage):
    """accepts string of page name in EnglishWikipedia. 
    returns a Page Object of either the page or it's redirect (upto 10 redirects).
    raises NoPage exception if the page does not exist"""
    possiblePage = Page(enwp,nameOfPage)
    for i in range(1,10):
        try:
            possiblePage.get()
            return possiblePage
        except IsRedirectPage, redirPageName:
            possiblePage = Page(enwp,str(redirPageName))
        except NoPage:
            raise NoPage
        
def determineAuthorityControlTemplate(pageObject):
    """returns 'noACtemplate' if no Authority Control Template, 'templateNoVIAF' if AC template but no VIAF number, 
    and returns the viaf number if it exists"""
    templates = pageObject.templatesWithParams()
    for template in templates:
        if template[0] == 'Authority control':
            for param in template[1]:
                if param[:4] == 'VIAF':
                    return param[5:]
            return 'templateNoVIAF'
    return 'noACtemplate'

def determineNormdatenTemplate(pageObject):
    """returns 'noNormdatenTemplate' if no Normdaten Template, 'templateNoVIAF' if Normdaten template but no VIAF number, 
    and returns the viaf number if it exists"""
    templates = pageObject.templatesWithParams()
    for template in templates:
        if template[0] == 'Normdaten':
            for param in template[1]:
                if param[:4] == 'VIAF':
                    return param[5:]
            return 'templateNoVIAF'
    return 'noNormdatenTemplate'

def getGermanName(pageObject):
    """returns a Page object which is the equivalent German Wikipedia page to argument
    raises NoPage if there is no German equivalent."""
    pageText = pageObject.get()
    interWikis = getLanguageLinks(pageText)
    try:
        return interWikis[dewp]
    except KeyError:
        raise NoPage
    
def writeToWiki(validatedPage, acStatus, normdatenStatus):
    """Writes viafnum or reports viafnum conflicts to or about validatedPage"""
    if (normdatenStatus == 'noNormdatenTemplate') or (normdatenStatus == 'templateNoVIAF'):
        #Germans could use this data, but that's another project.
        if acStatus == 'noACtempate':
            writeEntireTemplate(validatedPage, viafnum)
        elif acStatus == 'templateNoVIAF':
            writeVIAFparamOnly(validatedPage,viafnum)
        elif type(acStatus)==int:
            pass
            #check and report
    elif type(normdatenStatus)==int:
        if acStatus == 'noACtempate':
            if acStatus == normdatenStatus:
                writeEntireTemplate(validatedPage, viafnum)
            else:
                pass#report
        elif acStatus == 'templateNoVIAF':
            if viafnum == normdatenStatus: #so there is a english template and viafnum agrees with dewp
                writeVIAFparamOnly(validatedPage,viafnum)
            else:
                pass#report
        elif type(acStatus)==int:
            if acStatus == normdatenStatus:
                pass#report
            else:
                pass#report
    else:
        raise Error

def writeEntireTemplate(validatedPage, viafnum):
    """Uses add_text.py to add the wikitext of
     {{Authority control}} template with the VIAF parameter"""
    ACtemplateWithVIAF = '\n{{Authority control|VIAF=' + str(viafnum) + '}}\n'
    editSummary = 'Added the {{Authority control}} template with VIAF number ' + str(viafnum) + '.'
    add_text(page = validatedPage, 
             addText = ACtemplateWithVIAF, 
             always = True, #so add_text won't ask for confirmation
             summary = editSummary)

def writeVIAFparamOnly(validatedPage,viafnum):
    """Instantiates and runs replace.py's ReplaceRobot class"""
    preloadingGen = [validatedPage]
    replacements = [('{{Authority control' , '{{Authority control|VIAF=' + str(viafnum) + '|')]
    editSummary = 'Adding VIAF parameter to Authority control with VIAF number ' + str(viafnum)
    exceptions = []
    acceptall = True
    allowoverlap = False
    recursive = False
    add_cat = None
    sleep = None
    titlefile = None
    excoutfile = None
    replaceBot = ReplaceRobot(preloadingGen, replacements, exceptions, acceptall,
                       allowoverlap, recursive, add_cat, sleep, editSummary,
                       titlefile, excoutfile)
    replaceBot.run()

writeVIAFparamOnly(Page(enwp,'User:VIAFbot/empty'),123456789)

print determineNormdatenTemplate(getGermanName(Page(enwp,'Oscar Wilde')))
print determineAuthorityControlTemplate(Page(enwp,'Oscar Wilde'))

#the main loop
for wikilink in wikilinks:
    wikilink = wikilink.split() #to get the line into a list of (name, viafnum)
    unvalidatedPageName = wikilink[0]
    viafnum = wikilink[1]
    try:
        validatedPage = pageValidate(unvalidatedPageName) #It's possible that the page doesn't exist
    except NoPage:
        viafbotrun.write(unvalidatedPageName.title() + "did not exist, or redirected more than 20 times")
        continue  #If the page doesn't exist, then we don't need to write anything to the Wiki.
    
    #get statuses of Authority Control and Normdaten templates
    acStatus = determineAuthorityControlTemplate(validatedPage)
    try:
        germanPageName = getGermanName(validatedPage)
    except NoPage: #There was no German equivalent page
        germanPageName = None
        viafbotrun.write('No German equivalent')
    if germanPageName: #Only need to get NormdatenStaus if a German equivalent page exists.
        normdatenStatus = determineNormdatenTemplate(germanPageName)
    else:
        normdatenStatus = 'noNormdatenTemplate' #if there's no page there's also noACtemplate either

    try:
        writeToWiki(validatedPage, acStatus, normdatenStatus)
    except Error:
        viafbotrun.write("Drastic. AC or Normdaten did not have one of the supposed 3 statuses (no,yesnoviaf,yeswithviaf)")
    
    
    writeToLog()
    
    origNameOfPage = wikilink[0]
    afternameOfPage = pageValidator(origNameOfPage)
    print origNameOfPage, afternameOfPage
    total = total +1
    if afternameOfPage == None:
        nopage= nopage +1
        viafbotrun.write("No such article as " + origNameOfPage)
    else:
        pass
    if origNameOfPage == afternameOfPage:
        same = same +1
    else:
        pass
    linkvalidity.write( str(total) + " " + str(same) + str(nopage) + '\n')

#close resources
wikilinks.close()