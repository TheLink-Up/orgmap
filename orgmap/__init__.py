from pyramid.config import Configurator
from pyramid.renderers import JSONP

from sqlalchemy import engine_from_config

from .models import DBSession, Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_tm')
    config.add_renderer('jsonp', JSONP(param_name='callback'))
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('org', '/org')
    config.scan()
    return config.make_wsgi_app()
