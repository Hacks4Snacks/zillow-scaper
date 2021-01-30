# Minimal Zillow Scraper

This script will scrape Zillow based on a zip code or custom search parameters. Custom search parameters must first be created on Zillow, then the created URL string can be copied and placed as a filter within the script (example in script).

## Advisory

Be advised, Zillow can detect scrapers/bots and is perpetually changing, so the functionality of this script could cease at any time. This script was created out of neccessity due to how competitive the market is
at this time, so the code isn't perfect and may be a bit fragile and lacking useful features or informational items.

### Fields 

This Zillow scraper can extract the fields below:

1. Title (Status)
2. Address
3. City
4. State
5. Zip Code
6. Days on Zillow
7. Price
8. Facts and Features
9. URL

## Running the scraper
The script must be run with arguments for zip code and sort. The sort argument has the options ‘newest’, ‘cheapest’, and 'custom' listings available. 
However, the custom URL is placed as an example filter within the script, so it must be altered to meet specific needs. Additionally, when using the custom filter the zip code becomes useless and just servers as a positional parameter that can be anything.

Example - To run the script using a custom URL pulled from a search created on Zillow.com: 

```
python3 zillow_scraper.py austin custom
python3 zillow_scraper.py 78634 newest
```

Personally, I set this script as a CRON job to run every six (6) hours to minimize the chance of getting blocked, but use as desired.

## Sample Output

This will create a csv file and can be configured to send an email:

Filename - properties-austin.csv
Filename - properties-78634.csv (example output not shown)

title,address,city,state,postal_code,days_on_zillow,price,facts and features,url


Active,"1565 W Pflugerville Pkwy, Pflugerville, TX 78660",Pflugerville,TX,78660,0,"$595,000","4 bds, 3.0 ba ,2394 sqft",https://www.zillow.com/homedetails/1565-W-Pflugerville-Pkwy-Pflugerville-TX-78660/29452977_zpid/

Active,"8312 Turning Trl, Austin, TX 78737",Austin,TX,78737,0,"$575,000","3 bds, 3.0 ba ,2522 sqft",https://www.zillow.com/homedetails/8312-Turning-Trl-Austin-TX-78737/120895471_zpid/

Active,"3508 Winter Wren Way, Pflugerville, TX 78660",Pflugerville,TX,78660,0,"$550,000","5 bds, 3.0 ba ,2700 sqft",https://www.zillow.com/homedetails/3508-Winter-Wren-Way-Pflugerville-TX-78660/145657488_zpid/
