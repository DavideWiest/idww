import json
import codecs
import os.path
from modules.sys_helper import CLogger

cl = CLogger()

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError)


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        cl.logprint('SAVED: {0!s}'.format(new_settings_file))



def get_client(settings_file_path, username, password, proxy=""):

    device_id = None
    try:

        settings_file = settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            cl.logprint('ERROR IN get_client: Unable to find file: {0!s}'.format(settings_file))

            # login new
            if proxy != "":
                api = Client(username, password, on_login=lambda x: onlogin_callback(x, settings_file_path), proxy=proxy)
            else:
                api = Client(username, password, on_login=lambda x: onlogin_callback(x, settings_file_path))
        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            #logprint('REUSING CACHED SETTINGS: {0!s}'.format(settings_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            if proxy != "":
                api = Client(username, password, settings=cached_settings, proxy=proxy)
            else:
                api = Client(username, password, settings=cached_settings)
        
        return api

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        cl.logprint('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        if proxy != "":
            api = Client(username, password, device_id=device_id, on_login=lambda x: onlogin_callback(x, settings_file_path), proxy=proxy)
        else:
            api = Client(username, password, device_id=device_id, on_login=lambda x: onlogin_callback(x, settings_file_path))
        
        return api

    except ClientLoginError as e:
        cl.logprint('ClientLoginError {0!s}'.format(e))
    except ClientError as e:
        cl.logprint('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
    except Exception as e:
        cl.logprint('Unexpected Exception: {0!s}'.format(e))
