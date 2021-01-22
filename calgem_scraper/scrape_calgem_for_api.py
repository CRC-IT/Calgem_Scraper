import io
import re
import urllib
import urllib3
import pandas as pd
import boto3
import os
import os.path
from bs4 import BeautifulSoup

#get header function
def get_api_data(apiNum):
    # initializing url and soup
    http = urllib3.PoolManager()
    url_api = 'https://secure.conservation.ca.gov/WellSearch/Details?api=########&District=&County=&Field=&Operator=&Lease=&APINum=########&address=&ActiveWell=&ActiveOp=&Location=&sec=&twn=&rge=&bm=&PgStart=0&PgLength=10&SortCol=6&SortDir=asc&Command=Search'
    url_api = url_api.replace("########", apiNum)
    response = http.request('GET', url_api)
    soup = BeautifulSoup(response.data, "html.parser")

    # ================================================= DOWNLOAD PDF DATA ==============================================#

    # getting download link for the pdf
    sep = 'target'
    soup.find_all("a", href=re.compile(r"_DATA_"))
    url_api = str(soup.find_all("a", href=lambda href: href and "_DATA" in href))
    url_api = url_api.strip("[<a href=" "")
    url_api = url_api.split(sep, 1)[0]
    url_api = url_api.replace("\"", "")

    # download the pdf uncomment to save locally
    pdfName = apiNum + '.pdf'
    response = urllib.request.urlopen(url_api)
    p = io.BytesIO(response.read())
    p.seek(0, os.SEEK_END)

    # Upload the pdf for conversion
    s3 = boto3.resource('s3', verify=False)
    s3.Object('crc-convert-pdf', pdfName).put(Body=p.getvalue())

    # ================================================= HEADER DATA ====================================================#
    # collecting all labels from the file
    labels = []
    for label_list in soup.select('label'):
        labels.append(label_list.string)

    # collect all data fields from the file
    data_elems = soup.find_all(class_=["col-sm-1", "col-sm-2", "col-sm-3", "col-sm-4", "col-sm-5"])
    data_fields = []
    data = []
    for data_elem in data_elems:
        data_fields.append(re.sub('<[^>]+>', '', str(data_elem)))
        data = [sub.replace('\n', '').replace('\r', '') for sub in data_fields]

    # removing labels from collected data fields
    new_strings = []
    for x in data:
        # this is ugly but gets the job done find a better solution long-term
        new_string = x.replace("API #", "").replace("Lease", "").replace("Well #", "").replace("County", "").replace(
            "District", "").replace("Operator", "").replace("Field", "").replace("Area", "").replace("Section","").replace(
            "Township", "").replace("Range", "").replace("Base Meridian", "").replace("Well Status", "").replace(
            "Pool WellTypes", "").replace("SPUD Date", "").replace("GIS Source", "").replace("Datum", "").replace(
            "Latitude", "").replace("Longitude", "")
        new_string = new_string.strip()
        new_strings.append(new_string)

    # create the csv for header data
    df = pd.DataFrame()
    df = df.append([labels], ignore_index=True)
    df = df.append([new_strings], ignore_index=True)

    # store csv from dataframe to local machine
    headerDataName = 'headerData_' + apiNum + '.csv'

    # ================================================= HEADER UPLOAD ====================================================#

    # uploading header data to s3 bucket
    output_bucket = 'crcdal-well-data'
    key = 'calgem-webscrape/' + headerDataName
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    s3.Object(output_bucket, key).put(Body=csv_buffer.getvalue())

def validate_api(api):
    if len(api) == 14:
        return api[2:10]
    elif len(api) == 12:
        return api[2:10]
    elif len(api) == 10:
        return api[2:10]
    elif len(api) == 8:
        return api
    else:
        raise ValueError('Unknown API format')
