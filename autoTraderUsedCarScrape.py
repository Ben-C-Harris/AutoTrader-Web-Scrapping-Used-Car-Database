import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

USING_PROXY = False
PROXY_SETTINGS = {"https": "https://XXX.X.X.X:XXXXX"}
PKL_READ_FILE = "autoTraderMakeAndModel.pkl"
PKL_OUT_FILE = "usedCarAutoTraderOutput.pkl"
MAX_PAGE_NUM = 30

class AutoTraderUsedCarScraper():
    
        def __init__(self, PROXY_SETTINGS, PKL_READ_FILE, PKL_OUT_FILE):
            self.proxySettings = PROXY_SETTINGS
            self.pklIn = PKL_READ_FILE
            self.pklOut = PKL_OUT_FILE
            self.maxPageNum = MAX_PAGE_NUM
            self.useProxy = USING_PROXY
          
            
        '''
        Create URL required for each make and model based upon AutoTrader.co.uk's website structure
        '''
        def urlModelCreate(self, make, model):           
            urlP1 = 'https://www.autotrader.co.uk/car-search?sort=relevance&postcode=SW1A%201AA&radius=1500&onesearchad=Used&onesearchad=Nearly%20New&onesearchad=New&make='
            urlP2 = '&model='
            urlP3 = '&page='
            fullURL = urlP1 + str(make.upper()) + urlP2 + str(model.upper()) + urlP3
            return fullURL
        
        
        '''
        Create list of all URLs required for relevant make and model upto the max pages requested
        '''
        def urlPages(self, fullURL, pagesEnd):
            urlSet = []
            startPage = 1
            while startPage <= pagesEnd:
                url = fullURL + str(startPage)
                urlSet.append(url)
                startPage = startPage+1
            return urlSet
        
        
        '''
        Web scrape all required pages - any failed requests are logged.
        Note: failed requests can happen for several reasons - main two are:
            1. Blocked/Kicked from website
            2. You didn't set the proxy settings properly
        '''
        def scrapePage(self, urlSet, makeModel, make, model):
            soupSet = []
            problemRows = []
            for i, url in enumerate(urlSet):
                try: # Try as not always sucessful...
                    if self.useProxy:
                        page = requests.get(url, proxies = self.proxySettings)
                    else:
                        # Headers are sensible to add as it increases success rate
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36','Content-Type': 'text/html',}
                        page = requests.get(url, headers=headers)
                     
                    soup = BeautifulSoup(page.text, 'html.parser') # Parse from BS Object to HTML
                    soupSet.append(soup)           
                    print("Request successful on page: " + str(i+1))

                except: # Failed request - print to console and log
                    print("--------- FAILED REQUEST ON PAGE: " + str(i) + " ---------")
                    print("--------- ENSURE PROXY SERVER SETTINGS ARE ACCURATE ---------")
                    problemRows.append(["Data Retrieval Issue", makeModel[0], make, model])
                    pass   
            
            return soupSet, problemRows
        
        
        '''
        Strip the car name and get a list of all its main attributes from soup html. 
        
        Simplified example of HTML below:

            <div class="information-container">
            <h2 class="listing-title title-wrap">
            <a class="js-click-handler Audi SQ5 3.0 BiTDi Tiptronic quattro (s/s) 5dr</a>
            </h2>
            <p class="listing-attention-grabber ">**300 BHP Four Wheel Drive**</p>
            <ul class="listing-key-specs ">
                <li>2016 (16 reg)</li>
                <li>SUV</li>
                <li>90,000 miles</li>
                <li>3.0L</li>
                <li>322bhp</li>
                <li>Automatic</li>
                <li>Diesel</li>
            </ul>               
        '''
        def getNamesFeatures(self, soup):
            names = []
            features = []
            for line in soup.find_all(class_="information-container"):
                name = line.find('a')
                feature = line.find('ul')
                names.append(name.text)
                features.append(feature.text)     
            return names, features
        
        
        '''
        Strip the car price out of the soup HTML
        
        Simplified example of HTML below:
        
        <a class="js-click-handler listing-fpa-link listings-price-link tracking-standard-link">

                <div data-label="search appearance click" class="vehicle-price">£21,950</div>
        </a>                
        '''
        def getPrices(self, soup):
            prices = []
            for line in soup.find_all(class_="vehicle-price"):
                value_arb = line.text[1:]
                value_arb2 = value_arb.split('£')
                int_val = float(value_arb2[-1].replace(',', '')) 
                prices.append(int_val)
            return prices
        
        
        '''
        Break groups of features down into discrete feature components
        '''
        def getFeaturesList(self, features):
            features_list = []
            for row in features:
                features_list.append(row.split("\n")) # Split by new line
            return features_list


        '''
        Turn the pulled features into intelligible attributes for the car.
        This logic is derived from the specific needs of the dataset but will
        work throughout the dataset and has been tested to this effect.
        
        Examples:
            Miles if contains "miles"
            Litres if it contains "l" BUT is not a registration such as L Reg, and also not a limosine
            Reg if it contains "reg" or if it contains 19XX or 20XX such as 1998 or 2019
            Bhp if it contains "bhp"
            Trans if it contains a transmission type
            Fuel if it contains a fuel type
        '''
        def getAttributeValues(self, item):
            miles = []
            litres = []
            reg = []
            bhp = []
            trans = []
            fuel = []
            for row in item:
                if "miles" in row:
                    arb1 = row[:-6]
                    miles = float(arb1.replace(',', '')) 
                elif "L" in row and 'reg' not in row and "imo" not in row: #"imo" added due to Limosine issue...
                    arb2 = row[:-1]
                    litres = float(arb2)
                elif ( ("reg" in row) or (len(row)==4 and (row[:-2]=="19")) or (len(row)==4 and (row[:-2]=="20")) ):
                    #print("FOUND REG'Y")
                    reg = int(row[0:4])
                elif "bhp" in row:
                    arb4 = row[:-3]
                    bhp = float(arb4)
                elif "Manual" in row or "Automatic" in row:
                    trans = row
                elif "Petrol" in row or "Diesel" in row:
                    fuel = row

            group = [reg, miles, bhp, litres, trans, fuel]
            return group


        '''
        If any feature attributes remain unfilled then fill it with NAN
        '''
        def nanFill(self, group):
            group_NAN = [] # empty filled with NAN
            for attribute in group:
                if attribute == []:
                    item = np.nan
                    group_NAN.append(item)
                else:
                    group_NAN.append(attribute)  
            return group_NAN
        
        
        '''
        Extract the feature atrributes for the database for a given make and model
        '''
        def extractAttributes(self, soup_set):
            dfIter = pd.DataFrame([])
            for soup in soup_set:            
                
                # Get attributes
                names, features = self.getNamesFeatures(soup)
                prices = self.getPrices(soup)
                features_list = self.getFeaturesList(features)
                   
                # Adjust attribute features including filling Null attributes
                full_feature_list = []
                for item in features_list:                    
                    group = self.getAttributeValues(item)
                    groupNANFill = self.nanFill(group)
                    full_feature_list.append(groupNANFill)
                  
                # Put into df with Transform required due to columns/rows    
                dfNP = pd.DataFrame([names, prices]).T
                dfNP.columns = ['Name','Price']
                
                # Place  attributes into df
                dfFeat = pd.DataFrame(full_feature_list)
        
                # Concat all attributes
                df_group = pd.concat([dfNP,dfFeat], axis=1, sort=False)
                
                # Append for output
                dfIter = dfIter.append(df_group, ignore_index=True, sort=False)
                    
            return dfIter


        '''
        Reformat the df to have correct naming and index.
        Also drop any rows that contain a NAN.
        
        Note: NAN variables could be a good place for future work.
              Within Machine Learning NAN values can be dealt with 
              in different ways. This is the simple remove method,
              in future an Imputation would be good to look into
        '''
        def dfGoodFormat(self, dfIter, make, model):
            print("Data Found As Expected - Well Done Bot...")
            # Set column names
            dfIter.columns = ['Name',
                          'Price',
                          'Year',
                          'Miles',
                          'BHP',
                          'L',
                          'Trans',
                          'Fuel']
            
            # Drop any cars with NAN values - See above Note on Imputation for future work
            dfIter = dfIter.dropna()
            dfIter = dfIter.drop_duplicates(subset=None, keep='first', inplace=False)
            
            dfIter['Make'] = make
            dfIter['Model'] = model
        
            dfIter = dfIter[['Make', 'Model', 'Name',
                          'Price',
                          'Year',
                          'Miles',
                          'BHP',
                          'L',
                          'Trans',
                          'Fuel']]
            return dfIter
            

