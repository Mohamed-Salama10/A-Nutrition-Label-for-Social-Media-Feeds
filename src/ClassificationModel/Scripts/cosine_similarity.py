from PIL import Image
import requests
from transformers import CLIPProcessor, CLIPModel
import torch.nn.functional as nn
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.ClassificationModel.Scripts.labels import labels_list, mood_list, purpose_list

# Initialize CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
# processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")


def load_image(input_path):
    # Check if the input path is a URL
    if input_path.startswith("http://") or input_path.startswith("https://"):
        # Open the image from a URL
        response = requests.get(input_path, stream=True)
        image = Image.open(response.raw)
    else:
        # Open the image from a local file path
        image = Image.open(input_path)
    return image


def get_image_embedding(image, model=model, processor=processor):

    # Load an image from the web

    image = load_image(input_path=image)

    # Process the image for the model
    inputs = processor(images=image, return_tensors="pt")

    # Generate the image embedding
    image_embedding = model.get_image_features(**inputs)

    # The image embedding is now stored in `outputs`
    return image_embedding


def get_text_embedding(text, model=model, processor=processor):

    # Process the text for the mode
    inputs = processor(text=text, return_tensors="pt", padding=True, truncation=True)

    # Generate the text embedding
    text_embedding = model.get_text_features(**inputs)

    # The text embedding is now stored in `outputs`
    return text_embedding


def get_cosine_similarity(image_link):
    all_lists = labels_list + mood_list + purpose_list
    link = image_link
    result_dict = {}
    for label in all_lists:

        word = label
        result = nn.cosine_similarity(
            get_text_embedding(text=word), get_image_embedding(image=link)
        ).item()
        if result >= 0.23:
            result_dict[label] = result

    return result_dict
