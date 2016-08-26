import pytest
from reservations import TripPlanner, Route


def test_trip_planner():
    planner = TripPlanner(departing=['Sept 5, after 5pm', 'Sept 6, before noon'],
                          returning=['Sept 9'],
                          departing_from='Vancouver',
                          arriving_in=['Victoria', 'Nanaimo'])
    expected_routes = [Route('vancouver tsawwassen', 'Victoria ')
