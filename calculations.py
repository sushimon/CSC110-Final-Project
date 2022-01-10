"""CSC110 Fall 2021: Project Phase 2 - Performing Calculations

Module Description
==================

This module contains functions for performing computations on the data and reporting statistics.

Copyright and Usage Information
===============================

All forms of distribution of this code, whether as given or
with any changes, are expressly prohibited.

This file is Copyright (c) 2021 Richard Shi.
"""
import math
from typing import Union
from load_data import YearlyMetrics, MonthlyMetrics

# Initial values that can be used for year, co2, and temp when extrapolating data
INITIAL_YEAR = 2020
INITIAL_CO2 = 414.24
INITIAL_TEMP = 15.49


####################################################################################################
# Functions for performing computations on the data
####################################################################################################
def calculate_concentration(past_concentration: float, emissions: float) -> float:
    """Return the estimated CO2 concentration.

    The CO2 concentration (in ppm) is calculated by taking 45% of the amount of CO2 emissions
    (in gigatons, GtC) and dividing it by 2.3 which produces the increase in CO2 concentration. The
    estimated CO2 concentration for the next year is calculated by adding the increase with the
    previous year's concentration.

    Preconditions:
        - past_concentration >= 0.0
        - emissions >= 0.0

    >>> new_concentration = calculate_concentration(414.24, 10.0)
    >>> round(new_concentration, 2) == 416.20
    True
    """
    increase_in_concentration = (emissions * 0.45) / 2.3
    estimated_concentration = past_concentration + increase_in_concentration

    return estimated_concentration


def calculate_temperature(current_temp: float, sensitivity: float, new_concentration: float,
                          current_concentration: float) -> tuple[float, float]:
    """Return a tuple containing the calculated temperature and calculated temperature anomaly.

    The temperature is calculated by the following formula:
    T = T0 + S * log_2 (C / C0), where T0 and C0 are the known temperature and CO2 concentration at
    some reference time, S is the climate sensitivity factor, and C is the new CO2 concentration.

    The temperature anomaly is calculated simply by subtracting the calculated temperature and the
    20th century average global temperature of 13.9 degrees Celsius.

    Preconditions:
        - 2.0 <= sensitivity <= 5.0

    >>> temp, temp_anomaly = calculate_temperature(13.98, 3.0, 316.91, 315.98)
    >>> round(temp, 2) == 13.99
    True
    >>> round(temp_anomaly, 2) == 0.09
    True
    """
    calculated_temp = current_temp + \
        sensitivity * math.log(new_concentration / current_concentration, 2)
    calculated_temp_anomaly = calculated_temp - 13.9

    return calculated_temp, calculated_temp_anomaly


def update_data(metrics: list[Union[YearlyMetrics, MonthlyMetrics]],
                sensitivity: float) -> None:
    """Mutate the input list <metrics> of YearlyMetrics or MonthlyMetrics objects. <metrics> should
    be the returned list from either the load_data.load_yearly_data or load_data.load_monthly_data
    function.

    This mutation will update the calculated_temp and calculated_temp_anomaly attributes of each
    object (except the first).

    Preconditions:
        - metrics is the returned list of load_data.load_yearly_data or load_data.load_monthly_data
        - 2.0 <= sensitivity <= 5.0
    """
    # Initial values taken from the first YearlyMetrics/MonthlyMetrics object
    past_co2 = metrics[0].co2
    past_temp = metrics[0].temp

    # Since the first row acts as initial values, we'll only need to update the objects beyond the
    # first index
    for i in range(1, len(metrics)):
        current_entry = metrics[i]
        current_co2 = current_entry.co2

        current_temp, current_temp_anomaly = calculate_temperature(current_temp=past_temp,
                                                                   sensitivity=sensitivity,
                                                                   new_concentration=current_co2,
                                                                   current_concentration=past_co2
                                                                   )
        current_entry.calculated_temp = current_temp
        current_entry.calculated_temp_anomaly = current_temp_anomaly

        past_co2 = current_co2
        past_temp = current_entry.temp


def extrapolate_data(num_entries: int, sensitivity: float, emissions: float) -> list[YearlyMetrics]:
    """Return a list of <num_entries> YearlyMetric objects that represent the extrapolated data.

    The variables <sensitivity> and <emissions> will be used in the calculate_temperature and
    calculate_concentration functions, respectively, to calculate the temperature and temperature
    anomalies for a given year.

    For the sake of convenience in our visualization part, we will be storing the calculated values
    in the temp and temp_anomaly instance attributes of YearlyMetrics and MonthlyMetrics instead.

    Preconditions:
        - num_entries > 0
        - 2.0 <= sensitivity <= 5.0
        - emissions >= 0.0

    >>> entries = 10
    >>> new_data = extrapolate_data(entries, 3.0, 10.0)
    >>> len(new_data) == entries  # Illustrating properties of the extrapolated data
    True
    >>> all(2021 <= entry.year <= 2020 + entries for entry in new_data)
    True
    >>> all(entry.temp is not None for entry in new_data)
    True
    >>> all(entry.temp_anomaly is not None for entry in new_data)
    True
    """
    metrics_so_far = []

    # Initial values
    past_co2 = INITIAL_CO2
    past_temp = INITIAL_TEMP

    for i in range(1, num_entries + 1):
        current_year = 2020 + i
        current_co2 = calculate_concentration(past_concentration=past_co2, emissions=emissions)
        current_temp, current_temp_anomaly = calculate_temperature(current_temp=past_temp,
                                                                   sensitivity=sensitivity,
                                                                   new_concentration=current_co2,
                                                                   current_concentration=past_co2
                                                                   )

        metrics_so_far.append(YearlyMetrics(year=current_year,
                                            co2=current_co2,
                                            temp=current_temp,
                                            temp_anomaly=current_temp_anomaly
                                            )
                              )

        past_co2 = current_co2
        past_temp = current_temp

    return metrics_so_far


####################################################################################################
# Functions for reporting statistics
####################################################################################################
def calculate_error(metrics: list[Union[YearlyMetrics, MonthlyMetrics]]) -> dict[str, float]:
    """Return a list of tuples containing the year (and month, if <metrics> is a list of
    MonthlyMetrics objects) and the percentage error of the recorded and accepted values for the
    temperature anomalies.

    Preconditions:
        - metrics is the mutated list after being passed to update_data
    """
    percent_errors_so_far = {}

    for entry in metrics[1:]:
        if isinstance(entry, YearlyMetrics):
            current_year = str(entry.year)
        else:
            current_year = f'{entry.year}, {entry.month}'

        calculated_value = entry.calculated_temp_anomaly
        known_value = entry.temp_anomaly

        # Since the known value could be 0, we will calculate percent error by taking the natural
        # log of e to the power of the calculated minus the known value and then multiplying it by
        # 100
        percent_error = abs(math.log(math.exp(calculated_value - known_value))) * 100

        percent_errors_so_far[current_year] = percent_error

    return percent_errors_so_far


def calculate_average_percent_error(metrics: list[Union[YearlyMetrics, MonthlyMetrics]]) -> str:
    """Return the average percent error of the recorded and accepted values for the temperature
    anomalies.

    Preconditions:
        - metrics is the mutated list after being passed to update_data
    """
    error_data = calculate_error(metrics)
    error_values = list(error_data.values())
    output = f'{round(sum(error_values) / len(error_values), 2)}%'

    return output


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    import python_ta.contracts

    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    python_ta.check_all(config={
        'extra-imports': ['math', 'load_data', 'Union'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })
