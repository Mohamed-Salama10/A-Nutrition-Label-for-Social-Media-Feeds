import requests
from requests.exceptions import ConnectionError
from src.ClassificationModel.Scripts.cosine_similarity import get_cosine_similarity
from src.ClassificationModel.Scripts.clipmodel import classify_single_image
from src.ClassificationModel.Scripts.labels import mood_list, labels_list, purpose_list

from bson import ObjectId
from PIL import Image
import io
import requests
from io import BytesIO
import os
import time


classification_url = "http://127.0.0.1:8000/nutri/getSinglePendingPost"
update_results_url = "http://127.0.0.1:8000/nutri/updateClassifiedPost"
update_broken_url = "http://127.0.0.1:8000/nutri/updateBrokenUrl"
bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoidGVzdCIsImlkIjoiNjViOGViZTI4ZDUyN2JjNjY2YzE3NTM2In0._-LatDYtRdGwxpYH-0V3dFNrKOEnoUt3hgdwywU8ZCo"
headers = {"Authorization": f"Bearer {bearer_token}"}


def is_image_valid(input_path_or_url):
    """
    Check if an image from a URL or a file path is valid using the Pillow library.

    Args:
        input_path_or_url (str): The URL or the file path to the image.

    Returns:
        bool: True if the image is valid, False otherwise.
    """
    try:

        if input_path_or_url.startswith(("http://", "https://")):
            # Handle URL
            response = requests.get(input_path_or_url)
            response.raise_for_status()  # Ensure we got a successful response
            image_data = BytesIO(response.content)
        else:
            # Handle file path
            image_data = input_path_or_url  # Directly use the file path for opening

        # Open and verify the image
        if isinstance(image_data, BytesIO):
            with Image.open(image_data) as image:
                image.verify()  # Verify the image integrity
                # Optionally, reload the image to ensure it's fully readable
                image = Image.open(BytesIO(response.content))
                image.load()
        else:
            with Image.open(image_data) as image:
                image.verify()
                # Re-open the image file to fully load it, ensuring it's readable
                image = Image.open(image_data)
                image.load()

        return True
    except Exception as e:

        return False


def process_single_unclassified_posts():
     """
    Process a single unclassified post retrieved from a specified classification URL.

    The function fetches an unclassified post from a web service, validates its image URL,
    and if valid, performs classification based on labels, mood, and purpose. 
    It then computes the cosine similarity of the image and updates the classification results back to the database.

    The process involves:
    - Retrieving an unclassified post using a GET request.
    - Checking if the post contains an image URL and verifying its validity.
    - Classifying the image using predefined lists for labels, mood, and purpose.
    - Computing cosine similarity for the image.
    - Updating the classification results in the database using a PUT request.

    Exceptions:
    - Handles exceptions related to network requests and classification processes, logging any errors encountered during the operations.

    Notes:
    - The function assumes the presence of global variables such as `headers`, `classification_url`, `update_broken_url`, `labels_list`, `mood_list`, `purpose_list`, and `update_results_url` which are used in the requests.
    - If the image URL is invalid, it sends an update using a PUT request to mark the URL as broken.

    Outputs:
    - The function prints the status of each major step to the console, including errors.
    """
    try:

        unclassified_post = requests.get(classification_url, headers=headers)
        unclassified_post = unclassified_post.json()
        if not unclassified_post:
            print("No Posts to classify")
            pass
        else:
            print("There is a post being classified..............")

            image_url = unclassified_post["post_url"]
            
            if image_url is None:
                print("There is no image")
                return
            elif is_image_valid(input_path_or_url=image_url) is False:
                query_params = {"post_url": unclassified_post["post_url"]}
                requests.put(update_broken_url, params=query_params)
                print("Image url is invalid")
                return
            else:
                try:
                    # Perform image classification for labels, mood, and purpose
                    labels_classification = classify_single_image(
                        image_path=image_url, labels_list=labels_list
                    )
                    mood_classification = classify_single_image(
                        image_path=image_url, labels_list=mood_list
                    )
                    purpose_classification = classify_single_image(
                        image_path=image_url, labels_list=purpose_list
                    )

                    print("Classification via clip is done..............")

                    cosine_similarity_results = get_cosine_similarity(
                        image_link=image_url
                    )
                    print("Classification via cosine similarity is done..............")

                    # Update the database with classification results
                    print("updating database..............")
                    post_classification_results = {
                        "post_id": unclassified_post["post_id"],
                        "owner_id": str(unclassified_post["owner_id"]),
                        "labels_classification": labels_classification,
                        "mood_classification": mood_classification,
                        "purpose_classification": purpose_classification,
                        "cosine_similarity_results": cosine_similarity_results,
                        "post_url":unclassified_post["post_url"]
                    }
                    print("classification is done ")
                    
                    update_post = requests.put(
                        update_results_url, json=post_classification_results
                    )
                except Exception as e:
                    print("first error")
                    print(f"An error occurred: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")


# while True:
#     process_single_unclassified_posts()

import threading
def classification_function():
    while True:
        process_single_unclassified_posts()
       


# Create a thread for running the background function
background_thread = threading.Thread(target=classification_function)
background_thread.daemon = (
    True  # Daemonize the thread so it terminates with the main program
)
background_thread.start()
