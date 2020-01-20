from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class DefaultPagination(PageNumberPagination):
    """
    Clase Paginator específica para fijar la paginación en una query.
    El funcionamiento será mediante el paso de parámetros se fijará el número
    máximo de elementos con los que paginaremos.
    Con esta estrategia podremos solicitar en la propia query el número máximo
    de elementos por página.

    Para usar esta paginación es necesario especificar las settigs de
    paginación en el archivo de settings del proyecto:

    ```
    # Settings para la paginación del proyecto
    PAGINATION_SETTINGS = {'DEFAULT_LIMIT': 50, 'MAX_LIMIT_DEFAULT': 20000}
    ```
    """

    page_size = settings.PAGINATION_SETTINGS["DEFAULT_LIMIT"]
    page_size_query_param = "page_size"
    max_page_size = settings.PAGINATION_SETTINGS["MAX_LIMIT_DEFAULT"]
