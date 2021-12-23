#!/usr/env python3

import argparse
import csv
import locale
import logging
import requests

from bs4 import BeautifulSoup
from datetime import timedelta, date, datetime
from pathlib import Path
from typing import List, Dict


class Extractor:
  def __init__(self, html: bytes):
    self.html = html
    self.soup = BeautifulSoup(self.html, 'html.parser')

  @property
  def objects(self):
    description = self.soup.find_all("p", {"class": "teaser-extended-text"})[0].text.strip()
    assert "Diesmal mit folgenden Objekten" in description
    description = description.replace("Diesmal mit folgenden Objekten: ", "")
    objects = description.split(", ")
    last = objects[-1]
    objects.pop()
    objects.extend(last.split(" und "))
    return objects

  @property
  def date(self):
    string = self.soup.find_all("div", {"class": "teaser-extended-info"})[0].text.strip()
    return datetime.strptime(string, "%d.%m.%Y").date()

  @property
  def length(self):
    string = self.soup.find_all("dd", {"class": "teaser-info"})[0].text.strip()
    length = string.split(" ")[0]
    assert length.isnumeric()
    return length


class Aggregator:
  def __init__(self):
    self.objects: Dict[date, List[str]] = dict()

    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

  def write_to_csv(self, filename: Path):
    with open(filename, "w") as file:
      csv_writer = csv.writer(file, dialect=csv.Dialect.delimiter)
      csv_writer.writerow(["date", "object"])
      csv_writer.writerows(self._get_objects_pivot())

  def _get_objects_pivot(self):
    objects_pivot = []
    for date, objects in self.objects.items():
      for object in objects:
        objects_pivot.append((date, object))
    return objects_pivot

  def _generate_record_url(self, date: date):
    return f"https://www.zdf.de/teaserElement?assetId=bares-fuer-rares-vom-{date.strftime('%d-%B-%Y').lower()}-100"

  def _retrieve_record(self, date: date):
    response = requests.get(self._generate_record_url(date))
    if response.status_code == 200:
      return response.content
    else:
      return None

  def _extract_from_record(self, html: bytes):
    extractor = Extractor(html)
    return extractor.date, extractor.objects

  def add_record(self, date: date):
    logging.info(f"Adding record {date}")

    html = self._retrieve_record(date)
    if html:
      record_date, objects = self._extract_from_record(html)
      assert record_date == date
      self.objects[date] = objects

  def _generate_dates_since(self, date_since: date):
    date = date_since
    step = timedelta(days=1)

    while date < date.today():
      yield date
      date += step

  def add_all_records_since(self, date_since: date):
    for date in self._generate_dates_since(date_since):
      self.add_record(date)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Scrape records of "Bares für Rares"')
  parser.add_argument('since', type=date.fromisoformat, help='Start date to start scraping from')
  parser.add_argument('output', type=Path, help='Path of output csv')
  args = parser.parse_args()

  logging.getLogger().setLevel(logging.INFO)

  aggregator = Aggregator()
  aggregator.add_all_records_since(args.since)
  #print(aggregator.objects)
  aggregator.write_to_csv(args.output)
