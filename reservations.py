import time
import pickle
import os
from datetime import datetime
from dateutil import parser, relativedelta
from fuzzywuzzy import process
from terminaltables import AsciiTable
from selenium import webdriver

from app import db
from models import Result, AvailableSailing
from terminals import terminal_map
from rq import Queue
from worker import conn

# RQ queue
pickle.HIGHEST_PROTOCOL = 2
q = Queue(connection=conn)

BASE_URL = "https://www.bcferries.com/bcferries/faces/reservation/booking.jsp?pcode=GUEST"


def _format_date(datetime_obj):
    """Format datetime object to `August 1, 2016` format
    """
    if datetime_obj:
        return datetime_obj.strftime('%B %d, %Y')
    else:
        return ''


def _parse_list(val):
    if isinstance(val, list):
        return val
    elif isinstance(val, str):
        return [val]
    else:
        raise TypeError('Unsupported type {}, must be `str` or `list`'.format(type(val)))


class TerminalNotFound(BaseException):
    pass


class InitialSailing(object):

    def __init__(self, departure_time, arrival_time, departure_terminal,
                 arrival_terminal, vessel_name, reservations_available):
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.departure_terminal = departure_terminal
        self.arrival_terminal = arrival_terminal
        self.vessel_name = vessel_name
        self.reservations_available = reservations_available


class Route(object):

    def __init__(self, departure_terminal, arrival_terminal):
        self.departure_terminal = departure_terminal
        self.arrival_terminal = arrival_terminal

    def __repr__(self):
        return 'Route({} - {})'.format(self.departure_terminal.title(),
                                       self.arrival_terminal.title())

    def __eq__(self, other):
        return ((self.departure_terminal == other.departure_terminal) and
                (self.arrival_terminal == other.arrival_terminal))

    def __hash__(self):
        return hash(self.departure_terminal + self.arrival_terminal)


