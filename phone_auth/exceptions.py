class AuthenticationMethodEmpty(Exception):
    """Exception raised if AUTHENTICATION_METHODS is set to
    empty set in settings

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="AUTHENTICATION_METHODS can't be empty"):
        self.message = message
        super().__init__(self.message)
