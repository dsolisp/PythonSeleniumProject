"""Locators for the SauceDemo Checkout pages (step-one & step-two)."""

from selenium.webdriver.common.by import By


class CheckoutLocators:
    """Locators mirroring CheckoutPage 1:1 (Law 1)."""

    # Step one — info form
    FIRST_NAME_INPUT = (By.XPATH, '//input[@data-test="firstName"]')
    LAST_NAME_INPUT = (By.XPATH, '//input[@data-test="lastName"]')
    POSTAL_CODE_INPUT = (By.XPATH, '//input[@data-test="postalCode"]')
    CONTINUE_BUTTON = (By.XPATH, '//input[@data-test="continue"]')

    # Step two — order summary
    SUMMARY_TOTAL = (By.XPATH, '//div[@class="summary_total_label"]')
    FINISH_BUTTON = (By.XPATH, '//button[@data-test="finish"]')

    # Confirmation
    CHECKOUT_COMPLETE_HEADER = (By.XPATH, '//h2[@class="complete-header"]')
    BACK_HOME_BUTTON = (By.XPATH, '//button[@data-test="back-to-products"]')
