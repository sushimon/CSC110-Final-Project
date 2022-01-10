"""CSC110 Fall 2021: Project Phase 2 - Loading and Cleaning Climate Data

Module Description
==================

This module contains dataclasses and functions for loading and cleaning the climate data from the
csv files. There are two dataclasses which store yearly and monthly climate data.

The data sets being used include:

- Yearly CO2 mean concentrations (from NOAA)
- Monthly CO2 mean concentrations (from NOAA)
- Yearly and monthly temperature anomaly data (from NOAA)

Copyright and Usage Information
===============================

All forms of distribution of this code, whether as given or
with any changes, are expressly prohibited.

This file is Copyright (c) 2021 Richard Shi.
"""
import os
from dataclasses import dataclass
from typing import Optional
import csv

# Constants for the csv file locations
ANNUAL_CO2_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\co2_annmean_mlo.csv'
ANNUAL_TEMP_ANOMALY_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\annual_temp_' \
                                                                         'anomalies.csv'
MONTHLY_CO2_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\co2_mm_mlo.csv'
MONTHLY_TEMP_ANOMALY_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\monthly_temp_' \
                                                                          'anomalies.csv'


@dataclass
class YearlyMetrics:
    """A bundle of yearly climate data that was measured by NOAA and our own calculated climate
    data.

    Instance Attributes:
        - year: The year that this entry of climate data was taken.
        - co2: The annual mean CO2 concentrations in ppm (parts per million).
        - temp_anomaly: The recorded temperature anomaly (the change in temperature in comparison to
        the 20th century average global temperature) in degrees Celsius. Initially set to None.
        - temp: The recorded average global temperature in degrees Celsius. It is calculated by
        adding temp_anomaly to the 20th century average global temperature (13.9 degrees Celsius).
        Initially set to None.
        - calculated_temp: The calculated temperature in degrees Celsius. Initially set to None.
        - calculated_temp_anomaly: The calculated temperature anomaly in degrees Celsius. It is
        calculated by finding the difference between calculated_temp and the 20th century average
        global temperature (13.9 degrees Celsius). Initially set to None.

    Representation Invariants:
        - self.year >= 1959

    Sample Usage:
    >>> data_for_1960 = YearlyMetrics(1960, 316.91)
    >>> data_for_1960.temp_anomaly is None  # Illustrating default values
    True
    >>> data_for_1960.temp is None
    True
    >>> data_for_1960.calculated_temp is None
    True
    >>> data_for_1960.calculated_temp_anomaly is None
    True
    """
    year: int
    co2: float
    temp_anomaly: Optional[float] = None
    temp: Optional[float] = None
    calculated_temp: Optional[float] = None
    calculated_temp_anomaly: Optional[float] = None


@dataclass
class MonthlyMetrics:
    """A bundle of monthly climate data that was measured by NOAA and our own calculated climate
    data.

    Instance Attributes:
        - year: The year that this entry of climate data was taken.
        - month: The month of the year (January is 1 and December is 12)
        - co2: The monthly mean CO2 concentrations in ppm (parts per million).
        - temp_anomaly: The recorded temperature anomaly (the change in temperature in comparison to
        the 20th century average global temperature) in degrees Celsius. Initially set to None.
        - temp: The recorded average global temperature in degrees Celsius. It is calculated by
        adding temp_anomaly to the 20th century average global temperature (13.9 degrees Celsius).
        Initially set to None.
        - calculated_temp: The calculated temperature in degrees Celsius. Initially set to None.
        - calculated_temp_anomaly: The calculated temperature anomaly in degrees Celsius. It is
        calculated by finding the difference between calculated_temp and the 20th century average
        global temperature (13.9 degrees Celsius). Initially set to None.

    Representation Invariants:
        - self.year >= 1959
        - 1 <= self.month <= 12

    Sample Usage:
    >>> data_for_1960 = MonthlyMetrics(1960, 1, 316.43)
    >>> data_for_1960.temp_anomaly is None  # Illustrating default values
    True
    >>> data_for_1960.temp is None
    True
    >>> data_for_1960.calculated_temp is None
    True
    >>> data_for_1960.calculated_temp_anomaly is None
    True
    """
    year: int
    month: int
    co2: float
    temp_anomaly: Optional[float] = None
    temp: Optional[float] = None
    calculated_temp: Optional[float] = None
    calculated_temp_anomaly: Optional[float] = None


