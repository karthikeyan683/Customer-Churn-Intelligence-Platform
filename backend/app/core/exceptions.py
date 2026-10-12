class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


class CustomerNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            code="CUSTOMER_NOT_FOUND",
            message="Customer not found"
        )


class PredictionNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            code="PREDICTION_NOT_FOUND",
            message="No prediction found for this customer"
        )


class UnauthorizedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            code="UNAUTHORIZED",
            message="Authentication required"
        )


class ForbiddenException(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            code="FORBIDDEN",
            message="You do not have permission to perform this action"
        )
