from model import Model
import json


class ClassEncoder(json.JSONEncoder):
    """A custom JSON encoder that defaults to using the __dict__ method for
    database Model classes and subclasses. This allows for automatic
    conversion to JSON.
    """
    def default(self, o):
        """(ClassEncoder, Object) -> Object
        Returns a dict if the object is Model class or subclass, or the
        default serializable object otherwise.
        """
        if isinstance(o, Model):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


class Response:
    """A response to an AJAX request. Contains the data for the response,
    extra parameters for the response, the result indicating operation
    success or failure, and a message describing operation success or
    failure.
    """

    def __init__(self, result=False, msg='', data=None, params=None):
        """(Response, Bool, str, obj, dict) -> None
        Creates a response using the given data.
        """
        self.response = {'data': data, 'result': result, 'msg': msg}
        if params:
            self.update_params(params)

    def get_data(self):
        """(Response) -> obj
        Returns the data for the response.
        """
        return self.response['data']

    def get_params(self):
        """(Response) -> dict
        Returns the parameters for the response.
        """
        return self.response

    def to_json(self):
        """(Response) -> str
        Converts the response to JSON for sending over the internet. The
        custom encoder defined above is used for the conversion.
        """
        return json.dumps(self.response, cls=ClassEncoder)

    def update_params(self, params):
        """(Response, dict) -> None
        Updates the parameters for the response with the given dict.
        """
        self.response.update(params)

    def __str__(self):
        """(Response) -> str
        Converts the response to a printable string.
        """
        return str(self.response)

    def __len__(self):
        """(Response) -> int
        Returns the number of elements in the response data.
        """
        return len(self.get_data())

    def __eq__(self, other):
        """(Response, Response) -> bool
        Returns True if the response data is the same.
        """
        return self.get_data() == other.get_data()

    def __nonzero__(self):
        """(Response) -> bool
        Returns True if the result was true, and False otherwise.
        """
        return self.response['result']
