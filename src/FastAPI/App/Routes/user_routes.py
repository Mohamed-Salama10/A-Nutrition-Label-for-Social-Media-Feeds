from typing import List, Dict
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from src.FastAPI.database.database import user_collection
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from src.FastAPI.database.models import userModel
from src.FastAPI.database.schemas import list_users_serial, individual_user_serial
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing_extensions import Annotated
from passlib.context import CryptContext
from datetime import timedelta
from bson import ObjectId
from pymongo import ReturnDocument
from pydantic import BaseModel

###############################################################################
userRouter = APIRouter(prefix="/user", tags=["user"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="user/login")
SECRET_KEY = "login"
ALGORITHM = "HS256"
###############################################################################


def userAuth(userName: str, password: str):
    currentUser = user_collection.find_one({"userName": userName})

    if not currentUser:
        return False
    if not bcrypt_context.verify(password, currentUser["password"]):
        return False
    return currentUser


###############################################################################


def get_current_user(token: str = Depends(oauth_bearer)):
    """
    Retrieves user information from a JWT token.

    Args:
        token (str): The JWT token provided in the request header.

    Returns:
        dict: A dictionary containing user information decoded from the JWT token.

    Raises:
        HTTPException: Raises HTTP 401 UNAUTHORIZED if the token cannot be validated.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


###############################################################################


@userRouter.post("/createUser")
async def createUser(newUserRequest: userModel):
    """
    Creates a new user with the provided user information.

    Args:
        newUserRequest (userModel): The request payload containing user information.

    Returns:
        str: A message indicating the success of the user creation.

    Raises:
        HTTPException: Raises HTTP 422 UNPROCESSABLE ENTITY if user creation fails.
    """
    try:
        newUser = userModel()
        newUser = user_collection.insert_one(newUser.dict())
        newUserId = newUser.inserted_id
        current_user = user_collection.find_one_and_update(
            {"_id": newUserId},
            {
                "$set": {
                    "userName": newUserRequest.userName,
                    "email": newUserRequest.email,
                    "password": bcrypt_context.hash(newUserRequest.password),
                }
            },
        )

        return "success"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to create user: {str(e)}",
        )


###############################################################################


@userRouter.get("/getAllUsers")
async def getAllUsers():
    """
    Retrieves a list of all users from the database.

    Returns:
        list: A list of dictionaries representing user information.
    """
    try:
        allUsers = list_users_serial(user_collection.find())
        return allUsers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user data: {str(e)}",
        )


###############################################################################


def createLoginToken(userId: str, userName: str, expiresDelta: timedelta = None):
    """
    Creates a JWT token for user authentication.

    Args:
        userId (str): The user ID to be included in the token.
        userName (str): The username to be included in the token.
        expiresDelta (timedelta, optional): The expiration duration for the token.
                                            If not provided, the token will not have an expiration.

    Returns:
        str: The generated JWT token.
    """
    try:
        encoded_data = {
            "name": userName,
            "id": userId,
        }
        if expiresDelta is not None:
            expire_time = datetime.utcnow() + expiresDelta
            encoded_data.update({"exp": expire_time})
        token = jwt.encode(encoded_data, SECRET_KEY, ALGORITHM)
        return token
    except Exception as e:
        raise ValueError(f"Error creating login token: {str(e)}")


###############################################################################
@userRouter.get("/login")
async def getLoginToken(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Endpoint for user login and token generation.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
        dict: A dictionary containing the generated access token and token type.

    Raises:
        HTTPException: Raises HTTP 401 UNAUTHORIZED if login validation fails.
    """
    try:
        currentUser = userAuth(userName=form_data.username, password=form_data.password)
        if currentUser is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed validation"
            )

        token = createLoginToken(
            userId=str(currentUser["_id"]),
            userName=currentUser["userName"],
            # expiresDelta=timedelta(minutes=200),
        )

        user_collection.update_one(
            {"_id": currentUser["_id"]}, {"$set": {"token": token}}
        )

        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}",
        )


###############################################################################


@userRouter.post("/addPlatform", status_code=status.HTTP_201_CREATED)
async def addPlatform(
    new_platform: str, current_user: dict = Depends(get_current_user)
):
    """
    Adds a new platform to the user's list of platforms.

    Args:
        new_platform (str): The name of the new platform to be added.
        current_user (dict): The current user's information obtained from the JWT token.

    Returns:
        list: A list of user platforms after adding the new platform.

    Raises:
        HTTPException: Raises HTTP 404 NOT FOUND if the platform already exists in the user data.
    """
    try:
        new_platform = new_platform.strip('"')

        current_user_data = user_collection.find_one(
            {"_id": ObjectId(current_user["id"])}
        )
        if new_platform in current_user_data["user_platforms"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The platform already exists in the user data",
            )
        user_platforms = current_user_data["user_platforms"]
        user_platforms.append(new_platform)
        updated_user = user_collection.find_one_and_update(
            {"_id": ObjectId(current_user["id"])},
            {"$set": {"user_platforms": user_platforms}},
            return_document=ReturnDocument.AFTER,
        )

        return updated_user["user_platforms"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


###############################################################################


@userRouter.post("/addrPlatformInfo")
async def addTimeForPlatform(
    platform: str,
    timeSpent: float,
    scrollDistance: float,
    current_user: dict = Depends(get_current_user),
):
    """
    Adds or updates time spent and scroll distance information for a specific platform.

    Args:
        platform (str): The name of the platform for which information is being added.
        timeSpent (float): The time spent on the platform.
        scrollDistance (float): The scroll distance on the platform.
        current_user (dict): The current user's information obtained from the JWT token.

    Returns:
        dict: A dictionary containing the updated platform information.

    Raises:
        HTTPException: Raises HTTP 404 NOT FOUND if the platform does not exist in the user data.
    """
    try:
        platform = platform.strip('"')
        current_user_data = user_collection.find_one(
            {"_id": ObjectId(current_user["id"])}
        )
        print(current_user_data["user_platforms"])
        if platform not in current_user_data["user_platforms"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The platform does not exist in the user data",
            )

        if platform not in list(current_user_data["platform_info"].keys()):
            current_user_data["platform_info"][platform] = {
                "time_spent": timeSpent,
                "scroll_distance": scrollDistance,
            }
        else:
            current_user_data["platform_info"][platform]["time_spent"] += timeSpent
            current_user_data["platform_info"][platform][
                "scroll_distance"
            ] += scrollDistance

        updated_user = user_collection.find_one_and_update(
            {"_id": ObjectId(current_user["id"])},
            {"$set": {"platform_info": current_user_data["platform_info"]}},
            return_document=ReturnDocument.AFTER,
        )

        return updated_user["platform_info"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