# ============================================================================= 
# =============================================================================


'''
Deliver functional webscraping of AutoTrader to find all Makes and associated
models of used car avaliable at the time of webscraping.
'''
def performUsedCarWebScrape():
    # Define class object
    webScraper = AutoTraderUsedCarScraper(PROXY_SETTINGS, PKL_READ_FILE, PKL_OUT_FILE)
    
    # Read input
    dfMakeModel = pd.read_pickle(PKL_READ_FILE)
    
    # Create subset of run for debugging etc. 
    # dfMakeModel.iloc[:] for everything or dfMakeModel.iloc[173:178] for small subset
    dfMakeModel = dfMakeModel.iloc[:]
    
    dfAllData = pd.DataFrame([])
    dfIterSave = pd.DataFrame([]) #This is as an iterative data save to be safe!
    issues = []
    
    for makeModel in dfMakeModel.iterrows(): # iterate through all makes and models
        make = makeModel[1][0]
        model = makeModel[1][1]
        
        print('You have started to scrape the: ' + str(make) + ' ' + str(model))
        
        # Create unique URL
        fullURL = webScraper.urlModelCreate(make, model)
        
        # List of URLs for each page requested
        webpageSet = webScraper.urlPages(fullURL, MAX_PAGE_NUM)
        
        # Successful and failed AutoTrader website requests
        soupSet, failedRequests = webScraper.scrapePage(webpageSet, makeModel, make, model)
        
        # Log any issues
        issues.extend(failedRequests)
        
        # Pull all attributes from AutoTrader HTML
        dfIter = webScraper.extractAttributes(soupSet)

        if dfIter.shape[0] != 0: # If dfIter contains one car or more
            # Format df
            dfIter = webScraper.dfGoodFormat(dfIter, make, model)

            # Save data as you go - sensible in case of internet issues...
            dfIterSave = dfIterSave.append(dfIter, ignore_index=True, sort=False)
            dfIterSave.to_pickle("interSave.pkl")      
            dfIterSave.to_csv("interSave.csv")      
            
            # Append to overall df
            dfAllData = dfAllData.append(dfIter, ignore_index=True, sort=False)
            
        if dfIter.shape[0] == 0: # No cars found
            # Log any issues
            issues.append(["No Data Found", makeModel[0], make, model])
            print("---------- No Data Recieved For: " + str(make) + " " + str(model) + " ---------")
                   
    dfAllData.to_pickle(PKL_OUT_FILE)
    dfAllData.to_csv("usedCarAutoTraderOutput.csv")
            

if __name__ == "__main__":
    performUsedCarWebScrape()


