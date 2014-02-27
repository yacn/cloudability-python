import os
import requests
import pprint
import json
pp = pprint.PrettyPrinter(indent=4).pprint

class Cloudability:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def billing_report(self, by='period', **kwargs):
        return BillingReport(self.auth_token, by=by, **kwargs).results

    def list_current_cost_reports(self):
        return CostReport(self.auth_token).current()

    def list_cost_report_measures(self):
        return CostReport(self.auth_token).measures()

    def organization(self, oid=''):
        return Organizations(self.auth_token, oid=oid).results

#    def cost_report(self):
#        return CostReport(self.auth_token).results

class Base(Cloudability):
    _base_api_url = 'https://app.cloudability.com/api/1'

    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.api_url = self._base_api_url + self._api_endpoint
        
    def _fetch_report(self, data={}, endpoint=''):
        data.update({'auth_token': self.auth_token})
        return requests.get(self.api_url + endpoint, params=data)

class Report:
    def __init__(self, results):
        self._raw = results
        self.entries = []
        for entry in results:
            e = Entry(entry)
            self.entries.append(e)

    def __str__(self):
        string = "[\n"
        for e in self.entries:
            string += "\n".join((2*" ") + i for i in e.__str__().splitlines())
            string += "\n"
        string = string.rstrip("\n")
        string += "\n]"
        return string

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, key):
        return self.entries[key]

    def __iter__(self):
        return iter(self.entries)

    def head(self):
        return self.entries[0]

    def tail(self):
        return self.entries[1:]

    def init(self):
        return self.entries[:-1]

    def last(self):
        return self.entries[-1]

    def drop(self, n):
        return self.entries[n:]

    def take(self, n):
        return self.entries[:n]

class Entry:
    def __init__(self, results):
        self._raw = results 
#        for key, val in json.iteritems():
#            setattr(self, key, val)

    def __getattr__(self, name):
        self._raw[name]

    def __str__(self):
        return json.dumps(self._raw, indent=2)

    def __repr__(self):
        return json.dumps(self._raw)

    def __unicode__(self):
        return unicode(json.dumps(self._raw, indent=2))


class Organizations(Base):
    _api_endpoint = '/organizations'

    def __init__(self, auth_token, oid=''):
        Base.__init__(self, auth_token)
        if len(oid) == 0:
            self.results = Report(self._fetch_report().json())
        else:
            self.results = Report(self._fetch_report(endpoint='/%s' % oid).json())
        #self.invitations = self.results['invitations']


class CostReport(Base):
    _api_endpoint = '/reporting/cost'

    def __init__(self, auth_token):
        Base.__init__(self, auth_token)
#        self.raw_results = self._fetch_report().json()
#        self.results = Report(self.raw_results)

    def current(self):
        return Report(self._fetch_report().json())

    def measures(self):
        results = self._fetch_report(endpoint='/measures').json()
        return Report(results)

    def filters(self):
        results = self._fetch_report(endpoint='/filters').json()
        return Report(results)

    def run(self, start, end, dimensions, metrics, sort_by, order, max_results, chart, offset=0):
        params = {
            'start_date': start, 'end_date': end, 'dimensions': dimensions,
            'metrics': metrics, 'sort_by': sort_by, 'order': order,
            'offset': offset, 'max_results': max_results, 'chart': chart
        }
        results = self._fetch_report(endpoint='/run', data=params).json()
        return Report(results)

    def enqueue(self, start, end, dimensions, metrics, sort_by, order, max_results, chart, offset=0):
        params = {
            'start_date': start, 'end_date': end, 'dimensions': dimensions,
            'metrics': metrics, 'sort_by': sort_by, 'order': order,
            'offset': offset, 'max_results': max_results, 'chart': chart
        }
        results = self._fetch_report(endpoint='/enqueue', data=params).json()
        return Report(results)

    def check_state(self, rid):
        ep = '/reports/%s/state' % rid
        results = self._fetch_report(endpoint=ep).json()
        return Report(results)

    def get(self, rid):
        ep = '/reports/%s/results' % rid
        results = self._fetch_report(endpoint=ep).json()
        return Report(results)


class BillingReport(Base):
    _api_endpoint = '/billing_reports'

    def __init__(self, auth_token, by='period', **kwargs):
        Base.__init__(self, auth_token)
        self.by         = by
        self.service    = kwargs.get('service', None)
        self.vendor     = kwargs.get('vendor', None)
        self.period     = kwargs.get('period', None)
        self.credential = kwargs.get('credential', None)
        self.account    = kwargs.get('account', None)
        self.req_data   = {
            'by': self.by, 'service': self.service, 'vendor': self.vendor,
            'period': self.period, 'credential': self.credential,
            'account': self.account
        }
        self.raw_results    = self._fetch_report(data=self.req_data).json()
        self.results = Report(self.raw_results)




c = Cloudability(os.environ['CLOUDABILITY_API_TOKEN'])
print "%s" % c.billing_report()
#print "%s" % c.cost_report()
#print "%s" % c.list_current_cost_reports()
#print "%s" % c.list_cost_report_measures()
#print "%s" % c.billing_report(by='service', vendor=1)
#print "%s" % c.organization()
