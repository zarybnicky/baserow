from django.db import transaction

from rest_framework.parsers import MultiPartParser

from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from baserow.api.decorators import map_exceptions, validate_body
from baserow.api.schemas import get_error_schema
from baserow.core.user_files.exceptions import (
    InvalidFileStreamError, FileSizeTooLargeError, FileURLCouldNotBeReached
)
from baserow.core.user_files.handler import UserFileHandler

from .serializers import UserFileSerializer, UserFileUploadViaURLRequestSerializer
from .errors import (
    ERROR_INVALID_FILE, ERROR_FILE_SIZE_TOO_LARGE, ERROR_FILE_URL_COULD_NOT_BE_REACHED
)


class UploadFileView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    @extend_schema(
        tags=['User files'],
        operation_id='upload_file',
        description=(
            'Uploads a file to Baserow by uploading the file contents directly. A '
            '`file` multipart is expected containing the file contents.'
        ),
        request=None,
        responses={
            200: UserFileSerializer,
            400: get_error_schema(['ERROR_INVALID_FILE', 'ERROR_FILE_SIZE_TOO_LARGE'])
        }
    )
    @transaction.atomic
    @map_exceptions({
        InvalidFileStreamError: ERROR_INVALID_FILE,
        FileSizeTooLargeError: ERROR_FILE_SIZE_TOO_LARGE
    })
    def post(self, request):
        """Uploads a file by uploading the contents directly."""

        if 'file' not in request.FILES:
            raise InvalidFileStreamError('No file was provided.')

        file = request.FILES.get('file')
        user_file = UserFileHandler().upload_user_file(request.user, file.name, file)
        serializer = UserFileSerializer(user_file)
        return Response(serializer.data)


class UploadViaURLView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=['User files'],
        operation_id='upload_via_url',
        description=(
            'Uploads a file to Baserow by downloading it from the provided URL.'
        ),
        request=UserFileUploadViaURLRequestSerializer,
        responses={
            200: UserFileSerializer,
            400: get_error_schema([
                'ERROR_INVALID_FILE',
                'ERROR_FILE_SIZE_TOO_LARGE',
                'ERROR_FILE_URL_COULD_NOT_BE_REACHED'
            ])
        }
    )
    @transaction.atomic
    @map_exceptions({
        InvalidFileStreamError: ERROR_INVALID_FILE,
        FileSizeTooLargeError: ERROR_FILE_SIZE_TOO_LARGE,
        FileURLCouldNotBeReached: ERROR_FILE_URL_COULD_NOT_BE_REACHED
    })
    @validate_body(UserFileUploadViaURLRequestSerializer)
    def post(self, request, data):
        """Uploads a user file by downloading it from the provided URL."""

        url = data['url']
        user_file = UserFileHandler().upload_user_file_by_url(request.user, url)
        serializer = UserFileSerializer(user_file)
        return Response(serializer.data)
