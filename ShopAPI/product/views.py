from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters

from .filters import ProductItemFilter
from .serializers import *
from .models import *

# Create your views here.

# All Products by Category
class ProductByCategory(APIView):
    def get(self, request, category_slug):
        category = Category.objects.get(slug=category_slug)

        breadcrumbs = CategorySerializer(category).data

        products = Product.objects.select_related('category_id')\
                    .filter(category_id__slug=category_slug)
        products_data = ProductSerializer(products, many=True).data

        header = HeaderFooterSerializer(Product.objects.all()).data

        return Response({
            'breadcrumbs': breadcrumbs,
            'children': products_data,
            'header&footer': header
        })

# iphone/iphone-13/
class ItemsByProducts(generics.ListAPIView):
    serializer_class = ShortProductItemSerializer
    queryset = Product.objects.all()
    lookup_field = 'slug'
    lookup_url_kwarg = 'product_slug'

    def list(self, request, *args, **kwargs):
        product: Product = self.get_object()
        queryset = product.items.all()
        serializer = self.get_serializer(queryset, many=True)

        category_breadcrumb = CategorySerializer(product.category_id).data
        product_breadcrumb = ProductSerializer(product).data
        breadcrumbs = [category_breadcrumb,
                       product_breadcrumb]

        header = HeaderFooterSerializer(Product.objects.all()).data

        return Response({'breadcrumbs': breadcrumbs,
                        'products': serializer.data,
                        'header&footer': header
        })

# all products are given, people can search and filter
class SearchAndFilterProductItems(generics.ListAPIView):
    serializer_class = ProductItemSerializer
    filterset_class = ProductItemFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'color']

    def get_queryset(self):
        return ProductItem.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        categories = Category.objects.all()
        primary_filter = CategorySerializer(categories, many=True).data

        header = HeaderFooterSerializer(Product.objects.all()).data

        pfilter = self.request.query_params.get('pfilter', None)
        if pfilter is not None:
            filter = AttributeType.objects.prefetch_related('options', 'options__category_id').\
                    filter(options__category_id__slug=pfilter).distinct()

            filter_data = FilterSerializer(filter, many=True, context={'category': pfilter}).data

            return Response({
                'filter': filter_data,
                'products': serializer.data,
                'header&footer': header
            })

        return Response({
            'primary_filter': primary_filter,
            'products': serializer.data,
            'header&footer': header
        })

# Retrieve a Product Item Cart Separately with an ability to switch colors and memory
# iphone/iphone-13/iphone-13-black-128GB
class RetrieveProductItem(generics.RetrieveAPIView):
    serializer_class = FullProductItemSerializer

    def get_object(self):
        return ProductItem.objects.get(slug=self.kwargs['item_slug'])

    def retrieve(self, request, *args, **kwargs):
        query_set = self.get_object()
        product = self.get_serializer(query_set).data

        parent = self.kwargs['product_slug']
        familyset = Product.objects.get(slug=parent).items.all()
        family = ShortProductItemSerializer(family, many=True).data

        category_slug = self.kwargs['category_slug']
        category_name = query_set.product_id.name
        product_name = query_set.product_id.category_id.name
        product_slug = self.kwargs['product_slug']
        slug = query_set.slug
        name = query_set.name
        breadcrumbs = [
            {
                "name": category_name,
                "slug": category_slug
            },
            {
                "name": product_name,
                "slug": product_slug
            },
            {
                "name": name,
                "slug": slug
            }
        ]

        header = HeaderFooterSerializer(Product.objects.all()).data

        return Response({
            'breadcrumbs': breadcrumbs,
            'product': product,
            'family': family,
            'header&footer': header
        })