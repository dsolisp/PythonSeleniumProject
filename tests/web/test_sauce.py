from hamcrest import assert_that, equal_to, is_

from pages.sauce import SaucePage


def test_standard_user_adding_items_to_cart(driver):
    """Test that standard user can login and add items to cart."""
    sauce_page = SaucePage(driver[0])  # driver fixture returns (driver, db)
    sauce_page.open()
    sauce_page.fill_login_input()

    # Verify login was successful
    assert_that(sauce_page.is_logged_in(), is_(True))

    # Add products to cart
    sauce_page.add_default_products_to_cart()

    # Verify cart badge shows correct count
    cart_element = sauce_page.get_cart_element()
    assert_that(cart_element.text, equal_to("3"))
