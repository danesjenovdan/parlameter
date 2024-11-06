from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _

from parlanotifications.models import Keyword, NotificationUser
from parlanotifications.serializers import KeywordSerializer
from parladata.update_utils import send_email


class KeywordView(viewsets.ModelViewSet):
    permission_classes = []
    queryset = Keyword.objects.all().order_by("id")
    serializer_class = KeywordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            keyword = serializer.save()
            if not keyword.accepted_at:
                send_email(
                    _("Parlameter obvestila - potrditev"),
                    keyword.user.email,
                    "add_keyword.html",
                    {
                        "keyword": keyword.keyword,
                        "uuid": keyword.user.uuid,
                        "kid": keyword.id,
                    },
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        uuid = request.GET.get("uuid")
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user__uuid=uuid)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        uuid = request.GET.get("uuid")
        if str(instance.user.uuid) == uuid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["get"])
    def confirm(self, request, pk):
        uuid = request.GET.get("uuid")
        print(uuid)
        instance = get_object_or_404(Keyword, pk=pk)
        print(instance.user.uuid)
        if str(instance.user.uuid) == uuid:
            instance.accepted_at = timezone.now()
            instance.save()
            return Response({
                "keyword": instance.keyword,
                "email": instance.user.email,
            }, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
