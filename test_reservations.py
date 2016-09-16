import unittest
from reservations import TripPlanner, Route
from terminals import *


class TestTripPlanner(unittest.TestCase):

    def test_trip_planner(self):
        planner = TripPlanner(departing=['Sept 5', 'Sept 6'],
                              returning=['Sept 9'],
                              departing_from='Vancouver',
                              arriving_in=['Victoria', 'Nanaimo'])
        expected_routes = [Route(VANCOUVER_HORSESHOE_BAY, NANAIMO_DEPARTURE_BAY),
                           Route(VANCOUVER_TSAWWASSEN, NANAIMO_DUKE_POINT),
                           Route(VANCOUVER_TSAWWASSEN, VICTORIA)
                           ]
        self.assertCountEqual(expected_routes, planner.routes)
        print(planner.date_pairs)

    def test_trip_planner_vancouver_langdale(self):
        planner = TripPlanner(departing=['Sept 5', 'Sept 6'],
                              returning=['Sept 9'],
                              departing_from='Vancouver',
                              arriving_in='Langdale')
        expected_routes = [Route(VANCOUVER_HORSESHOE_BAY, LANGDALE)]
        self.assertCountEqual(expected_routes, planner.routes)

    def test_trip_planner_nanaimo_vancouver(self):
        planner = TripPlanner(departing=['Sept 5', 'Sept 6'],
                              returning=['Sept 9'],
                              departing_from='Nanaimo',
                              arriving_in='Vancouver')
        expected_routes = [Route(NANAIMO_DUKE_POINT, VANCOUVER_TSAWWASSEN),
                           Route(NANAIMO_DEPARTURE_BAY, VANCOUVER_HORSESHOE_BAY)]
        self.assertCountEqual(expected_routes, planner.routes)