class ReservationFinder(object):
    """Find avaliable reservations on BC Ferries website.

    Reservations are found for a given departure and return date,
    and between a specific departure and arrival terminal.
    """
    SUPPORTED_DRIVERS = {
        'chrome': 'Chrome',
        'phantomjs': 'PhantomJS',
        'firefox': 'Firefox',
    }

    GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google_chrome'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

    GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', None)
    CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', None)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = GOOGLE_CHROME_BIN if GOOGLE_CHROME_BIN else {}
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    executable_path = CHROMEDRIVER_PATH if CHROMEDRIVER_PATH else None

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
                 driver_type='chrome',
                 chrome_options=chrome_options,
                 executable_path=executable_path):
        #
        if executable_path:
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
        else:
            self.driver = webdriver.Chrome()
        # self.driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=chrome_options)
        # fuzzy match the departure terminal
        result = process.extractOne(departure_terminal,
                                    choices=terminal_map.keys(),
                                    score_cutoff=75)
        if result:
            self.departure_terminal = result[0]
        else:
            raise TerminalNotFound('Could not find terminal {}'.format(departure_terminal))

        # fuzzy match the arrival terminal
        arrival_choices = terminal_map[self.departure_terminal]
        result = process.extractOne(arrival_terminal, choices=arrival_choices, score_cutoff=75)
        if result:
            self.arrival_terminal = result[0]
        else:
            raise TerminalNotFound('Could not find terminal {}'.format(arrival_terminal))

        # parse departure date
        if departure_date:
            self.departure_date = parser.parse(departure_date)
        else:
            self.departure_date = (datetime.now() + relativedelta.relativedelta(days=7))

        # parse return date
        if return_date:
            self.return_date = parser.parse(return_date)
        else:
            self.return_date = None

        print('Searching for reservations Departing {} and Returning {}'.format(
                                    _format_date(self.departure_date),
                                    _format_date(self.return_date)))
        print('From: {} To: {}'.format(self.departure_terminal, self.arrival_terminal))

        self.num_12_plus = num_12_plus
        self.num_under_5 = num_under_5
        self.num_5_to_11 = num_5_to_11
        self.num_seniors = num_seniors
        self.height_under_7ft = height_under_7ft
        self.length_up_to_20ft = length_up_to_20ft
        self.driver_type = driver_type

    def start(self):
        """Start webdriver
        """
        print("In start fn")
        # self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
        # driver = self.driver
        self.driver.get(BASE_URL)
        print("In start fn 142")
        # switch to the iframe since it's where all the action happens
        self.driver.switch_to.frame('iframe_workflow')
        print("In start fn 143")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.driver.close()

    def _click_continue(self):
        """Click continue button on the current page
        """
        continue_button = self.driver.find_element_by_link_text('Continue')
        continue_button.click()

    def _get_departure_terminal(self):
        """Find departure terminal element
        """
        terminals = self.driver.find_elements_by_class_name("dd_div_deparr_terminal")
        for terminal in terminals:
            terminal_name = terminal.text.lower().replace('\n', ' ')
            if self.departure_terminal == terminal_name:
                return terminal
        raise TerminalNotFound('No departure terminal named {}'.format(self.departure_terminal))

    def _get_arrival_terminal(self):
        """Find arrival terminal element
        """
        terminals = self.driver.find_elements_by_class_name("dd_div_deparr_terminal")
        for terminal in terminals[14:]:
            terminal_name = terminal.text.lower().replace('\n', ' ')
            if self.arrival_terminal == terminal_name:
                return terminal
        raise TerminalNotFound('No arrival terminal named {}'.format(self.arrival_terminal))

    def _select_dates(self):
        # always need a departure date
        print("In Select dates")
        #select round trip
        self.driver.find_element_by_id('centerRegion:dateDestination:roundTrip:_0').click()
        self.driver.execute_script("document.getElementById('centerRegion:dateDestination:departureDate').setAttribute('type', 'text');")
        departure_date_elem = self.driver.find_element_by_id('centerRegion:dateDestination:departureDate')
        departure_date_elem.clear()
        departure_date_elem.send_keys(_format_date(self.departure_date))
        time.sleep(1)

        if self.return_date:
            # round-trip this radio box is pre-selected so we only need to fill out the
            # return date
            self.driver.execute_script("document.getElementById('centerRegion:dateDestination:returnDate').setAttribute('type', 'text');")
            departure_date_elem = self.driver.find_element_by_id('centerRegion:dateDestination:returnDate')
            departure_date_elem.clear()
            departure_date_elem.send_keys(_format_date(self.return_date))
            time.sleep(1)
        else:
            # one-way so we need to select the one-way radio box
            self.driver.find_element_by_id('centerRegion:dateDestination:roundTrip:_1').click()
        time.sleep(1)

    def _select_terminals(self):
        print("In Select terminals")
        departure_term = self._get_departure_terminal()
        departure_term.click()
        time.sleep(1)
        arrival_terminal = self._get_arrival_terminal()
        arrival_terminal.click()
        self._click_continue()

    def _enter_passenger_info(self):
        print("In passenger info")
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
        print("In vehicle info")
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
        print("In get avail sailings")
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
                    InitialSailing(
                      departure_time=sailing.find_element_by_class_name('sai_col_depart').text,
                      arrival_time=sailing.find_element_by_class_name('sai_col_arrive').text,
                      vessel_name=sailing.find_element_by_class_name('sai_col_vessel').text,
                      departure_terminal=self.departure_terminal,
                      arrival_terminal=self.arrival_terminal,
                      reservations_available=True,
                      ))

        print("End Avail sailings")
        return available_sailings

    def print_sailings(self, sailings):
        table_data = [['Departure', 'Arrival', 'Vessel']]
        for sailing in sailings:
            table_data.append([sailing.departure_time, sailing.arrival_time, sailing.vessel_name])
        table = AsciiTable(table_data)
        print('Available Salings on {}'.format(_format_date(self.departure_date)))
        print("From {} To {}".format(self.departure_terminal, self.arrival_terminal))
        print(table.table)
        return table.table

    def save_sailings_results(self, init_sailings):
        print("In save sailings")
        errors = []
        if init_sailings:
            print("If sailings")
            for sailing in init_sailings:
                print("for sailing: {} in sailings: {}".format(sailing, init_sailings))
                try:
                    sailing_to_save = AvailableSailing(
                      departure_time=sailing.departure_time,
                      arrival_time=sailing.arrival_time,
                      vessel_name=sailing.vessel_name,
                      departure_terminal=sailing.departure_terminal,
                      arrival_terminal=sailing.arrival_terminal,
                      reservations_available=sailing.reservations_available,
                      )
                    db.session.add(sailing_to_save)
                    db.session.commit()
                    print("db id: {}".format(sailing_to_save.id))
                    return sailing_to_save.id
                except Exception as e:
                    print("errrrors: {}".format(str(e)))
                    errors.append("Unable to add item to database.")
                    return {"error": errors}

    def __del__(self):
        self.driver.close()

    def close(self):
        self.driver.close()


