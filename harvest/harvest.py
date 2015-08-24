"""
 harvest.py

 Author: Jonathan Hosmer (forked from https://github.com/lionheart/python-harvest.git)
 Date: Sat Jan 31 12:17:16 2015

"""

import requests
from base64   import b64encode as enc64
try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode

from .constants import *


class HarvestError(Exception):
    pass

class HarvestClient(object):

    _uri = None
    _authorize_data = {}
    _authorize_url = None
    _oauth2 = False
    _email = None
    _password = None
    _content_type = None
    _headers = {}

    _errors = {
        'invalid_uri': 'Invalid harvest uri "{0}".'
    }

    def __init__(self, uri, content_type=None, **kwargs):
        parsed = urlparse(uri)
        if not (parsed.scheme and parsed.netloc):
            raise HarvestError(self._errors.get('invalid_uri').format(uri))
        self.uri = uri

        if not content_type:
            self.content_type = HTTPContentType.JSON
        else:
            self.content_type = content_type

        #Reset the headers on every initialization
        self.headers = {
            HTTPHeader.ACCEPT: self.content_type
        }
        
        self.oauth2 = bool(kwargs.get(OauthKey.CLIENT_ID))
        if self.oauth2:
            self.authorize_data = {
                OauthKey.CLIENT_ID: kwargs.get(OauthKey.CLIENT_ID),
                OauthKey.REDIRECT_URI: kwargs.get(OauthKey.REDIRECT_URI),
                OauthKey.RESPONSE_TYPE: OauthValue.CODE
            }
            self.authorize_url = '%s/%s' %(self.uri, HARVEST_OAUTH_AUTHORIZE_PATH)
            
        else:
            self.email    = kwargs.get(BasicKey.EMAIL)
            self.password = kwargs.get(BasicKey.PASSWORD)
            auth_string = '{self.email}:{self.password}'.format(self=self)
            auth_string = enc64(bytes(auth_string, 'ascii'))
            self.set_header(HTTPHeader.AUTH, HTTPHeader.BASIC_AUTH_FORMAT.format(auth_string))
            

        
    def set_header(self, key, value):
        self._headers.update({
            key: value
        })

    def get_tokens(self, code, secret):
        data = {
            OauthKey.CODE: code,
            OauthKey.CLIENT_ID: self.authorize_data.get(OauthKey.CLIENT_ID),
            OauthKey.CLIENT_SECRET: secret,
            # 'redirect_uri': self.authorize_data.get('redirect_uri'),
            OauthKey.GRANT_TYPE: OauthValue.AUTH_CODE
        }
        self.set_header(HTTPHeader.CONTENT_TYPE, HTTPContentType.FORM_ENCODED)
        rsp = self._post(HARVEST_OAUTH_TOKEN_PATH, params=data) #Data must be in query parameters
        self.set_header(HTTPHeader.CONTENT_TYPE, self.content_type) #Reset this content type
        return (rsp.get(OauthKey.ACCESS_TOKEN), rsp.get(OauthKey.REFRESH_TOKEN))

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, val):
        self._content_type = val

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, value):
        self._uri = value.rstrip('/')

    @property
    def token_url(self):
        return '%s/%s' %(self.uri, HARVEST_OAUTH_TOKEN_PATH)

    @property
    def authorize_url(self):
        return self._authorize_url

    @authorize_url.setter
    def authorize_url(self, value):
        self._authorize_url = '%s?%s' %(value, urlencode(self.authorize_data))

    @property
    def authorize_data(self):
        return self._authorize_data
    
    @authorize_data.setter
    def authorize_data(self, val):
        self._authorize_data = val

    @property
    def oauth2(self):
        return self._oauth2

    @oauth2.setter
    def oauth2(self, val):
        self._oauth2 = val

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, val):
        self._email = val.strip()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        self._password = val

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, val):
        self._headers = val
    

    @property
    def status(self):
        return status()

    ## Accounts

    @property
    def who_am_i(self):
        return self._get('/account/who_am_i')

    ## Client Contacts

    def contacts(self, updated_since=None):
        url = '/contacts'
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def get_contact(self, contact_id):
        return self._get('/contacts/{0}'.format(contact_id))

    def create_contact(self, new_contact_id, fname, lname, **kwargs):
        url  = '/contacts/{0}'.format(new_contact_id)
        kwargs.update({'first-name':fname, 'last-name':lname})
        return self._post(url, data=kwargs)

    def client_contacts(self, client_id, updated_since=None):
        url = '/clients/{0}/contacts'.format(client_id)
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def update_contact(self, contact_id, **kwargs):
        url = '/contacts/{0}'.format(contact_id)
        return self._put(url, data=kwargs)

    def delete_contact(self, contact_id):
        return self._delete('/contacts/{0}'.format(contact_id))

    ## Clients

    def clients(self, updated_since=None):
        url = '/clients'
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def get_client(self, client_id):
        return self._get('/clients/{0}'.format(client_id))

    def create_client(self, new_client_id, name, **kwargs):
        url  = '/clients/{0}'.format(new_client_id)
        kwargs.update({'name':name})
        return self._post(url, data=kwargs)

    def update_client(self, client_id, **kwargs):
        url = '/clients/{0}'.format(client_id)
        return self._put(url, data=kwargs)

    def toggle_client_active(self, client_id):
        return self._get('/clients/{0}/toggle'.format(client_id))

    def delete_client(self, client_id):
        return self._delete('/clients/{0}'.format(client_id))

    ## Expense Categories

    @property
    def expense_categories(self):
        return self._get('/expense_categories')

    def create_expense_category(self, new_expense_category_id, **kwargs):
        return self._post('/expense_categories/{0}'.format(new_expense_category_id), data=kwargs)

    def update_expense_category(self, expense_category_id, **kwargs):
        return self._put('/expense_categories/{0}'.format(expense_category_id), data=kwargs)

    def get_expense_category(self, expense_category_id):
        return self._get('/expense_categories/{0}'.format(expense_category_id))

    def delete_expense_category(self, expense_category_id):
        return self._delete('/expense_categories/{0}'.format(expense_category_id))

    def toggle_expense_category_active(self, expense_category_id):
        return self._get('/expense_categories/{0}/toggle'.format(expense_category_id))

    ## Time Tracking

    @property
    def today(self):
        return self._get('/daily')

    def get_day(self, day_of_the_year=1, year=2012):
        return self._get('/daily/{0}/{1}'.format(day_of_the_year, year))

    def get_entry(self, entry_id):
        return self._get('/daily/show/{0}'.format(entry_id))

    def toggle_timer(self, entry_id):
        return self._get('/daily/timer/{0}'.format(entry_id))

    def add(self, data):
        return self._post('/daily/add', data)

    def delete(self, entry_id):
        return self._delete('/daily/delete/{0}'.format(entry_id))

    def update(self, entry_id, data):
        return self._post('/daily/update/{0}'.format(entry_id), data)

    def _get(self, path='/', data=None, params=None):
        return self._request('GET', path, data, params)
    def _post(self, path='/', data=None, params=None):
        return self._request('POST', path, data, params=params)
    def _put(self, path='/', data=None, params=None):
        return self._request('PUT', path, data, params=params)
    def _delete(self, path='/', data=None):
        return self._request('DELETE', path, data)
    def _request(self, method='GET', path='/', data=None, params=None):
        url = '{self.uri}{path}'.format(self=self, path=path)
        kwargs = {
            'method'  : method,
            'url'     : url,
            'headers' : self.headers,
            'data'    : data,
            'params'  : params
        }
        if not self.oauth2 and 'Authorization' not in self.headers:
            kwargs['auth'] = (self.email, self.password)

        try:
            resp = requests.request(**kwargs)
            if 'DELETE' not in method:
                return resp.json()
            return resp
        except Exception as e:
            raise HarvestError(e)


def status():
    try:
        status = requests.get(HARVEST_STATUS_URL).json().get('status', {})
    except:
        status = {}
    return status
