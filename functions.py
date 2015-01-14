#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import ConfigParser, os, sys, urllib2, json, codecs

import xml.etree.ElementTree as ET

##### read config file
config = ConfigParser.ConfigParser()
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__)))  # read config file

api = config.get('missatsamtal', 'api')
apiFormat = config.get('missatsamtal', 'format')
apiList = config.get('missatsamtal', 'list')
apiSearch = config.get('missatsamtal', 'search')

timeOut = int(config.get('missatsamtal', 'timeOut'))

##### what to do on errors
def onError(errorCode, extra):
    print "\n*** Error:"
    if errorCode == 1:
        print extra
        usage(errorCode)
    elif errorCode == 2:
        print "    No options given"
        usage(errorCode)
    elif errorCode == 3:
        print "    No program part chosen"
        usage(errorCode)
    elif errorCode in (4, 5, 6, 8, 12, 13):
        print "    %s" % extra
        sys.exit(errorCode)
    elif errorCode in (7, 9, 10, 11):
        print "    %s" % extra

##### some help
def usage(exitCode):
    print "\nUsage:"
    print "----------------------------------------"
    print "%s -l [-v]" % sys.argv[0]
    print "      Lists the most common numbers and their companies, max 500"
    print "        Options: 'v'erbose output"
    print "    OR"
    print "%s -h" % sys.argv[0]
    print "      Prints this"
    sys.exit(exitCode)
    
def outputQuestion(action, limit, number, verbose):
    if verbose:
        print "The url would be:"
    
    if action == "list":
        print "%s&limit=%s" % (apiList, limit)
    elif action == "search":
        print "%s&number=%s&numberOfCompanies=%s" % (apiSearch, number, limit)
        
        
def getResponse(url, verbose):
    try:
        response = urllib2.urlopen(url, timeout=timeOut).read()  # get data from server
        if verbose:
            print "--- Got data"
    except urllib2.URLError, e:
        if verbose:
            print "*** There was an error: %r" % e
            print "*** Could not get data"
           
    if verbose:
        print "--- Response:\n    %s" % response
        
    return response
        
def listNumbers(limit, outFile, verbose):
    numberList = []
    
    if outFile:
        if verbose:
            print "Creating %s..." % outFile
        myFile = codecs.open(outFile, 'w', "utf-8")
        
    
    if verbose:
        print "--- Listing numbers..."
        print "--- URL: %s&limit=%s" % (apiList, limit)
        
    response = getResponse("%s&limit=%s" % (apiList, limit), verbose)
    
    if apiFormat == "json":
        data = json.loads(response)
    elif apiFormat == "xml":
        xmlRoot = ET.fromstring(response)  # read xml
        
        for xmlChild in xmlRoot:
            name = ""
            number = ""
            if verbose:
                print "%s" % (xmlChild.tag)
            for xmlInnerChild in xmlChild:
                if xmlInnerChild.tag.lower() == "number":
                    number = xmlInnerChild.text
                    if verbose:
                        print xmlInnerChild.tag
                        print number
                elif xmlInnerChild.tag.lower() == "name":
                    name = xmlInnerChild.text
                    if verbose:
                        print xmlInnerChild.tag
                        print name
                if name and number:
                    numberList.append({'number': number, 'name': name})
                
    for numbers in numberList:
        print numbers
        if outFile:
            if verbose:
                print "Writing %s,%s to file..." % (numbers['number'], numbers['name'])
            myFile.write("%s,%s\n" % (numbers['number'], numbers['name']))
        
    if outFile:            
        myFile.close()
            
    
      
def lookupNumber(number, numberOfCompanies, verbose):
    companyList = []
    
    if verbose:
        print "--- Getting info for %s..." % number
        print "--- URL: %s&number=%s&numberOfCompanies=%s" % (apiSearch, number, numberOfCompanies)
        
    response = getResponse("%s&number=%s&numberOfCompanies=%s" % (apiSearch, number, numberOfCompanies), verbose) 
                    
    if apiFormat == "json":
        data = json.loads(response)
    elif apiFormat == "xml":
        xmlRoot = ET.fromstring(response)  # read xml
        
        for xmlChild in xmlRoot:
            name = ""
            number = ""
            if xmlChild.tag.lower() == "comments":
                comments = xmlChild.text
                print "Comments: %s" % comments
            else:
                if verbose:
                    print xmlChild.tag
            for xmlInnerChild in xmlChild:
                name = ""
                comments = ""
                for xmlInnerInnerChild in xmlInnerChild:
                    if xmlInnerInnerChild.tag.lower() == "name":
                        name = xmlInnerInnerChild.text
                        if verbose:
                            print xmlInnerInnerChild.tag
                            print name
                    elif xmlInnerInnerChild.tag.lower() == "comments":
                        comments = xmlInnerInnerChild.text
                        if verbose:
                            print xmlInnerInnerChild.tag
                            print comments
                    if name and comments:
                        companyList.append({'name': name, 'comments': comments})
        
    for company in companyList:
        print company
        
        
        
        