class TripPlanner(object):
    """Plan a trip based on flexible dates and destinations.

    A wrapper around ReservationFinder which will find reservations
    on multiple days and multiple terminals so you can plan a trip
    that fits your schedule.

    To illustrate the use case lets use an example:
    Let's say you have Friday off and you want to head out of town.
    You want to leave either Thursday after work at 5pm or Friday before noon.
    You are on the fence between going to Victoria or Tofino.
    Normally you would have to check all of these combinations yourself,
    but using TripPlanner you just give the dates and terminals you are interested
    in and it will do the rest.

    planner = TripPlanner(departing=['Sept 5, after 5pm', 'Sept 6, before noon'],
                          returning=['Sept 9'],
                          departing_from='Vancouver',
                          arriving_in=['Victoria', 'Nanaimo'])
    planner.find_reservations()
    """

    def __init__(self, departing, returning, departing_from, arriving_in):
        _departure_dates = _parse_list(departing)
        _return_dates = _parse_list(returning)
        # TODO parse date modifiers like `after 5pm`

        # get all departure/return date pairs
        self.date_pairs = []
        for departure_date in _departure_dates:
            for return_date in _return_dates:
                self.date_pairs.append((parser.parse(departure_date),
                                        parser.parse(return_date)))

        _departure_terminals = _parse_list(departing_from)
        _arrival_terminals = _parse_list(arriving_in)

        # get all departure terminals
        self.routes = []
        for terminal in _departure_terminals:
            # find matches for terminal names provided
            term_names = process.extract(terminal, choices=terminal_map.keys(), limit=2)
            term_names = [r[0] for r in term_names if r[1] > 75]  # filter matches below 75%
            # in the case of 'Vancouver' we should have two term names
            # 'Tssawassen' and 'Horseshoe Bay'
            for term_name in term_names:
                # check each arrival terminal name to see if it is a match for given
                # departure terminal name
                for arrival_term in _arrival_terminals:
                    result = process.extractOne(arrival_term,
                                                choices=terminal_map[term_name],
                                                score_cutoff=75)
                    # create a route
                    if result:
                        self.routes.append(Route(term_name, result[0]))

    def find_reservation(self, dates, route):
        res = ReservationFinder(departure_terminal=route.departure_terminal,
                                arrival_terminal=route.arrival_terminal,
                                departure_date=_format_date(dates[0]),
                                return_date=_format_date(dates[1]),
                                )
        queued_job_ids = q.job_ids  # Gets a list of job IDs from the queue
        queued_jobs = q.jobs
        print('Job ids: {}'.format(queued_job_ids))
        print('Jobs: {}'.format(queued_jobs))

        res.start()
        sailings = res.get_available_sailings()
        results = res.save_sailings_results(sailings)
        res.close()
        return results

    def find_reservations(self):
        for route in self.routes:
            for dates in self.date_pairs:
                job = q.enqueue_call(
                    func=self.find_reservation, args=(dates, route), result_ttl=5000,
                )
                print(job.get_id())
                print('{} : routes scheduled for info parsing'.format(len(self.routes)))
                return job.get_id()

    def run(self):
        return self.find_reservations()