def load_yearly_data(filename1: str, filename2: str) -> list[YearlyMetrics]:
    """Returns a list of YearlyMetrics objects based on data in <filename1> and <filename2> which
    correspond to co2_annmean_mlo.csv and annual_temp_anomalies.csv.

    The data from the two data sets will provide the year, co2, and temp_anomaly values. The temp
    value will be calculated by adding temp_anomaly to the 20th century average global temperature
    (13.9 degrees Celsius). The calculated_temp and calculated_temp_anomaly values will initially be
    set to 0.0 and will be mutated later.

    >>> data = load_yearly_data(ANNUAL_CO2_FILE, ANNUAL_TEMP_ANOMALY_FILE)
    >>> len(data) == 62  # Verifying all the data from 1959-2020 was correctly parsed from the file
    True
    >>> data[0].year == 1959  # Verifying the first YearlyMetrics object is data from 1959
    True
    >>> data[61].year == 2020  # Verifying the last YearlyMetrics object is data from 2020
    True
    """
    # ACCUMULATOR metrics_so_far: The YearlyMetrics parsed from the data sets so far
    metrics_so_far = []

    with open(filename1) as f:
        reader = csv.reader(f, delimiter=',')
        # Skipping unnecessary lines
        for _ in range(56):
            next(reader)

        for row in reader:
            assert len(row) == 3, 'Expected each row to contain 3 elements.'
            year = int(row[0])
            if 1959 <= year <= 2020:
                co2 = float(row[1])
                # First, instantiate a YearlyMetrics object with the data from the current data set
                # and we will mutate it to fill in missing data once we parse the other data set.
                metrics_so_far.append(YearlyMetrics(year=year,
                                                    co2=co2
                                                    )
                                      )

    with open(filename2) as f:
        reader = csv.reader(f, delimiter=',')
        # Skipping unnecessary lines
        for _ in range(5):
            next(reader)
        # Add a variable to keep track of the current index to know which YearlyMetrics object to
        # mutate in the list.
        index = 0

        for row in reader:
            assert len(row) == 2, 'Expected each row to contain 2 elements.'
            year = int(row[0])
            if 1959 <= year <= 2020:
                temp_anomaly = float(row[1])
                temp = round(13.9 + temp_anomaly, 2)

                # Mutate the corresponding YearlyMetrics object to fill in the missing data.
                metrics_so_far[index].temp_anomaly = temp_anomaly
                metrics_so_far[index].temp = temp
                index += 1

    return metrics_so_far


def load_monthly_data(filename1: str, filename2: str) -> list[MonthlyMetrics]:
    """Returns a list of MonthlyMetrics objects based on data in <filename1> and <filename2> which
    correspond to co2_mm_mlo.csv and monthly_temp_anomalies.csv.

    The data from the two data sets will provide the year, month, co2, and temp_anomaly values. The
    temp value will be calculated by adding temp_anomaly to the 20th century average global
    temperature (13.9 degrees Celsius). The calculated_temp and calculated_temp_anomaly values will
    initially be set to 0.0 and will be mutated later.

    >>> data = load_monthly_data(MONTHLY_CO2_FILE, MONTHLY_TEMP_ANOMALY_FILE)
    >>> len(data) == 744
    True
    >>> data[0].year == 1959 and data[0].month == 1  # Verifying data
    True
    >>> data[743].year == 2020 and data[743].month == 12  # Verifying data
    True
    """
    # ACCUMULATOR metrics_so_far: The MonthlyMetrics parsed from the data sets so far.
    metrics_so_far = []

    with open(filename1) as f:
        reader = csv.reader(f, delimiter=',')
        # Skipping unnecessary lines
        for _ in range(52):
            next(reader)

        for row in reader:
            assert len(row) == 8, 'Expected each row to contain 8 elements.'
            year = int(row[0])
            if 1959 <= year <= 2020:
                month = int(row[1])
                co2 = float(row[3])
                # First, instantiate a MonthlyMetrics object with the data from the current data set
                # and we will mutate it to fill in missing data once we parse the other data set.
                metrics_so_far.append(MonthlyMetrics(year=year,
                                                     month=month,
                                                     co2=co2
                                                     )
                                      )

    with open(filename2) as f:
        reader = csv.reader(f, delimiter=',')
        # Skipping unnecessary lines
        for _ in range(5):
            next(reader)
        # Add a variable to keep track of the current index to know which MonthlyMetrics object to
        # mutate in the list.
        index = 0

        for row in reader:
            assert len(row) == 2, 'Expected each row to contain 2 elements.'
            year = int(row[0][:4])
            if 1959 <= year <= 2020:
                month = int(row[0][4:])
                temp_anomaly = float(row[1])
                temp = round(13.9 + temp_anomaly, 2)

                # Mutate the corresponding YearlyMetrics object to fill in the missing data.
                metrics_so_far[index].month = month
                metrics_so_far[index].temp_anomaly = temp_anomaly
                metrics_so_far[index].temp = temp
                index += 1

    return metrics_so_far


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    import python_ta.contracts

    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    python_ta.check_all(config={
        'extra-imports': ['dataclass', 'csv', 'Optional', 'os'],
        'allowed-io': ['load_yearly_data', 'load_monthly_data'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })
