import anyjson
import restkit

class restClient(object):
    """Client object for making requests."""
    def __init__(self, config):
        """Sets up config and restkit based client"""
        self._config = config
        self._client = restkit.RestClient()
        return self

    def _is_response(self, response, status_code):
        '''Checks if response status code is same as requested value'''
        return True if response.status_int == status_code else False

    def _deserialize_response(self, response):
        '''
            Deserializes response into native python objects via anyjson or
            via feedparser.parse method if xml. Xml parser can be overridden
            via configuration using the 'xml_parser' key
        '''
        if self._is_response(response, 200):
            if (response.headers['content-type'].startswith('text/javascript') or response.headers['content-type'].startswith('text/html') and response.body.startswith('{')):
                return anyjson.deserialize(response.body)   
            elif response.headers['content-type'].startswith('text/xml'):
                return response.body
            else:
                return response.body
        return response

    def request(self, method, uri, headers={}, body=None, deserialize=True, **params):
        '''Wrapper method around restkit client. Deserializes response'''
        if method == 'GET':
            response = self._client.request(
                method,
                uri,
                headers=headers,
                **params)
        elif method == 'POST':
                response = self._client.request(
                    method, 
                    uri, 
                    headers=headers, body=body)
        return self._deserialize_response(response) if deserialize is True else response

    def debug(self, debuglevel):
        restkit.debuglevel = debuglevel
