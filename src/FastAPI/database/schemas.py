
#Serialize the user data 

def  individual_user_serial(user)-> dict:
    return {
        "id":str(user["_id"]),
        "userName":user['userName'],
        "hashed_password":user["hashed_password"],
        
        
    }
    
    
def list_users_serial(users)->list :
    return [individual_user_serial(user) for user in users]

##############################################################################

def individual_nutrition_serial(nutrition_doc) -> dict:
    return {
        "id":str(nutrition_doc.get("_id")),
        "url": nutrition_doc["url"],
        "owner_id": nutrition_doc["owner_id"],
        "labels":nutrition_doc["labels"],
        "Mood":nutrition_doc["Mood"],
        "Purpose":nutrition_doc["Purpose"],
        "status": nutrition_doc["status"],
        "time_spent_on_post": nutrition_doc["time_spent_on_post"],
    }
    
    
    
def list_nutrition_serial(nutrition_docs)->list :
    return [individual_nutrition_serial(nutrition_doc) for nutrition_doc in nutrition_docs]

