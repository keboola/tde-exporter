# upload of tde via writer excpetion
class UploadException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

    def __str__(self):
        return 'UploadError: {0}'.format(self.message)
