class OpenVkApiError(BaseException):
    pass


class AuthRequired(OpenVkApiError):
    pass


class LoginRequired(OpenVkApiError):
    pass


class BadPassword(OpenVkApiError):
    pass


class TwoFactorError(OpenVkApiError):
    def __init__(self, wrong_code=False):
        self.wrong_code = wrong_code


class RawHTTPApiError(OpenVkApiError):
    def __init__(self, openvk, resp, method):
        self.openvk = openvk
        self.response = resp
        self.method = method


class RawApiError(OpenVkApiError):
    def __init__(self, openvk, resp_json, method):
        self.openvk = openvk
        self.response = resp_json
        self.method = method

    def __getitem__(self, item):
        return self.response[item]


class AuthFailed(RawApiError):
    def __init__(self, openvk, resp_json):
        super(AuthFailed, self).__init__(openvk, resp_json, "internal.acquireToken")
