"""
pyley Python client for an open-source graph database Cayley

:copyright: (c) 2014 by Ziya SARIKAYA @ziyasal.
:license: MIT, see LICENSE for more details.

"""
import json
import requests

__title__ = 'pyley'
__version__ = '0.1.1-dev'
__author__ = 'Ziya SARIKAYA @ziyasal'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 Ziya SARIKAYA @ziyasal'


class CayleyResponse(object):
    def __init__(self, raw_response, result):
        self.r = raw_response
        self.result = result


class CayleyClient(object):
    def __init__(self, url="http://localhost:64210", version="v1"):
        self.url = "%s/api/%s/query/gremlin" % (url, version)

    def Send(self, query):
        if isinstance(query, str):
            r = requests.post(self.url, data=query)
            return CayleyResponse(r, r.json())
        elif isinstance(query, _GremlinQuery):
            r = requests.post(self.url, data=str(query))
            return CayleyResponse(r, r.json())
        else:
            raise Exception("Invalid query parameter in Send")


class _GremlinQuery(object):
    queryDeclarations = None

    def __init__(self):
        self.queryDeclarations = []

    def __str__(self):
        return ".".join([str(d) for d in self.queryDeclarations])

    def _put(self, token, *parameters):
        q = _QueryDefinition(token, *parameters)
        self.queryDeclarations.append(q)


class GraphObject(object):
    def V(self):
        return _Path("g.V()")

    def V(self, *node_ids):
        builder = []
        l = len(node_ids)
        for index, node_id in enumerate(node_ids):
            if index == l - 1:
                builder.append(u"'{0:s}'".format(node_id))
            else:
                builder.append(u"'{0:s}',".format(node_id))

        return _Path(u"g.V({0:s})".format("".join(builder)))

    def M(self):
        return _Path("g.Morphism()")

    def Vertex(self):
        return self.V()

    def Vertex(self, *node_ids):
        if len(node_ids) == 0:
            return self.V()

        return self.V(node_ids)

    def Morphism(self):
        return self.M()

    def Emit(self, data):
        return "g.Emit({0:s})".format(json.dumps(data, default=lambda o: o.__dict__))


class _Path(_GremlinQuery):
    def __init__(self, parent):
        _GremlinQuery.__init__(self)
        self._put(parent)

    def Out(self, label):
        self._put("Out('%s')", label)

        return self

    def All(self):
        self._put("All()")

        return self

    def In(self, label):
        self._put("In('%s')", label)

        return self

    def Has(self, label, val):
        self._put("Has('%s','%s')", label, val)

        return self

    def Follow(self, query):
        if isinstance(query, str):
            self._put("Follow(%s)", query)
        elif isinstance(query, _GremlinQuery):
            self._put("Follow(%s)", query.build())
        else:
            raise Exception("Invalid parameter in follow query")

        return self

    def GetLimit(self, val):
        self._put("GetLimit(%d)", val)

        return self

    def Both(self, val):
        self._put("Both('%s')", val)

        return self

    def build(self):
        return str(self)


class _QueryDefinition(object):
    def __init__(self, token, *parameters):
        self.token = token
        self.parameters = parameters

    def __str__(self):
        if len(self.parameters) > 0:
            return str(self.token) % self.parameters
        else:
            return str(self.token)
