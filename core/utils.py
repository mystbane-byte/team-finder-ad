from django.core.paginator import Paginator

ITEMS_PER_PAGE = 12


def paginate(queryset, request, per_page=ITEMS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
