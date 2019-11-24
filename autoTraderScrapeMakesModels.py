import requests
import json
import pandas as pd

'''
Web scraping for website: https://www.autotrader.co.uk/

This Class is for web scraping and writing to PKL file all the makes and models
of used cars that AutoTrader currently has listed on its website.

To get a closer look at what is happenening within the request and JSON sections
of this script, I would advise looking into your network monitor and JSON/HTML browser.

This can be done through using: CNTRL+SHIFT+E or CTRL-U for JSON/HTML browser while more info
can be found at places such as (Your browser may be different):
    https://developer.mozilla.org/en-US/docs/Tools/Network_Monitor
'''

USING_PROXY = False
PROXY_SETTINGS = {"https": "https://XXX.X.X.X:XXXXX"}
OUTPUT_PKL_FILE = "dataMakeAndModelPickle.pkl"

class AutoTraderMakesAndModelsWebScraper():
    
        def __init__(self, PROXY_SETTINGS):
            self.proxySettings = PROXY_SETTINGS
            self.pklOut = OUTPUT_PKL_FILE
           
            
        '''
        Method that performs an active request on website for the makes avaliable on AutoTrader
        '''
        def requestMakes(self, proxySettings):
            # request page and place into structured JSON
            if USING_PROXY:
                req = requests.get("https://www.autotrader.co.uk/json/search/options?advertising-location=at_cars", proxies = proxySettings)
            else:
                req = requests.get("https://www.autotrader.co.uk/json/search/options?advertising-location=at_cars")
            structDat = json.loads(req.text)
            return structDat
        
        
        '''
        Parse structured request data and deliver the actual list of unique makes avalaible
        options and make within structuredRequest are the subsets where the data contains the makes
        '''
        def parseMakes(self, structuredRequest):
            makes = []
            for make in structuredRequest["options"]["make"]:
                makes.append(make["displayName"])
                print("Found make: " + make["displayName"])
            return makes
        
        
        '''
        Request and parse models for each previously found car make
        options and make within structDat are the subsets where the data contains the makes
        '''
        def reqAndParseModels(self, makes, proxySettings):
            dfMakeModel = pd.DataFrame([])
            for make in makes:
                # Create url for make so you can then pull from that webpage
                url_p1 = "https://www.autotrader.co.uk/json/search/options?advertising-location=at_cars&postcode=DE24%208QG&make="
                url_p2 = str(make)
                url_p3 = "&price-search-type=total-price"
                url = url_p1 + url_p2 + url_p3
                
                # request page and place into structured JSON
                if USING_PROXY:
                    req = requests.get(url, proxies = proxySettings)
                else:
                    req = requests.get(url)

                structDat = json.loads(req.text)
                
                # Go through structured list for one Make and find every 
                # associated model. i.e. Make = [BMW] thus Model =  [M3, M5, X3, ...]
                for model in structDat["options"]["model"]:
                    print("Found make: " + str(make) + " and model: " + model["displayName"])
                    makeModelPair = [make, model["displayName"]] # Create list pair
                    dfMakeModelPair = pd.DataFrame(makeModelPair).T # transform into df include .T for columns into rows
                    dfMakeModel = dfMakeModel.append(dfMakeModelPair)
             
            # Name columns and reindex df    
            dfMakeModel.columns = ["Make", "Model"]
            dfMakeModel = dfMakeModel.reset_index(drop=True)
            
            return dfMakeModel


# ============================================================================= 
# =============================================================================


'''
Deliver functional webscraping of AutoTrader to find all Makes and associated
models of used car avaliable at the time of webscraping.
'''
def performMakeModelWebScrape():
    # Define class object
    webScraper = AutoTraderMakesAndModelsWebScraper(PROXY_SETTINGS)
    
    # Request and Parse Makes from AutoTrader website
    makesRequest = webScraper.requestMakes(webScraper.proxySettings)
    makes = webScraper.parseMakes(makesRequest)
    
    # Request and Parse all associated Models for previously found Makes
    dfMakeModel = webScraper.reqAndParseModels(makes, webScraper.proxySettings)
    
    # Save df to PKL
    dfMakeModel.to_pickle(webScraper.pklOut)    
    dfMakeModel.to_csv("AutoTraderMakesModels.csv")


if __name__ == "__main__":
    performMakeModelWebScrape()