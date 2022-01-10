"""CSC110 Fall 2021: Project Phase 2 - Visualizing the Data

Module Description
==================

This module contains functions for creating an interactive GUI for user to play around with and
visualize the data.

Copyright and Usage Information
===============================

All forms of distribution of this code, whether as given or
with any changes, are expressly prohibited.

This file is Copyright (c) 2021 Richard Shi.
"""
import tkinter as tk
from typing import Union
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from load_data import YearlyMetrics, MonthlyMetrics

import load_data as load
import calculations as calc

# Constants for the csv file locations
ANNUAL_CO2_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\co2_annmean_mlo.csv'
ANNUAL_TEMP_ANOMALY_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\annual_temp_' \
                                                                         'anomalies.csv'
MONTHLY_CO2_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\co2_mm_mlo.csv'
MONTHLY_TEMP_ANOMALY_FILE = os.path.dirname(os.path.realpath(__file__)) + '\\monthly_temp_' \
                                                                          'anomalies.csv'


def run_visualization() -> None:
    """Show a window that the user can interact with to visualize the climate data.

    When this function is called, it creates a window where you can adjust the climate sensitivity
    factor to produce a graph of the climate data. You can also hit a button to extrapolate the data
    to model future climate data. Finally, you can check the accuracy of the climate model after you
    have produced at least one graph (the accuracy is based on the most recent graph produced).
    """
    window = tk.Tk()
    window.geometry('500x500')
    window.title('Visualizing the Climate Model')
    # To help organize the widgets
    frame = tk.Frame(window)
    frame.pack()

    # Check whether to display yearly or monthly data
    type_label = tk.Label(frame, text='Adjust the slider to the left to display monthly data and to'
                                      ' the right to display yearly data!')
    type_slider = tk.Scale(frame, from_=0, to=1, orient='horizontal', showvalue=False)
    # Climate sensitivity widgets
    sensitivity_label = tk.Label(frame,
                                 text='Adjust the slider to set the climate sensitivity factor!')
    sensitivity_slider = tk.Scale(frame, from_=2.0, to=5.0, resolution=0.1,
                                  digits=2, orient='horizontal')
    # Extrapolating data widgets
    extrapolate_input_q = tk.Label(frame, text='How many years of data do you want to extrapolate?')
    extrapolate_input = tk.Scale(frame, from_=1, to=100, orient='horizontal')
    extrapolate_emissions_q = tk.Label(frame, text='How many gigatons of carbon should be '
                                                   'emitted annually?')
    extrapolate_emissions = tk.Scale(frame, from_=0.0, to=50.0, resolution=0.1, digits=3,
                                     orient='horizontal')
    extrapolate_label = tk.Label(frame, text='Toggle on/off to extrapolate climate data!')
    extrapolate_button = tk.Button(frame, text='Off', bg='gainsboro', fg='red',
                                   command=lambda:
                                   extrapolate_button_callback(extrapolate_input_q,
                                                               extrapolate_input,
                                                               extrapolate_emissions_q,
                                                               extrapolate_emissions,
                                                               extrapolate_button
                                                               )
                                   )
    # Generate the graph widget
    visualize_button = tk.Button(frame, text='Click to visualize the data!',
                                 command=lambda:
                                 visualize_button_callback(get_specifications(type_slider,
                                                                              sensitivity_slider,
                                                                              extrapolate_button,
                                                                              extrapolate_input,
                                                                              extrapolate_emissions
                                                                              )
                                                           )
                                 )
    # Reporting error widgets
    report_error_button = tk.Button(frame, text='Click to see the accuracy of the model!',
                                    command=lambda:
                                    report_error_button_callback(
                                        get_specifications(type_slider,
                                                           sensitivity_slider,
                                                           extrapolate_button,
                                                           extrapolate_input,
                                                           extrapolate_emissions
                                                           )
                                    )
                                    )

    # Packing and organizing the widgets
    type_label.pack(side=tk.TOP)
    type_slider.pack(side=tk.TOP)
    sensitivity_label.pack(side=tk.TOP, pady=(20, 0))
    sensitivity_slider.pack(side=tk.TOP)
    extrapolate_label.pack(side=tk.TOP, pady=(20, 0))  # The tuple indicates (top, bottom) padding
    extrapolate_button.pack(side=tk.TOP)
    visualize_button.pack(side=tk.BOTTOM, pady=(20, 0))
    report_error_button.pack(side=tk.BOTTOM, pady=(20, 0))
    extrapolate_input_q.pack_forget()  # Make these widgets invisible until needed
    extrapolate_input.pack_forget()
    extrapolate_emissions_q.pack_forget()
    extrapolate_emissions.pack_forget()

    window.mainloop()


def extrapolate_button_callback(label1: tk.Label, inp: tk.Scale, label2: tk.Label, scale: tk.Scale,
                                button: tk.Button) -> None:
    """Update the extrapolate data button to reflect whether its been toggled on or off.

    This will also reveal or hide the widgets associated with extrapolating the data.
    """
    if button['text'] == 'Off':
        button.config(text='On', fg='green')
        label1.pack(side=tk.TOP, pady=(20, 0))  # Make the widgets visible now
        inp.pack(side=tk.TOP)
        label2.pack(side=tk.TOP)
        scale.pack(side=tk.TOP)
    else:
        button.config(text='Off', fg='red')
        label1.pack_forget()  # Hiding the widgets again
        inp.pack_forget()
        label2.pack_forget()
        scale.pack_forget()

    button.update()


