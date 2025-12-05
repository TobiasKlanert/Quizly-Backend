from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .serializers import UrlInputSerializer, QuizSerializer
from .permissions import IsQuizOwner
from quiz_app.models import Quiz
from quiz_app.services.quiz_builder import build_quiz_from_youtube


class QuizCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        input_serializer = UrlInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        url = input_serializer.validated_data["url"]

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
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        quizzes = Quiz.objects.filter(user=request.user).prefetch_related(
            'questions').order_by('-created_at')
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
