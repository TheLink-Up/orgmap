import unittest
import transaction

from pyramid import testing

from sqlalchemy import create_engine
from .models import (
    DBSession,
    Org,
    Base
)

import mock

from geopy.exc import GeopyError

import re
import json

def _initTestingDB():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        model = Org(
            name='name', city='city', state='state',
            url='url', lat=1.0, lng=2.0
        )
        DBSession.add(model)
    return DBSession

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        settings = {
            'geocode_service': 'foo',
            'geocode_apikey': 'bar'
        }
        self.request.registry.settings = settings
        # Patch the geocoder
        self.geoservice = mock.Mock()
        self.location = mock.MagicMock()
        self.geoservice.return_value.geocode.return_value = self.location
        self.patcher_get_geocoder_for_service = \
            mock.patch('geopy.geocoders.get_geocoder_for_service')
        self.mock_get_geocoder_for_service = self.mock_getgeoservice = \
            self.patcher_get_geocoder_for_service.start()
        self.mock_getgeoservice.return_value = self.geoservice

    def tearDown(self):
        self.session.remove()
        testing.tearDown()
        self.patcher_get_geocoder_for_service.stop()

    def test_calls_geocode_service_correctly(self):
        from .views import geocode
        org = mock.Mock(city='foo', state='bar', lat=None,lng=None)
        org = geocode(org, self.request.registry.settings)
        self.mock_getgeoservice.assert_called_once_with(
            self.request.registry.settings['geocode_service']
        )
        self.geoservice.assert_called_once_with(
            api_key=self.request.registry.settings['geocode_apikey']
        )
        self.geoservice.return_value.geocode.assert_called_once_with('foo,bar')

    def test_geocodes_city_state(self):
        from .views import geocode
        self.location.latitude = 1.0
        self.location.longitude = 2.0
        org = mock.Mock(lat=None,lng=None)
        org = geocode(org, self.request.registry.settings)
        self.assertEqual(1.0, org.lat)
        self.assertEqual(2.0, org.lng)

    def test_geocoding_error_does_not_set_latlng(self):
        from .views import geocode
        self.geoservice.return_value.geocode.side_effect = GeopyError
        org = mock.Mock(lat=None,lng=None)
        org = geocode(org, self.request.registry.settings)
        self.assertEqual(None, org.lat)
        self.assertEqual(None, org.lng)

    def test_bad_request(self):
        from .views import get_org
        from pyramid.httpexceptions import HTTPClientError
        self.assertRaises(HTTPClientError, get_org, self.request)

    def test_returns_org_without_geocoding_if_has_latlng(self):
        from .views import get_org
        self.request.GET = dict(
            city='city', state='state', name='name', url='url'
        )
        org = get_org(self.request)
        self.assertEqual(1.0, org['lat'])
        self.assertEqual(2.0, org['lng'])
        self.assertEqual('city', org['city'])
        self.assertEqual('state', org['state'])
        self.assertEqual('url', org['url'])
        self.assertEqual('name', org['name'])

    def test_geocodes_when_missing_latlng(self):
        model = Org(
            name='foo', city='city', state='state',
            url='url'
        )
        self.session.add(model)
        from .views import get_org
        self.request.GET = dict(
            city='city', state='state', name='foo', url='url'
        )
        self.location.latitude = 1.0
        self.location.longitude = 2.0
        org = get_org(self.request)
        self.assertEqual('foo', org['name'])
        self.assertEqual(1.0, org['lat'])
        self.assertEqual(2.0, org['lng'])

class GetOrCreateTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()

    def test_gets_existing(self):
        from .views import get_or_create
        org, created = get_or_create(
            self.session, Org, city='city', state='state', url='url'
        )
        self.assertFalse(created)

    def test_creates_missing(self):
        from .views import get_or_create
        org, created = get_or_create(
            self.session, Org, city='foo', state='bar', url='url'
        )
        self.assertTrue(created)
        r = self.session.query(Org).filter_by(city='foo', state='bar', url='url').all()
        r = list(r)
        self.assertEqual(1, len(r))

def _parse_jsonp(jsonptext):
    '''strip callback and return jsonp'''
    m = re.search('^(\w+)\("(.*)"\);$', jsonptext)
    callback, _json = m.groups()
    return callback, json.loads(_json.replace('\\',''))

class APIFunctionalTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()
        from pyramid.paster import get_app
        app = get_app('development.ini')
        from webtest import TestApp
        self.testapp = TestApp(app)
        # Patch the geocoder
        self.geoservice_class = mock.Mock()
        self.location = mock.MagicMock()
        self.geoservice_class.return_value.geocode.return_value = self.location
        self.patcher_get_geocoder_for_service = \
            mock.patch('geopy.geocoders.get_geocoder_for_service')
        self.mock_get_geocoder_for_service = self.mock_getgeoservice = \
            self.patcher_get_geocoder_for_service.start()
        self.mock_getgeoservice.return_value = self.geoservice_class

    def tearDowd(self):
        self.session.remove()
        testing.tearDown()
        self.patcher_get_geocoder_for_service.stop()

    def test_gets_org_json(self):
        params = dict(
            callback='foo',
            city='city',
            state='state',
            name='name',
            url='url'
        )
        res = self.testapp.get('/org', params, status=200)
        callback, _json = _parse_jsonp(res.body)
        self.assertEqual('foo', callback)
        self.assertEqual(1.0, _json['lat'])
        self.assertEqual(2.0, _json['lng'])

        for k,v in params.items():
            if k == 'callback':
                continue
            self.assertEqual(v, _json[k])

    def test_gets_org_json_missing_org(self):
        params = dict(
            callback='foo',
            city='city',
            state='state',
            name='new',
            url='http://foo.bar/baz'
        )
        self.location.latitude = 1.0
        self.location.longitude = 2.0
        res = self.testapp.get('/org', params, status=200)
        callback, _json = _parse_jsonp(res.body)
        self.assertEqual('foo', callback)
        self.assertEqual(1.0, _json['lat'])
        self.assertEqual(2.0, _json['lng'])

        for k,v in params.items():
            if k == 'callback':
                continue
            self.assertEqual(v, _json[k])
