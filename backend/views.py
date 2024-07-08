from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.generics import get_object_or_404

from .serializers import GiveawaySerializer, GiveawaySerializerPublic, PlatformSerializer, SupplierSerializer, SupplierSerializerPublic
from .models import Giveaway, Platform, Supplier


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })


class GiveawayListView(APIView):
    """
    View class for listing all and creating a new giveaway, endpoint: /giveaways/
    """

    def get(self, request, format=None) -> Response:
        """ For listing out the giveaways, HTTP method: GET """
        max_limit = 2000 if request.user.is_authenticated else 25
        params = {
            'id': request.query_params.get('id', None),
            'status': request.query_params.getlist('status', None),
            'supplier': request.query_params.getlist('supplier', None),
            'order_by': request.query_params.get('order_by', 'created_at'),
            'offset': request.query_params.get('offset', 0),
            'limit': request.query_params.get('limit', max_limit),
        }
        OFFSET = int(params['offset'])
        LIMIT = int(params['limit']) if int(
            params['limit']) <= max_limit else max_limit
        status_intersection = list(
            set(params['status']) & set(Giveaway.Status.values)) if params['status'] else None
        STATUS = status_intersection if status_intersection else None

        giveaways = Giveaway.objects
        filters = False
        if STATUS:
            filters = True
            giveaways = giveaways.filter(status__in=STATUS)
        if params['id']:
            filters = True
            giveaways = giveaways.filter(id=params['id'])
        if params['supplier']:
            filters = True
            giveaways = giveaways.filter(supplier__in=params['supplier'])
        if not filters:
            giveaways = giveaways.all()
        if params['order_by']:
            giveaways = giveaways.order_by(params['order_by'])
        giveaways = giveaways[OFFSET:OFFSET+LIMIT]
        # Passing the queryset through the serializer
        if request.user.is_authenticated:
            serializer = GiveawaySerializer(giveaways, many=True)
        else:
            serializer = GiveawaySerializerPublic(giveaways, many=True)

        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, format=None) -> Response:
        """ For creating a new giveaway, HTTP method: POST """
        serializer = GiveawaySerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            print(f"serializer.errors: {serializer.errors}")
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class GiveawayDetailView(APIView):
    """
    View class for listing, updating and deleting a single giveaway, endpoint: /giveaways/<int:pk>/
    """

    def get(self, request, pk=None, format=None) -> Response:
        """ For listing out a single giveaway, HTTP method: GET """
        giveaway = get_object_or_404(Giveaway.objects.all(), pk=pk)
        if request.user.is_authenticated:
            serializer = GiveawaySerializer(giveaway)
        else:
            serializer = GiveawaySerializerPublic(giveaway)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def put(self, request, pk=None, format=None):
        """ For updating an existing giveaway, HTTP method: PUT """
        giveaway = get_object_or_404(Giveaway.objects.all(), pk=pk)
        serializer = GiveawaySerializer(giveaway, data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data)
        else:
            print(f"serializer.errors: {serializer.errors}")
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, format=None) -> Response:
        """ For deleting a giveaway, HTTP method: DELETE """
        giveaway = get_object_or_404(Giveaway.objects.all(), pk=pk)
        giveaway.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlatformListView(APIView):
    """
    View class for listing all platforms, endpoint: /platforms/
    """

    def get(self, request, format=None) -> Response:
        """ For listing out the platforms, HTTP method: GET """
        params = {
            'id': request.query_params.getlist('id', None)
        }
        platforms = Platform.objects
        filters = False
        if params['id']:
            filters = True
            platforms = platforms.filter(id__in=params['id'])
        if not filters:
            platforms = platforms.all()
        # Passing the queryset through the serializer
        serializer = PlatformSerializer(platforms, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class SupplierListView(APIView):
    """
    View class for listing all suppliers, endpoint: /suppliers/
    """

    def get(self, request, format=None) -> Response:
        """ For listing out the platforms, HTTP method: GET """
        params = {
            'enabled': request.query_params.get('enabled', None),
            'id': request.query_params.getlist('id', None)
        }
        suppliers = Supplier.objects
        filters = False
        if params['enabled']:
            filters = True
            suppliers = suppliers.filter(enabled=params['enabled'])
        if params['id']:
            filters = True
            suppliers = suppliers.filter(id__in=params['id'])
        if not filters:
            suppliers = suppliers.all()
        suppliers = suppliers.order_by("order")
        # Passing the queryset through the serializer
        if request.user.is_authenticated:
            serializer = SupplierSerializer(suppliers, many=True)
        else:
            serializer = SupplierSerializerPublic(suppliers, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class SupplierDetailView(APIView):
    """
    View class for listing, updating and deleting a single supplier, endpoint: /suppliers/<int:pk>/
    """

    def get(self, request, pk=None, format=None) -> Response:
        """ For listing out a single supplier, HTTP method: GET """
        supplier = get_object_or_404(Supplier.objects.all(), pk=pk)
        if request.user.is_authenticated:
            serializer = SupplierSerializer(supplier)
        else:
            serializer = SupplierSerializerPublic(supplier)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def put(self, request, pk=None, format=None):
        """ For updating an existing supplier, HTTP method: PUT """
        supplier = get_object_or_404(Supplier.objects.all(), pk=pk)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data)
        else:
            print(f"serializer.errors: {serializer.errors}")
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
