import pytest
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.Session import Session
from PySmartSkies.Credentials import DIS_Credentials,CVMS_Credentials
from credentials import cvms_credentials, dis_credentials
from geojson import Point, LineString, FeatureCollection, loads
import json
authenticated_api: DIS_API = None

@pytest.fixture(autouse=True)
def authenticate_cvms():
    global authenticated_api
    if authenticated_api is None:
        session = Session(cvms_credentials, dis_credentials)
        api = DIS_API(session)
        api.authenticate()
        authenticated_api = api
    yield

def test_get_obstacles():
    linestring = LineString([(-4.105086, 56.784097), (-3.675487, 56.712680)], validate=True)
    point = Point((-4.105086, 56.784097), validate=True)
    _range = 15000
    obstacles = authenticated_api.get_aware_obstacle(linestring, _range)
    assert obstacles is not None
    obstacles = authenticated_api.get_aware_obstacle(point, _range)
    assert obstacles is not None


def test_get_population():
    linestring = LineString([(-4.105086, 56.784097), (-3.675487, 56.712680)], validate=True)
    point = Point((-4.105086, 56.784097), validate=True)
    _range = 100
    population = authenticated_api.get_aware_population(linestring, _range)
    assert population is not None
    population = authenticated_api.get_aware_population(point, _range)
    assert population is not None


def test_get_terrain():
    linestring = LineString([(-4.105086, 56.784097), (-3.675487, 56.712680)], validate=True)
    point = Point((-4.105086, 56.784097), validate=True)
    _range = 100
    terrain = authenticated_api.get_aware_terrain(linestring, _range)
    assert terrain is not None
    terrain = authenticated_api.get_aware_terrain(point, _range)
    assert terrain is not None


def test_get_danger():
    linestring = LineString([(-4.105086, 56.784097), (-3.675487, 56.712680)], validate=True)
    point = Point((-4.105086, 56.784097), validate=True)
    _range = 100
    danger = authenticated_api.get_aware_danger(linestring, _range)
    assert danger is not None
    danger = authenticated_api.get_aware_danger(point, _range)
    assert danger is not None

def test_get_enroute():
    linestring = LineString([(-4.105086, 56.784097), (-3.675487, 56.712680)], validate=True)
    point = Point((-4.105086, 56.784097), validate=True)
    _range = 100
    enroute = authenticated_api.get_aware_enroute(linestring, _range)
    assert enroute is not None
    enroute = authenticated_api.get_aware_enroute(point, _range)
    assert enroute is not None

def test_get_restricted():
    linestring = LineString([(-4.105086, 56.784097), (-3.675487, 56.712680)], validate=True)
    point = Point((-4.105086, 56.784097), validate=True)
    _range = 100
    restricted = authenticated_api.get_aware_restricted(linestring, _range)
    assert restricted is not None
    restricted = authenticated_api.get_aware_restricted(point, _range)
    assert restricted is not None

def test_get_celltowers():
    linestring = LineString([(-4.105086, 56.784097), (-3.675487, 56.712680)], validate=True)
    point = Point((-4.105086, 56.784097), validate=True)
    _range = 100
    celltowers = authenticated_api.get_aware_celltowers(linestring, _range)
    assert celltowers is not None
    celltowers = authenticated_api.get_aware_celltowers(point, _range)
    assert celltowers is not None

def test_get_weather_data():
    lat = -4.425421176
    lon = 55.9064512595
    weather_data = authenticated_api.get_weather_data(lat, lon)
    assert type(weather_data) == dict