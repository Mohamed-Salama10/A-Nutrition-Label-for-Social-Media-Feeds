from turtle import pos
from typing_extensions import Annotated
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Body
from src.FastAPI.database.models import nutritionModel
from jose import JWTError, jwt
from src.FastAPI.database.database import Nutrition_collection, user_collection
from pymongo import ReturnDocument
from bson import ObjectId
from src.FastAPI.App.classificationProcess import process_single_unclassified_posts
import os
from tkinter import Tk, Label, PhotoImage, Toplevel
from PIL import Image, ImageTk
from src.FastAPI.database.schemas import (
    list_nutrition_serial,
    individual_nutrition_serial,
)
from pydantic import BaseModel
from src.ClassificationModel.Scripts.labels import mood_list, labels_list, purpose_list
from fastapi_utils.tasks import repeat_every
import time
from src.ClassificationModel.Scripts.clipmodel import classify_single_image
from src.ClassificationModel.Scripts.emotionAnalysisModel import (
    get_emotion_classification,
)
import threading
import time
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime

############################################################################

nutritionRouter = APIRouter(prefix="/nutri", tags=["Nutrition"])


SECRET_KEY = "login"
ALGORITHM = "HS256"
oauth_bearer = OAuth2PasswordBearer(tokenUrl="user/login")


