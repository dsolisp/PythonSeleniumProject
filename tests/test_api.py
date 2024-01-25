import requests
from hamcrest import assert_that, equal_to

base_url = "https://jsonplaceholder.typicode.com"


def test_create_and_retrieve_post():
    # Create a new post
    post_data = {
        "title": "Python Test Post",
        "body": "This is a test post created by Python",
        "userId": 1
    }
    post_response = requests.post(f"{base_url}/posts", json=post_data)

    # Assertion for the status code of the POST request
    assert_that(post_response.status_code, equal_to(201))

    # Retrieve the post using the response from the created post
    post_id = post_response.json()["id"]
    get_response = requests.get(f"{base_url}/posts/{1}")

    # Assertions for the status code and content of the GET request
    assert_that(get_response.status_code, equal_to(200))
    assert_that(get_response.json()["title"], equal_to("sunt aut facere repellat provident occaecati excepturi optio reprehenderit"))
    assert_that(get_response.json()["body"], equal_to("quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"))