def visualize_button_callback(specifications: tuple[str, list]) -> None:
    """Visualize the climate data given the user's specifications.

    The <specifications> list will either contain specifications for modelling recorded climate data
    or for extrapolating climate data, depending on whether or not the str in the tuple is 'Off' or
    'On,' respectively.

    Preconditions:
        - len(specifications) != 0
        - specifications[1] != []
    """
    is_extrapolate = True if specifications[0] == 'On' else False

    if is_extrapolate:
        num_entries, sensitivity, emissions = specifications[1]
        climate_data = calc.extrapolate_data(num_entries, sensitivity, emissions)
    else:
        is_yearly_data = specifications[1][0]
        if is_yearly_data:
            # Since there is so much data, we will just prompt the user for the start date of a
            # "section" of data they wish to look at. The "section" of data will be 12 data entries.
            # Subtract 1960 so we can get a valid index (0-50, inclusive for years between 1959 and
            # 2010) to form a "section" of 12 data entries. This is because the implementation of
            # load_data.calculate_error skips the first index.
            section_start = int(input('What year of data would you like to start at (1960-2010, '
                                      'inclusive)? ')) - 1960
            climate_data = load.load_yearly_data(ANNUAL_CO2_FILE, ANNUAL_TEMP_ANOMALY_FILE)
        else:
            climate_data = load.load_monthly_data(MONTHLY_CO2_FILE, MONTHLY_TEMP_ANOMALY_FILE)
            start_date = input('What year and month of data would you like to start at '
                               '(1959-1 to 2020-1, inclusive)? ')
            # Formula to calculate a valid index (0-732, inclusive) to form a "section" of 12 data
            # entries
            section_start = (int(start_date[0: 4]) - 1959) * 12 + (int(start_date[5:]) - 1)

        section_end = section_start + 12

        sensitivity = specifications[1][1]
        calc.update_data(climate_data, sensitivity)

        if not is_yearly_data:
            plot_compared_data(climate_data[section_start: section_end])
        else:
            plot_compared_data(climate_data[section_start: section_end])

    # Calling another function to plot the data
    plot_climate_data(climate_data)


def report_error_button_callback(specifications: tuple[str, list]) -> None:
    """Analyze the accuracy of the model by visualizing the percent error given the current
    specifications.

    Preconditions:
        - len(specifications) != 0
        - specifications[1] != []
    """
    is_extrapolate = True if specifications[0] == 'On' else False
    is_yearly_data = specifications[1][0]
    if is_extrapolate:
        # Print to the console if the user is in "extrapolate data" mode
        print('Cannot report accuracy of the model for extrapolated data!')
        return

    if is_yearly_data:
        # Since there is so much data, we will just prompt the user for the start date of a
        # "section" of data they wish to look at. The "section" of data will be 12 data entries.
        # Subtract 1960 so we can get a valid index (0-50, inclusive for years between 1959 and
        # 2009) to form a "section" of 12 data entries. This is because the implementation of
        # load_data.calculate_error skips the first index.
        section_start = int(input('What year of data would you like to start at (1960-2009, '
                                  'inclusive)? ')) - 1960
        climate_data = load.load_yearly_data(ANNUAL_CO2_FILE, ANNUAL_TEMP_ANOMALY_FILE)
    else:
        climate_data = load.load_monthly_data(MONTHLY_CO2_FILE, MONTHLY_TEMP_ANOMALY_FILE)
        start_date = input('What year and month of data would you like to start at '
                           '(1959-2 to 2020-1, inclusive)? ')
        # Formula to calculate a valid index (0-731, inclusive) to form a "section" of 12 data
        # entries
        section_start = (int(start_date[0: 4]) - 1959) * 12 + (int(start_date[5:]) - 1) - 1

    # Must add 13 instead of 12 because the implementation of load_data.calculate_error skips the
    # first index
    section_end = section_start + 13

    sensitivity = specifications[1][1]
    calc.update_data(climate_data, sensitivity)

    reported_errors = calc.calculate_error(climate_data[section_start: section_end])

    # Calling another function to plot the data
    plot_reported_errors(reported_errors)

    # Print to the console the average percent error
    print(f'The percent error in this run was: '
          f'{calc.calculate_average_percent_error(climate_data)}')


def get_specifications(scale1: tk.Scale, scale2: tk.Scale, button: tk.Button, scale3: tk.Scale,
                       scale4: tk.Scale) -> tuple[str, list]:
    """Returns a list of specifications detailing what type and how the climate data should be
    visualized.

    <scale1>, <scale2>, <button>, <scale3>, and <scale4> correspond to <type_slider>,
    <sensitivity_slider>, <extrapolate_button>, <extrapolate_input>, and <extrapolate_emissions>
    from the run_visualization function.
    """
    specifications_so_far = []
    yearly_data = True if int(scale1.get()) == 1 else False
    sensitivity = float(scale2.get())
    is_extrapolate = button['text']

    if is_extrapolate == 'Off':
        specifications_so_far.append(yearly_data)
        specifications_so_far.append(sensitivity)
    else:
        num_entries = int(scale3.get())
        emissions = float(scale4.get())

        specifications_so_far.append(num_entries)
        specifications_so_far.append(sensitivity)
        specifications_so_far.append(emissions)

    return is_extrapolate, specifications_so_far