def get_current_user(token: str = Depends(oauth_bearer)):
    """
    Get the current user based on the provided JWT token.

    Parameters:
    - token (str): The JWT token obtained from the client.

    Returns:
    dict: The decoded payload from the JWT token, representing the current user.

    Raises:
    HTTPException: If the token cannot be validated or if there is an authentication issue.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


############################################################################


class urlRequest(BaseModel):
    url: str


class updatePostTime(BaseModel):
    url: str
    time: float


pause_event = threading.Event()


@nutritionRouter.post("/createNutrition", status_code=status.HTTP_201_CREATED)
async def create_new_nutrition(
    urlRequest: urlRequest, current_user: dict = Depends(get_current_user)
):
    """
    Create a new nutrition entry.

    Parameters:
    - urlRequest (urlRequest): The data for the new nutrition entry.
    - current_user (dict): The current user obtained from the JWT token.

    Returns:
    str: A message indicating the success of the operation.

    Raises:
    HTTPException: If there is an issue creating the nutrition entry.
    """

    new_nutrition_request = nutritionModel()
    isUrlExist = Nutrition_collection.find_one({"url": urlRequest.url})
    if isUrlExist is not None:
        updated_time = Nutrition_collection.find_one_and_update(
            {"url": urlRequest.url}, {"$inc": {"time_spent_on_post": 1.5}}
        )

        return "Url already exist, time incremented by 1.5s"
    try:
        new_nutrition_post = Nutrition_collection.insert_one(
            new_nutrition_request.dict()
        )
        new_post_id = new_nutrition_post.inserted_id
        current_date = datetime.now()
        current_post = Nutrition_collection.find_one_and_update(
            {"_id": new_post_id},
            {
                "$set": {
                    "owner_id": current_user["id"],
                    "url": urlRequest.url,
                    "post_creation_time": current_date,
                    "status": "pending",
                }
            },
            return_document=ReturnDocument.AFTER,
        )

        return f"nutrition created with ID: {str(new_post_id)}"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


############################################################################
@nutritionRouter.get("/getAllPosts", status_code=status.HTTP_200_OK)
async def get_all_posts():
    """
    Get all nutrition posts.

    Returns:
    List[dict]: A list of dictionaries representing all nutrition posts.

    Raises:
    HTTPException: If there is an issue retrieving the posts.
    """
    try:
        all_posts = list_nutrition_serial(Nutrition_collection.find())
        return all_posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


############################################################################


@nutritionRouter.delete("/clearDb")
async def clearDatabase():
    """
    Clears all records from the Nutrition collection in the database.

    Returns:
        str: A message indicating the success of the operation.
    """
    try:
        Nutrition_collection.delete_many({})
        return "success"
    except Exception as e:
        return f"An error occurred: {str(e)}"


############################################################################


@nutritionRouter.post("/classificationTest")
async def classificationTest(url: str):
    """
    Performs image classification on the given URL.

    Args:
        url (str): The URL of the image to be classified.

    Returns:
        dict: A dictionary containing the classification results.
            - 'labels': List of labels predicted by the model.
            - 'emotions': List of emotions predicted by the model.
    """
    try:
        labels_results = classify_single_image(image_path=url, labels_list=labels_list)
        emotion_results = classify_single_image(image_path=url, labels_list=mood_list)
        return {"labels": labels_results, "emotions": emotion_results}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


#######################################################################
@nutritionRouter.get("/getAllPending")
async def getAllPending():
    """
    Retrieves all pending nutrition records from the database.

    Returns:
        list: A list of dictionaries representing pending nutrition records.
    """
    allPending = Nutrition_collection.find({"status": "pending"})
    return list_nutrition_serial(allPending)


############################################################################


@nutritionRouter.get("/getNutritionFacts")
async def get_nutrition_facts(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the popular labels, moods, and purposes based on the user's classified nutrition posts.

    Parameters:
        current_user (dict): The dictionary containing information about the current user.

    Returns:
        dict: A dictionary containing the popular labels, moods, and purposes.
    """
    try:
        current_user_id = current_user["id"]
        all_classified_posts = Nutrition_collection.find(
            {"status": "done", "owner_id": current_user_id}
        )
        count_of_all_posts = Nutrition_collection.count_documents(
            {"status": "done", "owner_id": current_user_id}
        )

        avg_mood_dict = {mood: 0 for mood in mood_list}
        avg_label_dict = {label: 0 for label in labels_list}
        avg_purpose_dict = {purpose: 0 for purpose in purpose_list}

        for classified_post in all_classified_posts:
            for mood, value in classified_post["Mood"].items():
                avg_mood_dict[mood] += value
            for label, value in classified_post["labels"].items():
                avg_label_dict[label] += value
            for purpose, value in classified_post["Purpose"].items():
                avg_purpose_dict[purpose] += value

        avg_mood_dict = {
            key: value / count_of_all_posts for key, value in avg_mood_dict.items()
        }
        avg_label_dict = {
            key: value / count_of_all_posts for key, value in avg_label_dict.items()
        }
        avg_purpose_dict = {
            key: value / count_of_all_posts for key, value in avg_purpose_dict.items()
        }
        # Sorting the dictionary items by their values in descending order
        highest_mood_values = sorted(
            avg_mood_dict.items(), key=lambda x: x[1], reverse=True
        )[:4]
        highest_label_values = sorted(
            avg_label_dict.items(), key=lambda x: x[1], reverse=True
        )[:4]
        highest_purpose_values = sorted(
            avg_purpose_dict.items(), key=lambda x: x[1], reverse=True
        )[:2]

        highest_label_values_dict = {
            label[0]: label[1] for label in highest_mood_values
        }
        highest_mood_values_dict = {mood[0]: mood[1] for mood in highest_label_values}
        highest_purpose_values_dict = {
            purpose[0]: purpose[1] for purpose in highest_purpose_values
        }

        for i in highest_purpose_values:
            highest_mood_values_dict[i[0]] = i[1]

        for i in highest_purpose_values:
            highest_purpose_values_dict[i[0]] = i[1]
        return {
            "Popular Labels": highest_label_values_dict,
            "Popular Moods": highest_mood_values_dict,
            "Popular purpose": highest_purpose_values_dict,
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": f"{e} occurred while processing the request."}


############################################################################


@nutritionRouter.put("/updatePostTime", status_code=status.HTTP_200_OK)
async def updatePostTime(
    updatePostTime: updatePostTime, current_user: dict = Depends(get_current_user)
):
    """
    Update the time spent on a post for the current user.

    Args:
        updatePostTime (updatePostTime): The data containing the URL and time to update.
        current_user (dict): The current user obtained from the authentication system.

    Returns:
        dict: A message indicating the success of the operation.

    Raises:
        HTTPException: If there's an internal server error during the process.
    """
    try:
        post_url = updatePostTime.url
        post_time = updatePostTime.time
        current_user_id = current_user["id"]
        updated_post = Nutrition_collection.find_one_and_update(
            {"owner_id": current_user_id, "url": post_url},
            {"$set": {"time_spent_on_post": post_time}},
        )

        return {"Message": "success"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


############################################################################


@nutritionRouter.get("/getPendingPostsCount")
async def getPendingPostsCount(current_user: dict = Depends(get_current_user)):
    current_user_id = current_user["id"]
    allPendingPostsCount = Nutrition_collection.count_documents(
        {"status": "pending", "owner_id": current_user_id}
    )
    return allPendingPostsCount


############################################################################


@nutritionRouter.get("/getSinglePendingPost")
async def getSinglePendingPost(current_user: dict = Depends(get_current_user)):
    current_user_id = current_user["id"]

    pending_post = Nutrition_collection.find_one(
        {"status": "pending", "owner_id": current_user_id}
    )

    if pending_post is None:
        return {}
    else:
        pending_post_object = {
            "post_id": str(pending_post["_id"]),
            "post_url": pending_post["url"],
            "owner_id": pending_post["owner_id"],
        }
        print(pending_post_object)
        return pending_post_object


@nutritionRouter.put("/updateClassifiedPost")
async def updateClassifiedPost(post_classification_results: dict):

    post_id = post_classification_results["post_id"]
    owner_id = post_classification_results["owner_id"]
    post_url = post_classification_results["post_url"]
    labels_classification = post_classification_results["labels_classification"]
    mood_classification = post_classification_results["mood_classification"]
    purpose_classification = post_classification_results["purpose_classification"]
    cosine_similarity_results = post_classification_results["cosine_similarity_results"]
    print(post_id)
    response = Nutrition_collection.find_one_and_update(
        {"url": post_url},
        {
            "$set": {
                "labels": labels_classification,
                "Mood": mood_classification,
                "Purpose": purpose_classification,
                "cosine_similarity_classification": cosine_similarity_results,
                "status": "success",
            }
        },
    )
    return "success"


@nutritionRouter.put("/updateBrokenUrl")
async def updateBrokenUrl(post_url: str):
    current_post = Nutrition_collection.find_one_and_update(
        {"url": post_url}, {"$set": {"status": "broken_url"}}
    )
    return "success"
