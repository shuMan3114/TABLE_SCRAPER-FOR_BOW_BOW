from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import re

class TableScraper:
    # Initialisation of table_scraper object
    def __init__(self,link):
        try:
            response = urlopen(link)
        # Handling server errors
        except HTTPError as e:
            print(e)
            return None
        try:
            content = BeautifulSoup(response.read(), 'html.parser')
        # Handling missing tags and attributes  
        except AttributeError as e:
            print(e)
            return None
        #  Assigning the link to the scraper attribute link and the html file to the scraper attribute content
        self.content = content
        self.link = link
    
    # Scraping website for all table titles - table elements which do not have a caption will not be considered as a table ..
    def __initTableTitles__(self):
        # Finds all containers having tag = table
        tables = self.content.findAll('table')
        captionList = {}
        count = 1
        
        for table in tables:
            # Querying through each table to find all <caption></caption> tags which is commonly used to assign table title
            if(table.findAll('th') or table.find('thead')):
                if(not len(table.findAll('caption'))):
                    heading = table.find_previous_sibling(re.compile("^h[1-6]$"))
                    print(heading)
                    if(heading != None):
                        cleanCaption = (heading.text)[0:-6]
                        # print(count,cleanH,sep="\t")
                    else:
                        cleanCaption = " "
                else:
                    captions = list(table.findAll('caption'))
                    print(captions)# Handler for captions returning None/empty list
                    if len(captions):
                        caption = captions[0]# Removes the "\n" at the end of the caption string
                        stripNewLine = str(caption.getText())[:-1]
                    else:
                        stripNewLine = " " # removes all refrencess like [1],[2] by splitting it and then taking the first one
                    captionRefSplit = stripNewLine.split("[")
                    cleanCaption = captionRefSplit[0] # adds to caption dictionary
            else:
                cleanCaption = " "
            count +=1
            captionList[count] = cleanCaption  
        # assgins tableTitles attribute to object
        self.tableTitles = captionList
    
    # Removes all tables which do not have a title
    def __cleanDFs__(self):
        self.__initTableTitles__()
        # Gets all tables in webpage
        dirtyDF = pd.read_html(self.link)
        dfDict = {}
        cleanedTableTitles = []
        count = 0
        for (key,caption) in self.tableTitles.items() :
            if(caption != ' '):
                dfDict[caption] = dirtyDF[count]
                cleanedTableTitles.append(caption)
            count +=1
        self.Tables = dfDict
        self.tableTitles = cleanedTableTitles
    
    # Gets the title of the webpage
    def getTitle(self):
        self.title = self.content.h1.getText()
        print(f"Title of URL is: {self.title}")
    
    # Gets the tables required by the user
    def getTables(self):
        self.__cleanDFs__()
        print("-------TABLES--------")
        captions = self.tableTitles
        count = 1
        # Prints the options to use for each table
        for title in captions:
            print(f"{count} for {title}")
            count +=1
        prompt_str = f"Enter {count+1} to extract specific tables {count+2} to extract range of tables: "
        # Range or specific
        range_or_specific = eval(input(prompt_str))
        if(range_or_specific == (count+1)):
            query_list = eval(input("Enter list of table numbers required: "))
        else:
            lower_lim = int(input("Enter lower limit of range(inclusive): "))
            upper_lim = int(input("Enter upper limit of range(inclusive): "))
            query_list = range(lower_lim,upper_lim+1)
        queried_DF = {}
        for num in query_list:
            queried_DF[captions[num-1]] = self.Tables[captions[num-1]]
        return queried_DF

    #  I give up commenting just read the damm code  
    def export_csv(self,DF_dict={}):
        if(len(DF_dict) == 0):
            DF_dict = self.getTables()
        if(len(DF_dict) > 1):
            verdict = eval(input("Enter 1 to append in same file 2 to create saparate csv files for each: "))
        if(verdict == 1):
            FILE_PATH = input("Enter file path: ")
            for (title,df) in DF_dict.items():
                df.to_csv(FILE_PATH , mode = 'a')
        else:
            loc_verdict = int(input("Enter 1 to export to different directory 2 to export to current directory: "))
            if(loc_verdict == 1):
                DIR_PATH = input("Enter directory path: ")
            else:
                DIR_PATH = ""
            for (title,df) in DF_dict.items():
                PATH = DIR_PATH + re.sub('\W+','', title) + ".csv"
                df.to_csv(PATH)