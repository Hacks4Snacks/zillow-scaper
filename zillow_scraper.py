import argparse
import io
import json
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.request import Request, urlopen

import pandas as pd
import unicodecsv as csv
from lxml import html


def clean(text):
    if text:
        return ' '.join(' '.join(text).split())
    return None


def create_url(zipcode, filter):
    # Creating Zillow URL based on the filter

    if filter == "newest":
        url = f'https://www.zillow.com/homes/for_sale/{zipcode}/0_singlestory/days_sort'
    elif filter == "cheapest":
        url = f'https://www.zillow.com/homes/for_sale/{zipcode}/0_singlestory/pricea_sort/'
    elif filter == "custom":
        url = 'https://www.zillow.com/homes/for_sale/house_type/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Austin%2C%20TX%22%2C%22mapBounds%22%3A%7B%22west%22%3A-98.52625746932375%2C%22east%22%3A-97.0952882310425%2C%22south%22%3A30.147364640687798%2C%22north%22%3A31.07750066604496%7D%2C%22customRegionId%22%3A%22d5d515fee2X1-CR1o8wjt01otvge_u77s3%22%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A650000%7D%2C%22doz%22%3A%7B%22value%22%3A%227%22%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A2133%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%2C%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
    else:
        url = f'https://www.zillow.com/homes/for_sale/{zipcode}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy'
    # print(url)
    return url


def write_data_to_csv(data):
    # saving scraped data to csv

    with open(f'properties-{zipcode}.csv', 'wb') as csvfile:
        fieldnames = ['title', 'address', 'city', 'state', 'postal_code', 'days_on_zillow', 'price',
                      'facts and features', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def get_data_from_json(raw_json_data):
    # getting data from json (type 2 of zillow A/B testing page)

    cleaned_data = clean(raw_json_data).replace('<!--', "").replace("-->", "")
    properties_list = []

    try:
        json_data = json.loads(cleaned_data)
        search_results = json_data.get('cat1').get('searchResults').get('listResults', [])
        # print(search_results)

        for properties in search_results:
            address = properties.get('address')
            property_info = properties.get('hdpData', {}).get('homeInfo')
            city = property_info.get('city')
            state = property_info.get('state')
            postal_code = property_info.get('zipcode')
            days_on_zillow = property_info.get('daysOnZillow')
            price = properties.get('price')
            bedrooms = properties.get('beds')
            bathrooms = properties.get('baths')
            area = properties.get('area')
            info = f'{bedrooms} bds, {bathrooms} ba ,{area} sqft'
            property_url = properties.get('detailUrl')
            title = properties.get('statusText')

            data = {'address': address,
                    'city': city,
                    'state': state,
                    'postal_code': postal_code,
                    'days_on_zillow': days_on_zillow,
                    'price': price,
                    'facts and features': info,
                    'url': property_url,
                    'title': title}
            properties_list.append(data)

        return properties_list

    except ValueError:
        return None


def parse(zipcode, filter=None):
    url = create_url(zipcode, filter)

    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    parser = html.fromstring(webpage)

    # identified as zillow type 2 page
    raw_json_data = parser.xpath('//script[@data-zrr-shared-data-key="mobileSearchPageStore"]//text()')
    return get_data_from_json(raw_json_data)


def send_email():
    # read csv using pandas and then convert the csv to html string
    str_io = io.StringIO()
    df = pd.read_csv(f'properties-{zipcode}.csv')
    df.sort_values(["days_on_zillow"], axis=0, ascending=True, inplace=True)
    df.to_html(buf=str_io, index=False, justify="center")
    table_html = str_io.getvalue()

    sender_email = 'CHANGEME'
    receiver_email = ['CHANGEME']
    password = 'CHANGEME'

    message = MIMEMultipart('alternative')
    message['Subject'] = f'Zillow Property Update {datetime.strftime(datetime.now(), "%m/%d/%Y, %H:%M:%S")}'
    message['From'] = sender_email
    message['To'] = ", ".join(receiver_email)

    html = f"""\
    <html>
      <body>
        <p>MAKE THIS WHATEVER YOU WANT TO HAVE IN THE BODY OF THE EMAIL ABOVE THE RESULT TABLE.</p>
        <p>{table_html}</p>
      </body>
    </html>
    """

    html_body = MIMEText(html, "html")
    message.attach(html_body)

    # send email
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
        
if __name__ == "__main__":

    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('zipcode', help='')
    sortorder_help = """
    available sort orders are :
    newest : Latest property details,
    cheapest : Properties with cheapest price,
    custom : Create custom filter on Zillow and paste contents as custom filter
    """

    argparser.add_argument('sort', nargs='?', help=sortorder_help, default='Homes For You')
    args = argparser.parse_args()
    zipcode = args.zipcode
    sort = args.sort
    #print(f"Fetching data for {zipcode}")
    scraped_data = parse(zipcode, sort)
    if scraped_data:
        # print ("Writing data to output file")
        write_data_to_csv(scraped_data)
    send_email()
