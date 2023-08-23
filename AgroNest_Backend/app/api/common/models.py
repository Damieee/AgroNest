from typing import (
    Any,
    List,
    Optional,
)

from sqlmodel import Field, SQLModel

class ResponseModel(SQLModel):
    """Creates a response model for the app.api.

    Provides a structure for providing a response to the .
    Provides a static method for success responses

    Attributes:
        status: The status of the response.
        message: The message of the response.
        data: The data of the response.
    """

    status: bool
    message: str
    data: Any

    @staticmethod
    def success(data: Any, message: str = "success") -> dict[str, Any]:
        """Provides a success response data

        Args:
            data (dict): data to be returned
            message (str, optional): Descriptive messaged. Defaults to "success".

        Returns:
            dict: key-value pair of status, message and data
        """
        return ResponseModel(status=True, message=message, data=data).dict()

    @staticmethod
    def error(message: str, data: Any | None = None) -> dict[str, Any]:
        """Provides an error response data

        Args:
            data (dict): data to be returned
            detail (str): Descriptive error message.

        Returns:
            dict: key-value pair of status, detail
        """

        return ResponseModel(status=False, message=message, data=data).dict()

    @staticmethod
    def example(
        description: str = 'Success',
        status: bool = True,
        message: str = '',
        data: dict[str, Any] = {},
    ) -> dict[str, Any]:
        """Provides an error response data

        Args:
            data (dict): data to be returned
            detail (str): Descriptive  message.

        Returns:
            dict: key-value pair of status, detail
        """
        if message == '':
            message = description
        return {
            "description": description,
            'content': {
                'application/json': {
                    'example': {
                        'success': status,
                        'message': message,
                        'data': data
                    }
                }
            }
        }


class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    image: str
    description: str
    location: str
    # tags: List[str]