def plot_climate_data(metrics: list[Union[YearlyMetrics, MonthlyMetrics]]) -> None:
    """Plot the climate data in <metrics> as a time series.

    This function will plot both the recorded or calculated CO2 concentration and temperature
    values.

    Preconditions:
        - metrics != []
    """
    date_format = 'Year' if isinstance(metrics[0], YearlyMetrics) else 'Year, Month'
    x_data, y_data1, y_data2 = get_xy_data1(metrics)

    # The first graph
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=x_data, y=y_data1, name='CO2 Concentration Data'),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=x_data, y=y_data2, name='Temperature Data'), secondary_y=True)

    fig.update_layout(title='Time series of CO2 Concentration and Temperature',
                      xaxis_title=date_format)
    fig.update_yaxes(title='CO2 Concentration (in ppm)', secondary_y=False)
    fig.update_yaxes(title='Temperature (in degrees Celsius)', secondary_y=True)

    fig.show()


def plot_compared_data(metrics: list[Union[YearlyMetrics, MonthlyMetrics]]) -> None:
    """Plot the climate data in <metrics> as a time series.

    This function will plot the calculated and recorded temperature anomaly values.

    Preconditions:
        - metrics != []
        - metrics is not a list of extrapolated data
    """
    date_format = 'Year' if isinstance(metrics[0], YearlyMetrics) else 'Year, Month'
    x_data, y_data1, y_data2 = get_xy_data2(metrics)

    fig = go.Figure(data=[
        go.Bar(name='Calculated Temperature Anomaly Values', x=x_data, y=y_data1),
        go.Bar(name='Recorded Temperature Anomaly Values', x=x_data, y=y_data2)
    ])
    fig.update_layout(title='Time series of Calculated vs Recorded Temperature Anomaly Values',
                      xaxis_title=date_format,
                      yaxis_title='Temperature Anomaly (in degrees C)')

    fig.show()


def get_xy_data1(metrics: list[Union[YearlyMetrics, MonthlyMetrics]]) \
        -> tuple[list[str], list[float], list[float]]:
    """Returns a tuple of three parallel lists. The first list is the year (or year and month)
    corresponding to the climate data. The last two lists contains floats that correspond to the
    recorded CO2 concentration and the temperature.
    """
    dates_so_far = []
    concentrations_so_far = []
    temperatures_so_far = []

    for entry in metrics:
        if isinstance(entry, YearlyMetrics):
            current_date = str(entry.year)
        else:
            current_date = f'{entry.year}, {entry.month}'
        current_concentration = entry.co2
        current_temperature = entry.temp

        dates_so_far.append(current_date)
        concentrations_so_far.append(current_concentration)
        temperatures_so_far.append(current_temperature)

    return dates_so_far, concentrations_so_far, temperatures_so_far


def get_xy_data2(metrics: list[Union[YearlyMetrics, MonthlyMetrics]]) \
        -> tuple[list[str], list[float], list[float]]:
    """Returns a tuple of three parallel lists. The first list is the year (or year and month)
    corresponding to the climate data. The last two lists contains floats that correspond to the
    calculated and recorded temperatures.

    Preconditions:
        - the data in metrics is not extrapolated data
    """
    dates_so_far = []
    temp_anomalies_so_far = []
    recorded_temp_anomalies_so_far = []

    for entry in metrics:
        if isinstance(entry, YearlyMetrics):
            current_date = str(entry.year)
        else:
            current_date = f'{entry.year}, {entry.month}'
        calculated_temp_anomaly = entry.calculated_temp_anomaly
        recorded_temp_anomaly = entry.temp_anomaly

        dates_so_far.append(current_date)
        temp_anomalies_so_far.append(calculated_temp_anomaly)
        recorded_temp_anomalies_so_far.append(recorded_temp_anomaly)

    return dates_so_far, temp_anomalies_so_far, recorded_temp_anomalies_so_far


def plot_reported_errors(errors: dict[str, float]) -> None:
    """Plot the percent errors in <errors> as a time series.
    """
    x_data = list(errors.keys())
    y_data = list(errors.values())

    fig = go.Figure([go.Bar(name='Percent Error', x=x_data, y=y_data)])
    fig.update_layout(title='Time series of percentage error in temperature anomalies',
                      xaxis_title='Date',
                      yaxis_title='Percentage Error (in %)')

    fig.show()


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    import python_ta.contracts

    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    python_ta.check_all(config={
        'extra-imports': ['plotly.graph_objects', 'tkinter', 'load_data', 'calculations',
                          'plotly.subplots', 'os'],
        'allowed-io': ['visualize_button_callback', 'report_error_button_callback'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })
