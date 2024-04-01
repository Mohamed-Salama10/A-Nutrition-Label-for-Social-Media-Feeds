from transformers import pipeline
from src.ClassificationModel.Scripts.labels import mood_list
def get_emotion_classification(url):
    """This function uses an emotion image detection model to get the ratio of different emotions in the image.

    Args:
        url (str): The URL of the image or the path to an image.
        mood_list (list): List of emotions to get classification values for.

    Returns:
        dict: A dictionary containing classification values for specified emotions.
    """

    # Load the image classification pipeline
    pipe = pipeline("image-classification", model="dima806/facial_emotions_image_detection")

    # Get classification results for the image
    results = pipe(url)

    # Create a dictionary to store classification values for specified emotions
    classification_dict = {}

    # Iterate over the specified emotions in mood_list
    for mood in mood_list:
        # Find the corresponding result in the results list
        for result in results:
            if mood.lower() in result['label'].lower():
                # Add the classification values to the dictionary
                classification_dict[mood] = result['score']
                break  # Break the loop once a match is found

    return result