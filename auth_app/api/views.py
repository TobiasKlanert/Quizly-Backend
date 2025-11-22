from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        msg = {}
        if serializer.is_valid():
            serializer.save()
            msg = {
                'detail': 'User created successfully!'
            }
            return Response(msg)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
