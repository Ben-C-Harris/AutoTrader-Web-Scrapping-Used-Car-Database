# AutoTrader Web Scraping Used Car Database
Web Scraping used to create used car database from https://www.autotrader.co.uk/ which is then dynamically visualised using a bokeh server.

Look at my other repo: https://github.com/Ben-C-Harris/AutoTrader-Used-Car-Price-Prediction to see how I've then used it to make **Used Car Predictions using Machine Learning**.

I've created a database of used cars that have been web scraped from https://www.autotrader.co.uk/ which **includes 67,249 different cars**. The web scraper could be run for longer to recieve over 500,000 used cars if required. I've then created a bokeh server application that enables you to dynamically look at the dataset as you can see in the below video: 

<p align="center"><img src="dynamicBokehAutoTraderDemo.gif" /></p>

A selection of ten random rows of the dataset is as shown below:
```
      Make          Model           Name                                                                Price   Year   Miles    BHP   L   Trans     Fuel   
26935 Jeep          Grand Cherokee  Jeep Grand Cherokee 3.0 CRD V6 Overland 4x4 5dr                     5989.0  2007.0 79800.0  215.0 3.0 Automatic Diesel 
42907 Nissan        Qashqai         Nissan Qashqai 1.6 N-TEC 2WD 5dr                                    8500.0  2012.0 50000.0  113.0 1.6 Manual    Petrol 
11406 Chrysler      300C            Chrysler 300C 3.0 CRD V6 LUX 4dr                                    7495.0  2009.0 42889.0  218.0 3.0 Automatic Diesel 
2541  Audi          A4 Avant        Audi A4 AVANT TFSI SPORT 1.4 5dr                                    17200.0 2016.0 18379.0  148.0 1.4 Manual    Petrol 
63521 Volkswagen    Phaeton         Volkswagen Phaeton 3.0 TDI V6 4MOTION 4dr                           4895.0  2009.0 106000.0 237.0 3.0 Automatic Diesel 
2176  Audi          A3 Cabriolet    Audi A3 Cabriolet 1.8 TFSI Sport 2dr                                3965.0  2008.0 148082.0 158.0 1.8 Manual    Petrol 
10113 BMW           X5M             BMW X5 M 4.4 5dr                                                    54991.0 2016.0 14808.0  575.0 4.4 Automatic Petrol 
13550 Citroen       Ds3 Cabrio      Citroen DS3 CABRIO 1.6 DSPORT PLUS 3d 155 BHP * 3 MONTHS WARRANTY * 5995.0  2013.0 49000.0  153.0 1.6 Manual    Petrol 
35065 Mercedes-Benz A Class         Mercedes-Benz A Class A180 CDI Sport Edition 5dr - SAT NAV - …      12318.0 2015.0 45056.0  109.0 1.5 Manual    Diesel 
14909 Dacia         Sandero Stepway Dacia Sandero Stepway 0.9 Ambiance 5dr                              5995.0  2014.0 27000.0  90.0  0.9 Manual    Petrol 
```

# Dependencies
    requests
    json
    pandas
    BeautifulSoup
    numpy
    bokeh

# How to run
This process is run in three parts.

NB - if in anaconda ensure PATH is correct
   running server in commandline

model is simple to run and is commented to help share what is actually going on. Ensure you have the above packages installed in your environment and download/clone:

      
      carPricePredictRegression.py
      fullDataSet.pkl (Must be within dataSet dir as in GitHub folder layout)















