import os
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from pymongo.server_api import ServerApi
import atexit
from datetime import date, datetime
from langchain_core.tools import tool

load_dotenv()

uri = os.getenv("MONGODB_URI")

CLIENT = MongoClient(uri, server_api=ServerApi('1'))
DB = CLIENT["linkedin_posts"]
POST_COLLECTION = DB["posts"]
SERIES_COLLECTION = DB["series"]
STATE_COLLECTION = DB["state"]
atexit.register(CLIENT.close)

# === Table: Posts ===

def get_post(post_id)-> dict:
    response = POST_COLLECTION.find_one({"post_id": int(post_id)})
    return response or {}

def get_last_post_id():
    response = POST_COLLECTION.find().sort("post_id", DESCENDING).limit(1)
    post_id = 0

    for post in response:
        post_id = int(post.get("post_id"))

    return post_id

def set_posts(post_id: int, post: str, topic: str, series_id: int | None):
    result = POST_COLLECTION.update_one(
        {"post_id": post_id},
        {
            "$set": {
                "post": post,
                "topic": topic,
                "series_id": series_id,
                "date": date.today().isoformat(),
                "impressions": []
            }
        },
        upsert=True
    )

    if series_id is not None:
        add_post_to_list(series_id, post_id)

    return result

def set_posts_impressions(post, num_impressions, date):
    result = POST_COLLECTION.update_one(
        {
            "post": {"$regex": post},
            "impressions.date": {"$ne": date}  # solo si NO existe esa fecha
        },
        {
            "$push": {
                "impressions": {
                    "num_impressions": num_impressions,
                    "date": date
                }
            }
        },
        upsert=True
    )
    return result

@tool
def get_last_5_posts(post_id):
    """retrieve the last 5 posts"""
    response = POST_COLLECTION.find().sort("post_id",DESCENDING).limit(5)
    posts =[]
    for post in response:
        posts.append(post)
    return posts or []

# === Table: State ===

@tool
def get_actual_series_id():
    """retrieve the id of the actual series of posts"""
    response = STATE_COLLECTION.find_one()
    if response is None:
        return "No actual serie"
    return response.get("actual_serie", "")   

def _get_actual_series_id():
    response = STATE_COLLECTION.find_one()
    if response is None:
        return "No actual serie"
    
    return response.get("actual_serie", "")   

@tool
def get_programing_knowledge():
    """retrieve a list of programming languages, tecnologies and frameworks known by the post author"""
    response = STATE_COLLECTION.find_one({})
    if response is None:
        return []
    return response.get("knowledge")
@tool
def get_global_feedback():
    """Retrieve the global feedback that guide the style of the posts"""
    response = STATE_COLLECTION.find()
    feedback = ""
    for i in response:
        feedback = i["global_feedback"]
    return feedback

@tool
def set_global_feedback(query: str):
    """Save the global feedback in the data base for next iterations"""
    STATE_COLLECTION.update_one({}, {"$set": {"global_feedback": query}}, upsert=True)

@tool
def set_next_series():
    """Adds one the actual_serie id"""
    STATE_COLLECTION.update_one({}, {"$set":{"actual_serie": (get_last_series_id() + 1)}})

@tool
def hold_next_series():
    """set actual_series to None"""
    STATE_COLLECTION.update_one({}, {"$set":{"actual_serie": None}})

# === Table: Series ===

@tool
def get_series_posts_by_id(series_id: str):
    """retrieve the structured content of all the current posts of a series by the series id"""
    response = SERIES_COLLECTION.find_one({"series_id":int(series_id)})
    result = ""
    if response == None or len(response["posts_list"]) == 0:
        result = "No post in the series"
    else:
        for post_id in response["posts_list"]:
            post = get_post(post_id)
            result += f"Post id: {post_id}, Post: {post.get('post')}\n"
            
    return result

@tool
def get_series_id_topic():
    """retrieve the structured content of all series and it's topics"""
    response = SERIES_COLLECTION.find()
    result = ""
    for serie in response:
        result += f'Series_id: {serie.get("series_id")}\n'
        result += f'Series_topic: {serie.get("series_topic")}\n\n'
            
    return result

@tool
def get_series_topic(series_id: str):
    """retrieve the topic of the actual series of posts"""
    response = SERIES_COLLECTION.find_one({"series_id": int(series_id)})
    if response is None:
        return "No actual serie"
    return response.get("series_topic")


def get_last_series_id():
    response = SERIES_COLLECTION.find().sort("series_id", DESCENDING).limit(1)
    series_id = 0

    for series in response:
        series_id = int(series.get("series_id"))

    return series_id

@tool
def set_series_topic(series_topic: str):
    """Sets the topic for a new series of posts"""
    SERIES_COLLECTION.update_one(
        {"series_id": _get_actual_series_id()},
        {"$set": {
            "series_topic": series_topic, 
            "posts_list": []
            }
        }, 
        upsert=True
        )

def add_post_to_list(series_id: int,post_id: int):
    SERIES_COLLECTION.update_one(
        {"series_id": series_id}, 
        {"$addToSet": {
            "posts_list": post_id
            }
        }, 
        upsert=True
        )



