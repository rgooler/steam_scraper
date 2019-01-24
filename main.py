#!/usr/bin/env python3
import requests
import pymysql.cursors
import pprint
from datetime import datetime
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


def parse_page(page=1):
    # Fetch page
    url = "https://gamesdonequick.com/tracker/donations/?page=%s" % page
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    # Grab the table
    rows = list()
    for row in soup.table.children:
        if row == "\n":
            continue
        if '<thead>' in str(row):
            continue
        # Rip apart the table
        cells = row.findAll("td")
        my_row = dict()
        # donor
        try:
            my_row['donor_id'] = cells[0].a['href'].split('/')[-1]
            my_row['donor_name'] = cells[0].a.text
        except:
            #Anonymous
            my_row['donor_id'] = None
            my_row['donor_name'] = None
        # received
        dt = cells[1].text.strip()
        my_row['received'] = datetime.strptime(dt, "%m/%d/%Y %H:%M:%S +0000")
        # donation
        my_row['donation_id'] = cells[2].a['href'].split('/')[-1]
        my_row['ammount'] = cells[2].text.replace(',','').strip().split('$')[-1]
        # comment
        # - skip -
        rows.append(my_row)
    # Return so we can parse elsewhere
    return rows

def create_donor(conn, row):
    if row['donor_id'] is None:
        return
    with conn.cursor() as cursor:
        # Create a new record
        sql = "REPLACE INTO `donors` (`id`, `name`) VALUES (%s, %s)"
        cursor.execute(sql, (row['donor_id'], row['donor_name']))


def create_donation(conn, row):
    with conn.cursor() as cursor:
        # Create a new record
        sql = "REPLACE INTO `donations` (`id`, `donor_id`, `received`, `ammount`) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (row['donation_id'], row['donor_id'], row['received'].strftime('%Y-%m-%d %H:%M:%S'), row['ammount']))

if __name__ == "__main__":
    # Connect to the database
    conn = pymysql.connect(read_default_file='my.cnf',
                           cursorclass=pymysql.cursors.DictCursor)

    for page in range(2768, 8050):
        print("==[Page %s]==" % page)
        rows = parse_page(page)
        for row in rows:
            print("Donation: %s" % row['donation_id'])
            create_donor(conn, row)
            create_donation(conn, row)
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        conn.commit()