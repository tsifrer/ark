class P2PException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        data = {'status_code': self.status_code, 'message': self.message}
        if self.payload:
            data.update(self.payload)
        return data
