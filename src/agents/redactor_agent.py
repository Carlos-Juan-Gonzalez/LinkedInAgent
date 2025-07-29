from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from src.mongoDB import get_actual_series_id, get_series_posts_by_id, get_global_feedback
from datetime import date

@tool
def get_actual_date():
    """Tool to check the actual date for the post"""
    return date.today().isoformat()

def get_redactor_agent(model,prompt_query):
    redactor_agent = create_react_agent(
        model=model,
        tools=[get_actual_date,get_actual_series_id,get_series_posts_by_id, get_global_feedback],
        prompt=prompt_query
    )
    return redactor_agent

