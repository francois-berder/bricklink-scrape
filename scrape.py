#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import argparse
import csv
import multiprocessing
import sys

BRICKLINK_URL_FORMAT = "http://www.bricklink.com/catalogPG.asp?S={}"


class LegoSet:
    def __init__(self, n, name, qty, rrp, price):
        self.n = n
        self.name = name
        self.quantity = qty
        self.rrp = rrp
        self.price = price


def get_price(driver, n):
    driver.get(BRICKLINK_URL_FORMAT.format(n))
    tables = driver.find_elements(By.TAG_NAME, "TABLE")
    if not tables:
        raise RuntimeError('No tables')
    rows = tables[0].find_elements(By.TAG_NAME, "tr")
    if not rows:
        raise RuntimeError('No rows')
    cols = rows[0].find_elements(By.TAG_NAME, "td")
    if not cols:
        raise RuntimeError('No cols')
    content = cols[0].text
    idx = content.find('Avg Price: EUR ')
    if idx < 0:
        raise RuntimeError('No price')
    price = content[idx+len('Avg Price: EUR '):-1]
    return float(price[:price.find('\n')])


def process_lego_sets(sets):
    if not sets:
        return sets

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    for lego_set in sets:
        print('Fetching price for {} set'.format(lego_set.name))
        try:
            lego_set.price = get_price(driver, lego_set.n)
        except RuntimeError as err:
            print('Failed to fetch price for {} set. Reason: {}'.format(name, err))
    driver.quit()
    return sets


def print_stats(sets):
    if not sets:
        print('Empty Lego set collection')
        return

    titles = ['Number', 'Name', 'Quantity',
              'RRP (EUR)', 'Price per set (EUR)', 'Profit per set (EUR)']
    line = '|'.join(str(x).ljust(24) for x in titles)
    print(line)
    print('-' * len(line))
    for lego_set in sets:
        rrp = lego_set.rrp if lego_set.rrp else '?'
        price = lego_set.price if lego_set.price else '?'
        profit = round(lego_set.price - lego_set.rrp,
                       2) if lego_set.rrp and lego_set.price else '?'
        data = [lego_set.n, lego_set.name,
                lego_set.quantity, rrp, price, profit]
        line = '|'.join(str(x).ljust(24) for x in data)
        print(line)

    total_price = 0.0
    for lego_set in sets:
        if not lego_set.price:
            break
        total_price += lego_set.price * lego_set.quantity
    else:
        print('Total price of the collection: {} EUR'.format(round(total_price, 2)))


def split_list(lego_collection, n):
    return (lego_collection[i::n] for i in range(n))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('collection_file', help='CSV file describing Lego collection')
    args = parser.parse_args()

    lego_collection = []

    # Parse Lego collection from Brickset CSV file
    with open(args.collection_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            n = line['Number']
            name = line['Set name']
            quantity = int(line['Qty owned'])
            if line["RRP (EUR)"]:
                rrp = float(line["RRP (EUR)"])
            else:
                rrp = None
            lego_collection.append(LegoSet(n, name, quantity, rrp, None))

    # Fetch price with multiple threads
    cpu_count = multiprocessing.cpu_count()
    split_lego_collection = list(split_list(lego_collection, cpu_count))
    executor = ThreadPoolExecutor(max_workers=cpu_count)
    future_to_lego_collection = {executor.submit(
        process_lego_sets, chunk) for chunk in split_lego_collection}
    wait(future_to_lego_collection)

    print_stats(lego_collection)
