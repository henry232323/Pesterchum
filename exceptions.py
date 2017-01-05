class IncompleteMessageError(Exception):
    def __init__(self, message):
        self.message = message
        error = "\"{}\" is not complete message".format(message)
        super(__class__, self).__init__(error)
