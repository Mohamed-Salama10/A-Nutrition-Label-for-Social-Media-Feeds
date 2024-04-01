from fastapi import FastAPI, Depends, HTTPException
from src.FastAPI.App.Routes import user_routes
from src.FastAPI.App.Routes import nutrition_routes
from fastapi.middleware.cors import CORSMiddleware




# model.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(user_routes.userRouter)

app.include_router(nutrition_routes.nutritionRouter)

