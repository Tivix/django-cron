
# https://gist.github.com/bubenkoff/005ea57b63251dafe81f
import sys

from django.utils.importlib import import_module
from django.core.urlresolvers import clear_url_caches
from django.template import context, base, loader
from django.utils import translation
from django.utils.translation import trans_real


def reload_settings(settings):
    """Special routine to reload django settings, including:
    urlconf module, context processor, templatetags settings, database settings.
    This also includes re-setting up sqlalchemy database settings. Environment chosen is always TestEnv."""
 
    # resetup django settings
    settings._setup()
 
    # check if there's settings to reload
    if hasattr(settings, 'ROOT_URLCONF'):
        if settings.ROOT_URLCONF in sys.modules:
            reload(sys.modules[settings.ROOT_URLCONF])
        import_module(settings.ROOT_URLCONF)
        settings.LANGUAGE_CODE = 'en'  # all tests should be run with English by default
 
        # Make the ConnectionHandler use the new settings, otherwise the ConnectionHandler will have old configuraton.
        from django.db.utils import ConnectionHandler
        import django.db
        from django.db.utils import load_backend
        import django.db.transaction
        import django.db.models
        import django.db.models.sql.query
        import django.core.management.commands.syncdb
        import django.db.models.sql.compiler
        import django.db.backends
        import django.db.backends.mysql.base
        import django.core.management.commands.loaddata
 
        # all modules which imported django.db.connections should be changed to get new ConnectionHanlder
        django.db.models.sql.compiler.connections = django.db.models.connections = \
            django.core.management.commands.loaddata.connections = \
            django.db.backends.connections = django.db.backends.mysql.base.connections = \
            django.core.management.commands.syncdb.connections = django.db.transaction.connections = \
            django.db.connections = django.db.models.base.connections = django.db.models.sql.query.connections = \
            ConnectionHandler(settings.DATABASES)
 
        # default django connection and backend should be also changed
        django.db.connection = django.db.connections[django.db.DEFAULT_DB_ALIAS]
        django.db.backend = load_backend(django.db.connection.settings_dict['ENGINE'])
 
        import django.core.cache
        django.core.cache.cache = django.core.cache.get_cache(django.core.cache.DEFAULT_CACHE_ALIAS)
 
        # clear django urls cache
        clear_url_caches()
        # clear django contextprocessors cache
        context._standard_context_processors = None
        # clear django templatetags cache
        base.templatetags_modules = None
 
        # reload translation files
        reload(translation)
        reload(trans_real)
 
        # clear django template loaders cache
        loader.template_source_loaders = None
        from django.template.loaders import app_directories
        reload(app_directories)