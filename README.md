# Python Selenium 4 Project

## Introduction

Welcome to the Python Selenium 4  Project! This project aims to provide a robust framework for web automation, visual regression testing, and database management using Python.

### Technologies Used

- **Selenium 4 (v4.16.0):** Selenium is a powerful tool for automating web browsers. With Selenium 4, we can efficiently interact with web elements, perform actions like clicking buttons and filling forms, and navigate through web pages. It provides enhanced features and better performance compared to previous versions.

- **Pixelmatch (v0.3.0):** Pixelmatch is a pixel-level image comparison library. In this project, we leverage Pixelmatch for visual regression testing. By capturing screenshots of web pages and comparing them pixel by pixel, we can detect any visual changes between different versions of our web application.

- **Pillow (v10.2.0):** Pillow is a Python Imaging Library (PIL) fork. We use Pillow for image processing tasks such as resizing, cropping, and saving screenshots captured during testing.

- **PyHamcrest:** PyHamcrest is a library of matcher objects for test assertions. We use PyHamcrest to create expressive and readable assertions in our test cases.

- **WebDriver Manager (v4.0.1):** WebDriver Manager simplifies the management of web driver binaries. It automatically downloads and caches the latest web driver binaries for Selenium, eliminating the need for manual management.

- **Requests (v2.31.0):** Requests is a Python HTTP library. We utilize Requests for making HTTP requests to external services or APIs, such as fetching web pages or interacting with web services.

### Project Goals

1. **Web Automation:** Implement robust automation scripts using Selenium 4 to interact with web elements, simulate user actions, and perform end-to-end testing of web applications.

2. **Visual Regression Testing:** Integrate Pixelmatch for visual diffing to detect and report visual changes between different versions of web pages. Visual regression testing helps ensure that new changes do not introduce unintended visual discrepancies.

3. **Database Management:** Utilize SQLite to store and retrieve test data, including test results, screenshots, and metadata. The database enables efficient storage, retrieval, and analysis of test information, facilitating effective test reporting, debugging, and querying for specific test scenarios.

## Project Structure

```
PythonSeleniumProject/
|-- drivers/
|-- locators/
|   |-- google_result_locators.py
|   |-- google_search_locators.py
|-- pages/
|   |-- base_page.py
|   |-- google_result_page.py
|   |-- google_search_page.py
|-- tests/
|   |-- test_api.py
|   |-- test_google_search.py
|   |-- test_image_diff.py
|-- utils/
|   |-- diff_handler.py
|   |-- sql_connection.py
|   |-- webdriver_factory.py
|-- .gitignore
|-- conftest.py
|-- README.md
|-- requirements.txt
```





## Getting Started

To get started with the Python Selenium 4 Project, follow these steps:

1. **Clone the Repository:** Clone the project repository from [GitHub](https://github.com/dsolisp/PythonSeleniumProject) to your local machine.

2. **Install Python:** If you don't have Python installed, download and install the latest version of Python from the [official website](https://www.python.org/downloads/).

3. **Set Up a Virtual Environment:** Create a new virtual environment for the project using the following commands:
 
  For macOS and Linux:   

   ```bash
   # Create a new virtual environment
   python -m venv venv

   # Activate the virtual environment
   source venv/bin/activate
   ```

   For Windows:

   ```bash
   # Create a new virtual environment
   python -m venv venv

   # Activate the virtual environment
   venv\Scripts\activate
   ```

4. **Install Dependencies:** Install the necessary Python dependencies by running `pip install -r requirements.txt`. Make sure to use the specified package versions:

   ```bash
   pip install selenium==4.16.0 pytest~=7.4.4 pixelmatch~=0.3.0 pillow~=10.2.0 PyHamcrest webdriver-manager~=4.0.1 requests~=2.31.0


5. **Download Web Drivers:** WebDriver Manager will automatically download the latest web driver binaries for Selenium. You can also manually download the web drivers and place them in the `drivers` directory.

6. **Run the Tests:** Execute the test suite by running `pytest` in the project root directory. The tests will run, and the results will be displayed in the terminal.

## Next Milestones

The Python Selenium 4 Project aims to achieve the following milestones in the future:

1. **Extend Test Coverage:** Expand the test suite to cover additional web applications, including complex user interactions, form submissions, and dynamic web elements.
2. **Integrate CI/CD:** Implement continuous integration and continuous deployment (CI/CD) pipelines to automate the testing and deployment process.
3. **Enhance Visual Regression Testing:** Improve the visual regression testing framework to handle responsive web design, dynamic content, and cross-browser testing.
4. **Implement Test Reporting:** Integrate test reporting tools (Allure report) to generate detailed test reports, including test results, screenshots, and metadata.
5. **Connect to Test Case Management Tools:** Integrate with test case management tools (TestLink, TestRails) to synchronize test cases, test results, and test execution status.