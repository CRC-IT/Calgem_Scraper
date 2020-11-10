# This is the second draft of the calgem scraper
import csv
import io
import re
import urllib

import urllib3
import pandas as pd
import boto3
from botocore.client import ClientError
import numpy as np

import os
import os.path
from botocore.exceptions import ClientError, NoCredentialsError
from bs4 import BeautifulSoup

#creating a dictionary for results
def Convert(lst1, lst2):
    results = {lst1[i]: lst2[i] for i in range(0, len(lst1), 1)}
    return results

#get header function
def get_api_data():

    #initializing url and soup
    http = urllib3.PoolManager()
    url = 'https://secure.conservation.ca.gov/WellSearch/Details?api=02927040&District=&County=029&Field=228&Operator=&Lease=&APINum=&address=&ActiveWell=true&ActiveOp=true&Location=&sec=&twn=&rge=&bm=&PgStart=0&PgLength=10&SortCol=6&SortDir=asc&Command=Search'
    #url with api
    url_api = 'https://secure.conservation.ca.gov/WellSearch/Details?api=02927040&District=&County=&Field=&Operator=&Lease=&APINum=02927040&address=&ActiveWell=true&ActiveOp=true&Location=&sec=&twn=&rge=&bm=&PgStart=0&PgLength=10&SortCol=6&SortDir=asc&Command=Search'
    response = http.request('GET', url_api)
    soup = BeautifulSoup(response.data, "html.parser")

    #pulls elems of the header
    job_elems = soup.find_all(class_="panel-body")

    #================================================= DOWNLOAD PDF DATA ==============================================#

    #getting url from the pdf
    sep = 'target'
    soup.find_all("a", href=re.compile(r"_DATA_"))
    url = str(soup.find_all("a", href=lambda href: href and "_DATA" in href))
    url = url.strip("[<a href=" "")
    url = url.split(sep, 1)[0]
    url = url.replace("\"", "")
    #print(url)

    #download the pdf uncomment to save locally
    urllib.request.urlretrieve(url, "02927040.pdf")

    s3 = boto3.resource('s3', verify = False)
    s3.meta.client.upload_file('02927040.pdf', 'crc-convert-pdf', '02927040.pdf')

    #================================================= HEADER DATA ====================================================#
    #collecting all labels from the file
    labels = []
    for label_list in soup.select('label'):
        labels.append(label_list.string)
        #print(labels)

    #collect all data fields from the file
    data_elems = soup.find_all(class_=["col-sm-1","col-sm-2","col-sm-3","col-sm-4","col-sm-5"])
    data_fields = []
    data = []
    for data_elem in data_elems:
        data_fields.append(re.sub('<[^>]+>', '', str(data_elem)))
        data = [sub.replace('\n', '').replace('\r', '') for sub in data_fields]

    #removing labels from collected data fields
    new_strings = []
    for x in data:
        #this is ugly but gets the job done find a better solution long-term
        new_string = x.replace("API #", "").replace("Lease","").replace("Well #","").replace("County", "").replace("District", "").replace("Operator", "").replace("Field", "").replace("Area", "").replace("Section","").replace("Township","").replace("Range","").replace("Base Meridian","").replace("Well Status","").replace("Pool WellTypes","").replace("SPUD Date","").replace("GIS Source","").replace("Datum","").replace("Latitude","").replace("Longitude","")
        new_string = new_string.strip()
        new_strings.append(new_string)

    #create the csv for header data
    df = pd.DataFrame()
    df = df.append([labels],ignore_index=True)
    df = df.append([new_strings],ignore_index=True)

    #create csv from dataframe
    df.to_csv('sample.csv')

    #old function for creating a dictionary from the two lists
    #print(Convert(labels, new_strings))

    #================================================= HEADER UPLOAD ====================================================#

    #uploading header data to s3 bucket
    s3.meta.client.upload_file('sample.csv', 'crcdal-well-data', 'calgem-webscrape/sample.csv')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_api_data()

#assign variables to data from each field <--DONE
#have a function to easily print header data <-- DONE
#download the pdf to a given folder <-- DONE
#collect all labels from header info and store them in an array <-- DONE
#change header output to datafram csv <-- DONE
#upload the header csv to the location Nathan specifies <-- DONE
#output downloaded file to convert folder <-- DONE

#accepts api number as a function input <-- check with Nathan on functionality
#accept a list of api's as input <-- check with Nathan
#automate the output of header csv to be the name of the api <-- check with Nathan

