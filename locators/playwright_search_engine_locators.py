"""
Playwright search engine locators.
Centralized CSS selectors for Playwright-based automation.
Supports multiple search engines with fallback selectors.
"""


class PlaywrightSearchEngineLocators:
    """
    Locators for search engine pages using Playwright CSS selectors.

    Note: These are CSS selectors (strings), not Selenium tuples.
    Playwright uses different selector syntax than Selenium.
    """

    # Search input and interaction elements
    # DuckDuckGo: input#search_form_input
    # Google: input[name="q"], textarea[name="q"]
    SEARCH_INPUT = 'input[name="q"], textarea[name="q"], input#search_form_input'

    SEARCH_BUTTON = 'input[name="btnK"], button[type="submit"], button#search_button'

    # Search suggestions dropdown
    # DuckDuckGo: li[role="option"] (in combobox popover)
    # Google: [role="listbox"] [role="option"]
    SEARCH_SUGGESTIONS = 'li[role="option"]'
    SUGGESTIONS_CONTAINER = "[data-reach-combobox-popover]"

    # Results container - main results area
    # DuckDuckGo: article[data-testid], [data-area='mainline']
    # Google: #search, #rso
    RESULTS_CONTAINER = (
        "#search, #rso, #links, .results, article[data-testid], [data-area='mainline']"
    )

    # Individual result links
    # DuckDuckGo: article h2 a, [data-testid='result-title-a']
    # Google: #search a h3, #rso a h3
    RESULT_LINKS = (
        "#search a h3, #rso a h3, article h2 a, "
        ".result__a, [data-testid='result-title-a']"
    )

    # Result titles (headings)
    # DuckDuckGo: article h2, h2[data-testid='result-title']
    # Google: #search h3, #rso h3
    RESULT_TITLES = (
        "#search h3, #rso h3, article h2, "
        ".result__title, h2[data-testid='result-title']"
    )

    # Result descriptions/snippets
    # DuckDuckGo: article [data-result='snippet']
    # Google: .VwiC3b, .s3v9rd
    RESULT_DESCRIPTIONS = (
        ".VwiC3b, .s3v9rd, .result__snippet, article [data-result='snippet']"
    )

    # CAPTCHA detection (generic selectors)
    CAPTCHA_CONTAINER = "#captcha-form, .captcha"

    # No results message
    NO_RESULTS = (
        'p:has-text("did not match any documents"), .no-results, .no-results-message'
    )

    # Fallback selectors for search completion detection
    FALLBACK_CONTENT = ".react-results--main, body"

    # XPath for getting parent link element
    ANCESTOR_LINK_XPATH = "xpath=ancestor::a"
