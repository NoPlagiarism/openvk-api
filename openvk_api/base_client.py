from httpx import Client as Session, URL
import threading, time
from .exceptions import AuthFailed, BadPassword, LoginRequired, RawApiError, RawHTTPApiError, AuthRequired
from .consts import DEFAULT_INSTANCE, SESSION_HEADERS
from json.decoder import JSONDecodeError

GET_TOKEN_PATH = "/token"


class OpenVkClient:
    RPS_DELAY = 0.5  # ~2 requests per second

    def __init__(self, instance=None, token=None, session=None):
        self.instance = URL(instance) if instance is not None else URL(DEFAULT_INSTANCE)
        self.session = Session(base_url=self.instance, headers=SESSION_HEADERS) if session is None else session

        self.token = token

        self.lock = threading.Lock()
        self.last_request = 0.0

    def auth_with_password(self, login, password, code=None):
        if any((login is None, password is None)):
            raise LoginRequired()
        token_url = self.instance.join(GET_TOKEN_PATH)
        req_params = {"grant_type": "password", "username": login, "password": password}
        if code is not None:
            req_params["code"] = code
        resp = self.session.get(token_url, params=req_params)
        resp_json = resp.json()
        if resp.status_code == 200:
            self.token = resp_json["access_token"]
            return
        # TODO: ADD 2FA SUPPORT
        if resp_json["error_code"] == 28:
            raise BadPassword()
        raise AuthFailed(self, resp_json)

    def check_token(self):
        if self.token is None:
            raise AuthRequired()
        try:
            return self.method("Ovk.test")["authorized"]
        except Exception:
            return False

    @staticmethod
    def _get_error_by_json_response(resp):
        if "error_code" not in resp:
            return
        return {5: AuthRequired()}.get(resp["error_code"])

    def method(self, method, values=None, raw=False, force_unauthorized=False, http_method="GET", files=None):
        if files is not None and http_method != "POST":
            raise AttributeError("When sending files, http_method must be POST")
        values = values.copy() if values is not None else dict()

        if "access_token" not in values and self.token is not None and not force_unauthorized:
            values["access_token"] = str(self.token)

        with self.lock:
            delay = self.RPS_DELAY - (time.time() - self.last_request)
            if delay > 0:
                time.sleep(delay)

            resp = self.session.request(
                method=http_method,
                url=str(self.instance.join("/method/")) + method,
                params=values,
                files=files
            )
        if resp.status_code == 200:
            response = resp.json()
        else:
            try:
                response = resp.json()
                err = self._get_error_by_json_response(response)
                if err is not None:
                    raise err
                raise RawApiError(self, response, method)
            except JSONDecodeError:
                raise RawHTTPApiError(self, resp, method)
        return response if raw else response["response"]

    def get_api(self):
        return OpenVkApiMethod(self)


class OpenVkApiMethod:
    def __init__(self, openvk, method=None):
        self._vk, self._method = openvk, method

    def __getattr__(self, method):
        if '_' in method:
            m = method.split('_')
            method = m[0] + ''.join(i.title() for i in m[1:])

        return OpenVkApiMethod(self._vk, (self._method + "." if self._method else "") + method)

    def __call__(self, _options=None, **kwargs):
        if _options is None:
            _options = dict()
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple, set)):
                kwargs[key] = ",".join(str(x) for x in value)
        if "method" in _options:
            _options["http_method"] = _options.pop("method")

        return self._vk.method(self._method, kwargs, **_options)
