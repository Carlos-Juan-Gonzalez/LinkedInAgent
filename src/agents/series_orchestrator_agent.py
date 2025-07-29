from langgraph.prebuilt import create_react_agent
from src.mongoDB import set_next_series, set_series_topic, get_series_id_topic, get_last_5_posts, get_programing_knowledge,hold_next_series

def get_series_orquestrator_agent(model,prompt_query):
    series_orchestrator_agent = create_react_agent(
        model=model,
        tools=[set_next_series,set_series_topic,get_series_id_topic,get_last_5_posts,get_programing_knowledge,hold_next_series],
        prompt=prompt_query
    )
    return series_orchestrator_agent
