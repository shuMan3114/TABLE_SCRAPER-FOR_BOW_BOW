from TableScraper import TableScraper

f1_wiki = TableScraper("https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions")
f1_wiki.export_csv()