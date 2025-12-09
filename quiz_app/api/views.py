"""API views for creating, listing, retrieving, updating, and deleting quizzes."""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .serializers import QuizSerializer
from .permissions import IsQuizOwner

from quiz_app.models import Quiz
from quiz_app.services.quiz_builder import build_quiz_from_youtube


class QuizCreateAPIView(APIView):
    """
    Create a Quiz from a YouTube URL by downloading the video, transcribing it, and generating quiz content.
    Expected behavior:
    - Authentication: Requires an authenticated user (permission_classes = [IsAuthenticated]).
    - Input: Expects a POST body containing 'url' (the frontend field), which is mapped to 'video_url' by the initial serializer.
    - Validation: Validates the provided URL using QuizSerializer (context includes the requesting user; initial validation is partial to accept just the URL).
    - Generation: Calls build_quiz_from_youtube(url) to perform video download, transcription, and automatic quiz generation; the returned dict is augmented with 'video_url'.
    - Persistence: Validates the generated quiz payload with QuizSerializer (with user context) and saves a Quiz instance.
    - Response: On success returns the serialized Quiz and HTTP 201 Created.
    Error handling:
    - Raises/returns HTTP 400 with a validation error detail when serializer/model validation fails (ValidationError).
    - Returns HTTP 500 with a generic error message for unexpected exceptions.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Frontend sends `url`; serializer maps it to `video_url`.
        serializer = QuizSerializer(
            data={"url": request.data.get("url")},
            context={"user": request.user},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data["video_url"]

        try:
            quiz_dict = build_quiz_from_youtube(url)
            quiz_dict["video_url"] = url

            serializer = QuizSerializer(
                data=quiz_dict, context={"user": request.user})
            serializer.is_valid(raise_exception=True)
            quiz = serializer.save()

            return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Internal Server Error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizListAPIView(APIView):
    """List quizzes belonging to the authenticated user.
    Handles GET requests and returns a serialized list of Quiz objects
    owned by the requesting user. The queryset is limited to quizzes
    where Quiz.user == request.user, prefetches related 'questions' to
    minimize additional database queries, and is ordered by newest first
    ('-created_at').
    Authentication and permissions:
    - Requires authentication (IsAuthenticated). Anonymous users will be denied.
    Response:
    - On success returns HTTP 200 with serializer data produced by QuizSerializer(many=True).
        The exact fields and nested question representation are defined by QuizSerializer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        quizzes = Quiz.objects.filter(user=request.user).prefetch_related(
            'questions').order_by('-created_at')
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single Quiz instance while enforcing authentication and ownership.
    This view extends DRF's RetrieveUpdateDestroyAPIView to provide endpoint handlers for:
    - GET: retrieve a single Quiz instance.
    - PATCH: partially update fields on the Quiz (serializer validation is applied).
    - DELETE: remove the Quiz instance.
    Behavior and guarantees:
    - Access is restricted to authenticated users who also pass the IsQuizOwner permission check.
    - The view uses QuizSerializer for input validation and output representation.
    - Partial updates via PATCH use serializer.save() and return a 200 OK with the serialized object on success, or 400 Bad Request with validation errors on failure.
    - Deletions delegate to the generic destroy() implementation and will return the standard DRF response (typically 204 No Content) on success.
    - If the requested object does not exist or the user lacks permission, DRF will raise the appropriate errors (Http404 or PermissionDenied) before the handler code is executed.
    Attributes:
        queryset (QuerySet): Quiz.objects.all()
        serializer_class (Serializer): QuizSerializer
        permission_classes (list): [IsAuthenticated, IsQuizOwner]
    Notes:
    - PUT (full update) is supported by the base class but is not overridden here.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        quiz = self.get_object()

        serializer = self.get_serializer(
            quiz,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
