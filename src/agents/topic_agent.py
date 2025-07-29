from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from src.mongoDB import get_series_posts_by_id, get_actual_series_id, get_series_topic, get_programing_knowledge

def get_topic_agent(model,prompt_query):
    topic_agent = create_react_agent(
        model=model,
        tools=[get_series_posts_by_id, get_actual_series_id,get_series_topic, get_programing_knowledge],
        prompt=prompt_query
    )
    return topic_agent

