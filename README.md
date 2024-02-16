# Python Selenium 4 Project

## Introduction

Welcome to the Python Selenium 4 Visual Diff Project! This project aims to provide a robust framework for web automation, visual regression testing, and database management using Python.

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


## Getting Started

To get started with the Python Selenium 4 Visual Diff Project, follow these steps:

1. **Clone the Repository:** Clone the project repository from [GitHub](https://github.com/dsolisp/PythonSeleniumProject) to your local machine.

2. **Install Dependencies:** Install the necessary Python dependencies by running `pip install -r requirements.txt`. Make sure to use the specified package versions:

   ```bash
   pip install selenium==4.16.0 pytest~=7.4.4 pixelmatch~=0.3.0 pillow~=10.2.0 PyHamcrest webdriver-manager~=4.0.1 requests~=2.31.0
