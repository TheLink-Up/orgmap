from pyramid.view import view_config
from pyramid.httpexceptions import HTTPClientError

import logging
log = logging.getLogger(__name__)

from sqlalchemy.sql.expression import ClauseElement

import geopy.geocoders
import geopy.exc

from .models import DBSession, Org

db = DBSession

@view_config(route_name='org', renderer='jsonp')
def get_org(request):
    log.info("Getting org for request {0}".format(request.GET))
    for k in ('city', 'state', 'name', 'url'):
        if k not in request.GET:
            log.error("Request is missing one of city, state, name or url")
            raise HTTPClientError("Missing required parameter")
    city = request.GET['city']
    state = request.GET['state']
    name = request.GET['name']
    url = request.GET['url']
    # Get or create org for query
    org, created = get_or_create(db, Org, city=city, state=state, name=name, url=url)
    # Geocode if missing lat and/or lng
    if not org.lat or not org.lng:
        org = geocode(org, request.registry.settings)
        # Save changes
        db.flush()
    # Return the org
    return org

def geocode(org, settings):
    '''
    Geocode the org's city and state and
    and update the org(just the object aka no org.save())

    :param models.Org org: organization to geocode
    :param dict settings: ini settings
    :return: models.Org with lat and lng filled out
    '''
    geo_service_class = geopy.geocoders.get_geocoder_for_service(
        settings['geocode_service']
    )
    geoservice = geo_service_class(api_key=settings['geocode_apikey'])
    citystate = "{0},{1}".format(org.city, org.state)
    log.info("Geocoding {0}".format(citystate))
    try:
        location = geoservice.geocode(citystate)
        org.lat = location.latitude
        org.lng = location.longitude
    except geopy.exc.GeopyError as e:
        # Just do nothing then if there was an error
        # eventually we will log this but I don't know how to
        # do logging quite yet
        log.warning("Could not geocode {0} because {1}".format(citystate,e))
        pass
    return org

def get_or_create(session, model, defaults=None, **kwargs):
    '''
    http://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
    '''
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True
