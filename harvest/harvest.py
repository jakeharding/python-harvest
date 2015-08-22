"""
 harvest.py

 Author: Jonathan Hosmer (forked from https://github.com/lionheart/python-harvest.git)
 Date: Sat Jan 31 12:17:16 2015

"""

import requests
from base64   import b64encode as enc64
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

HARVEST_STATUS_URL = 'http://www.harveststatus.com/api/v2/status.json'
HARVEST_OAUTH_AUTHORIZE_PATH = "oauth2/authorize"

class HarvestError(Exception):
    pass

class HarvestClient(object):

    _uri = None
    _authorize_data = {}
    _authorize_url = None
    _oauth2 = False

    # def __init__(self, uri, email, password, put_auth_in_header=True):
    def __init__(self, uri, **kwargs):
        parsed = urlparse(uri)
        if not (parsed.scheme and parsed.netloc):
            raise HarvestError('Invalid harvest uri "{0}".'.format(uri))
        self.uri = uri.rstrip('/')
        
        self.oauth2 = bool(kwargs.get('client_id'))
        if self.oauth2:
            self.authorize_url = '%s/%s' % (self.uri, HARVEST_OAUTH_AUTHORIZE_PATH)
            self.authorize_data = kwargs

        # self.__email    = email.strip()
        # self.__password = password
        # self.__headers = {
        #     'Accept'        : 'application/json',
        #     # 'User-Agent'    : 'Mozilla/5.0',  # 'TimeTracker for Linux' -- ++ << >>
        # }
        # if put_auth_in_header:
        #     auth_string = '{self.email}:{self.password}'.format(self=self)
        #     auth_string = enc64(bytes(auth_string, 'ascii'))
        #     self.__headers['Authorization'] = 'Basic {0}'.format(auth_string)

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, value):
        self._uri = value

    @property
    def authorize_url(self):
        return self._authorize_url

    @authorize_url.setter
    def authorize_url(self, value):
        self._authorize_url = value

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
    


    # @property
    # def email(self):
    #     return self.__email
    # @property
    # def password(self):
    #     return self.__password

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

    def _get(self, path='/', data=None):
        return self._request('GET', path, data)
    def _post(self, path='/', data=None):
        return self._request('POST', path, data)
    def _put(self, path='/', data=None):
        return self._request('PUT', path, data)
    def _delete(self, path='/', data=None):
        return self._request('DELETE', path, data)
    def _request(self, method='GET', path='/', data=None):
        url = '{self.uri}{path}'.format(self=self, path=path)
        kwargs = {
            'method'  : method,
            'url'     : '{self.uri}{path}'.format(self=self, path=path),
            'headers' : self.__headers,
            'data'    : data,
        }
        if not oauth2 and 'Authorization' not in self.__headers:
            kwargs['auth'] = (self.email, self.password)

        try:
            resp = requests.request(**kwargs)
            if 'DELETE' not in method:
                return resp.json()
            return resp
        except Exception as e:
            raise HarvestError(e)


# class HarvestOauth(Harvest):
#     authorize_url = None
#     authorize_data = {}
#     oauth2 = True

#     def __init__(self, domain, client_id, redirect):
#         self.__uri = domain.rstrip('/')
#         self.authorize_url = '%s/oauth2/authorize'
#         redirect = urlparse(redirect)
#         self.authorize_data = {
#             'redirect_uri': redirect,
#             'client_id': client_id
#         }
#         self.get_auth_code()

#     def get_auth_code(self):
#         rsp = self._get(self.authorize_url, self.authorize_data)
#         import pdb; pdb.set_trace()


def status():
    try:
        status = requests.get(HARVEST_STATUS_URL).json().get('status', {})
    except:
        status = {}
    return status
