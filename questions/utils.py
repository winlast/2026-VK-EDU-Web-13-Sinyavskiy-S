from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # ?page=abc, ?page=1.5 и т.п. -> первая страница
        page = paginator.page(1)
    except EmptyPage:
        # номер меньше 1 -> первая страница, больше последней -> последняя
        if int(page_number) < 1:
            page = paginator.page(1)
        else:
            page = paginator.page(paginator.num_pages)

    # номера страниц для шаблона пагинатора: 1 … 4 5 [6] 7 8 … 20
    page.elided_page_range = paginator.get_elided_page_range(
        page.number, on_each_side=2, on_ends=1,
    )
    return page
