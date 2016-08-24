from __future__ import print_function

import time

from datetime import datetime
from dateutil import parser, relativedelta
from fuzzywuzzy import process
from terminaltables import AsciiTable
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from terminals import terminals

BASE_URL = "https://www.bcferries.com/bcferries/faces/reservation/booking.jsp?pcode=GUEST"


class TerminalNotFound(BaseException):
    pass


class Sailing(object):

    def __init__(self, departure_time, arrival_time, departure_terminal,
                 arrival_terminal, vessel_name, reservations_available):
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.departure_terminal = departure_terminal
        self.arrival_terminal = arrival_terminal
        self.vessel_name = vessel_name
        self.reservations_available = reservations_available


class Reservation(object):

    SUPPORTED_DRIVERS = {
        'chrome': 'Chrome',
        'phantomjs': 'PhantomJS',
        'firefox': 'Firefox',
    }

    def __init__(self,
                 departure_terminal='horseshoe bay',
                 arrival_terminal='departure bay',
                 departure_date=None,
                 return_date=None,
                 num_12_plus=1,
                 num_under_5=0,
                 num_5_to_11=0,
                 num_seniors=0,
                 height_under_7ft=True,
                 length_up_to_20ft=True,
                 driver_type='chrome'):

        result = process.extractOne(departure_terminal, choices=terminals.keys(), score_cutoff=75)
        if result:
            self.departure_terminal = result[0]
        else:
            raise TerminalNotFound('Could not find terminal {}'.format(departure_terminal))

        arrival_choices = terminals[self.departure_terminal]
        result = process.extractOne(arrival_terminal, choices=arrival_choices, score_cutoff=75)
        if result:
            self.arrival_terminal = result[0]
        else:
            raise TerminalNotFound('Could not find terminal {}'.format(arrival_terminal))

        if departure_date:
            self.departure_date = parser.parse(departure_date)
        else:
            self.departure_date = (datetime.now() + relativedelta.relativedelta(days=7))

        if return_date:
            self.return_date = parser.parse(return_date)
        else:
            self.return_date = None

        print('Searching for reservations Departing {} and Returning {}'.format(
                                self._format_date(self.departure_date),
                                self._format_date(self.return_date)))
        print('From: {} To: {}'.format(self.departure_terminal, self.arrival_terminal))

        self.num_12_plus = num_12_plus
        self.num_under_5 = num_under_5
        self.num_5_to_11 = num_5_to_11
        self.num_seniors = num_seniors
        self.height_under_7ft = height_under_7ft
        self.length_up_to_20ft = length_up_to_20ft
        self.driver_type = driver_type

    def start(self):
        self.driver = getattr(webdriver, self.SUPPORTED_DRIVERS.get(self.driver_type))()
        self.driver.get(BASE_URL)
        # switch to the iframe
        self.driver.switch_to_frame('iframe_workflow')

    def __enter__(self):
        self.driver = getattr(webdriver, self.SUPPORTED_DRIVERS.get(self.driver_type))()
        self.driver.get(BASE_URL)
        # switch to the iframe
        self.driver.switch_to_frame('iframe_workflow')
        return self

    def __exit__(self, *args):
        self.driver.close()

    def _format_date(self, datetime_obj):
        if datetime_obj:
            return datetime_obj.strftime('%B %d, %Y')
        else:
            return ''

    def _click_continue(self):
        continue_button = self.driver.find_element_by_link_text('Continue')
        continue_button.click()

    def _get_departure_terminal(self):
        terminals = self.driver.find_elements_by_class_name("dd_div_deparr_terminal")
        for terminal in terminals:
            terminal_name = terminal.text.lower().replace('\n', ' ')
            if self.departure_terminal == terminal_name:
                return terminal
        raise TerminalNotFound('No departure terminal named {}'.format(self.departure_terminal))

    def _get_arrival_terminal(self):
        terminals = self.driver.find_elements_by_class_name("dd_div_deparr_terminal")
        for terminal in terminals[14:]:
            terminal_name = terminal.text.lower().replace('\n', ' ')
            if self.arrival_terminal == terminal_name:
                return terminal
        raise TerminalNotFound('No arrival terminal named {}'.format(self.arrival_terminal))

    def _select_dates(self):
        # always need a departure date
        self.driver.execute_script("document.getElementById('centerRegion:dateDestination:departureDate').setAttribute('type', 'text');")
        departure_date_elem = self.driver.find_element_by_id('centerRegion:dateDestination:departureDate')
        departure_date_elem.clear()
        departure_date_elem.send_keys(self._format_date(self.departure_date))
        time.sleep(1)

        if self.return_date:
            # round-trip this radio box is pre-selected so we only need to fill out the
            # return date
            self.driver.execute_script("document.getElementById('centerRegion:dateDestination:returnDate').setAttribute('type', 'text');")
            departure_date_elem = self.driver.find_element_by_id('centerRegion:dateDestination:returnDate')
            departure_date_elem.clear()
            departure_date_elem.send_keys(self._format_date(self.return_date))
            time.sleep(1)
        else:
            # one-way so we need to select the one-way radio box
            self.driver.find_element_by_id('centerRegion:dateDestination:roundTrip:_1').click()

        time.sleep(1)

    def _select_terminals(self):
        departure_term = self._get_departure_terminal()
        departure_term.click()
        time.sleep(1)
        arrival_terminal = self._get_arrival_terminal()
        arrival_terminal.click()
        self._click_continue()

    def _enter_passenger_info(self):
        twelve_plus_select = self.driver.find_element_by_id('centerRegion:passengers:passIterBaseOutbound:0:selectOnePassengerCountTop')
        twelve_plus_select.send_keys(str(self.num_12_plus))
        if self.num_12_plus == 1:
            twelve_plus_select.send_keys(str(self.num_12_plus))

        five_to_eleven_select = self.driver.find_element_by_id('centerRegion:passengers:passIterBaseOutbound:1:selectOnePassengerCountTop')
        five_to_eleven_select.send_keys(str(self.num_5_to_11))
        if self.num_5_to_11 == 1:
            five_to_eleven_select.send_keys(str(self.num_5_to_11))

        under_5_select = self.driver.find_element_by_id('centerRegion:passengers:passIterBaseOutbound:2:selectOnePassengerCountTop')
        under_5_select.send_keys(str(self.num_under_5))
        if self.num_under_5 == 1:
            under_5_select.send_keys(str(self.num_under_5))

        senior_select = self.driver.find_element_by_id('centerRegion:passengers:passIterBaseOutbound:3:selectOnePassengerCountTop')
        senior_select.send_keys(str(self.num_seniors))
        if self.num_seniors == 1:
            senior_select.send_keys(str(self.num_seniors))

        self._click_continue()

    def _enter_vehicle_info(self):
        if self.height_under_7ft:
            elem = self.driver.find_element_by_id('centerRegion:vehicle:so_fareType_value:_0')
        else:
            elem = self.driver.find_element_by_id('centerRegion:vehicle:so_fareType_value:_1')
        elem.click()
        if self.length_up_to_20ft:
            elem = self.driver.find_element_by_id('centerRegion:vehicle:so_lengthOver20_option:_0')
        else:
            elem = self.driver.find_element_by_id('centerRegion:vehicle:so_lengthOver20_option:_1')
        elem.click()
        self._click_continue()

    def get_available_sailings(self):
        self._select_dates()
        time.sleep(1)
        self._select_terminals()
        time.sleep(1)
        self._enter_passenger_info()
        time.sleep(1)
        self._enter_vehicle_info()
        time.sleep(1)

        sailings = self.driver.find_elements_by_class_name('sai_div_sailings_row_outer')
        available_sailings = []
        for sailing in sailings:
            if 'select' in sailing.find_element_by_class_name('sai_col_select').text.lower():
                available_sailings.append(
                    Sailing(
                      departure_time=sailing.find_element_by_class_name('sai_col_depart').text,
                      arrival_time=sailing.find_element_by_class_name('sai_col_arrive').text,
                      vessel_name=sailing.find_element_by_class_name('sai_col_vessel').text,
                      departure_terminal=self.departure_terminal,
                      arrival_terminal=self.arrival_terminal,
                      reservations_available=True,
                      ))
        return available_sailings

    def print_sailings(self, sailings):
        table_data = [['Departure', 'Arrival', 'Vessel']]
        for sailing in sailings:
            table_data.append([sailing.departure_time, sailing.arrival_time, sailing.vessel_name])
        table = AsciiTable(table_data)
        print('Available Salings on {}'.format(self._format_date(self.departure_date)))
        print("From {} To {}".format(self.departure_terminal, self.arrival_terminal))
        print(table.table)

    def __del__(self):
        self.driver.close()

    def close(self):
        self.driver.close()

if __name__ == '__main__':
    with Reservation() as res:
        res.print_sailings(res.get_available_sailings())
