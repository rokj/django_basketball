def get_from(page_number=1, count=1):
    return int(page_number - 1) * int(count);

def get_pages(total, per_page):
    return (int(total - 1) / per_page) + 1;
