import enum
from typing import Optional, Dict, Any

import sentry_sdk
from fastapi import HTTPException, Request, status
from sentry_sdk import isolation_scope


class DetailType(enum.Enum):
    INVALID_APIKEY = 'invalid-apikey'
    INVALID_SIGNATURE = 'invalid-signature'
    INVALID_CREDENTIALS = 'invalid-credentials'
    INVALID_TOKEN = 'invalid-token'


class ProblemDetailException(HTTPException):
    def __init__(
        self,
        request: Request,
        title: str,
        status_code: Optional[int] = status.HTTP_500_INTERNAL_SERVER_ERROR,
        previous: Optional[Exception] = None,
        to_sentry: Optional[bool] = False,
        additional_data: Optional[dict] = None,
        detail_type: DetailType = None,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=title, headers=headers)

        self._request = request
        self._title = title
        self._status_code = status_code
        self._previous = previous
        self._type = detail_type
        self._detail_type = detail_type
        self._detail = detail
        self._headers = headers

        if additional_data:
            self._additional_data = additional_data
        else:
            self._additional_data = {}

        if to_sentry:
            with isolation_scope() as scope:
                for key, value in self.__dict__.items():
                    scope.set_extra(key, value)
                sentry_sdk.capture_exception(self)

    @property
    def detail_type(self) -> str:
        if self._detail_type:
            result = str(self._detail_type.value)
        else:
            result = None

        return result
