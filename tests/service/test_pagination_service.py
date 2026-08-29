import pytest
from assertpy import assert_that

from vox.service.pagination_service import PaginationService


@pytest.fixture
def pagination_service():
    return PaginationService()


def test_paginate_content_splits_items_into_pages_of_the_requested_size(
    pagination_service,
):
    # Arrange
    content = [{"title": f"Post {index}"} for index in range(5)]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=2,
        max_pages=0,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that(pages).is_length(3)
    assert_that(pages[0]["items"]).is_length(2)
    assert_that(pages[1]["items"]).is_length(2)
    assert_that(pages[2]["items"]).is_length(1)


def test_paginate_content_sorts_items_by_the_requested_field(pagination_service):
    # Arrange
    content = [{"title": "B"}, {"title": "C"}, {"title": "A"}]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=10,
        max_pages=0,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that([item["title"] for item in pages[0]["items"]]).is_equal_to(
        ["A", "B", "C"]
    )


def test_paginate_content_sorts_items_in_reverse_when_requested(pagination_service):
    # Arrange
    content = [{"title": "B"}, {"title": "C"}, {"title": "A"}]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=10,
        max_pages=0,
        sort_by="title",
        reverse=True,
        template_name="index",
    )

    # Assert
    assert_that([item["title"] for item in pages[0]["items"]]).is_equal_to(
        ["C", "B", "A"]
    )


def test_paginate_content_truncates_to_the_requested_max_pages(pagination_service):
    # Arrange
    content = [{"title": f"Post {index}"} for index in range(5)]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=1,
        max_pages=2,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that(pages).is_length(2)


def test_paginate_content_keeps_all_pages_when_max_pages_is_zero(pagination_service):
    # Arrange
    content = [{"title": f"Post {index}"} for index in range(5)]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=1,
        max_pages=0,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that(pages).is_length(5)


def test_paginate_content_names_the_first_page_after_the_template(pagination_service):
    # Arrange
    content = [{"title": f"Post {index}"} for index in range(3)]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=1,
        max_pages=0,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that(pages[0]["pagination"]["current_page"]).is_equal_to("index.html")
    assert_that(pages[1]["pagination"]["current_page"]).is_equal_to("index_page1.html")
    assert_that(pages[2]["pagination"]["current_page"]).is_equal_to("index_page2.html")


def test_paginate_content_links_previous_and_next_pages_to_their_actual_file_names(
    pagination_service,
):
    # Arrange
    content = [{"title": f"Post {index}"} for index in range(3)]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=1,
        max_pages=0,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that(pages[0]["pagination"]["previous_page"]).is_none()
    assert_that(pages[0]["pagination"]["next_page"]).is_equal_to("index_page1.html")

    assert_that(pages[1]["pagination"]["previous_page"]).is_equal_to("index.html")
    assert_that(pages[1]["pagination"]["next_page"]).is_equal_to("index_page2.html")

    assert_that(pages[2]["pagination"]["previous_page"]).is_equal_to("index_page1.html")
    assert_that(pages[2]["pagination"]["next_page"]).is_none()


def test_paginate_content_includes_the_page_size_and_item_totals(pagination_service):
    # Arrange
    content = [{"title": f"Post {index}"} for index in range(3)]

    # Act
    pages = pagination_service.paginate_content(
        content=content,
        page_size=2,
        max_pages=0,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that(pages[0]["pagination"]["total_pages"]).is_equal_to(2)
    assert_that(pages[0]["pagination"]["items_per_page"]).is_equal_to(2)
    assert_that(pages[0]["pagination"]["total_items"]).is_equal_to(2)
    assert_that(pages[1]["pagination"]["total_items"]).is_equal_to(1)


def test_paginate_content_returns_an_empty_list_for_no_content(pagination_service):
    # Act
    pages = pagination_service.paginate_content(
        content=[],
        page_size=10,
        max_pages=0,
        sort_by="title",
        reverse=False,
        template_name="index",
    )

    # Assert
    assert_that(pages).is_empty()
