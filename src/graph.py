import os
import json
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END
from typing import Literal

from src.prompts import ModelPrompts
from src.models import State
from src.agents.topic_agent import get_topic_agent
from src.agents.research_agent import get_research_agent
from src.agents.redactor_agent import get_redactor_agent 
from src.agents.editor_agent import get_editor_agent
from src.agents.series_orchestrator_agent import get_series_orquestrator_agent
from src.mongoDB import set_posts, get_last_post_id, get_last_series_id

load_dotenv()

def editor_next(state: State )-> Literal["redactor","series","final"]:
    match state.next:
        case "redactor":
            return "redactor"
        case "series":
            return "series"
        case "final":
            return "final"
    return "redactor"

class Graph:
    def __init__(self, model=None, prompts=None):
        self.model = model or init_chat_model("gpt-4o-mini", temperature=0.5, model_provider="openai", api_key=os.getenv("OPENAI_API_KEY"))
        self.prompts = prompts or ModelPrompts()
        self.graph = self.__build_graph__()

    def __build_graph__(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("topic", self._topic_step)
        graph_builder.add_node("research", self._research_step)
        graph_builder.add_node("redactor", self._redactor_step)
        graph_builder.add_node("editor", self._editor_step)
        graph_builder.add_node("series", self._series_orchestration_step)
        graph_builder.add_node("final", self._final_step)

        graph_builder.set_entry_point("topic")
        graph_builder.add_edge("topic", "research")
        graph_builder.add_edge("research", "redactor")
        graph_builder.add_edge("redactor", "editor")
        graph_builder.add_conditional_edges("editor", editor_next,{
            "redactor": "redactor",
            "series": "series",
            "final": "final"
        })
        graph_builder.add_edge("series","final")
        graph_builder.add_edge("final", END)
        
        return graph_builder.compile()
    
    def _topic_step(self, state: State):
        print("topic step")
        topic_agent = get_topic_agent(self.model, self.prompts.TOPIC_PROMPT)
        response = topic_agent.invoke({"messages": [{"role": "user", "content": self.prompts.USER_TOPIC}]})
        topic = ""
        position = ""

        try:
            data = json.loads(response["messages"][-1].content)
            topic = data["topic"]
            position = data["position"]

        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")

        return {"topic": topic, "position": position}
    
    def _research_step(self, state: State):
        print("research step")
        topic = state.topic or "AI"
        research_agent = get_research_agent(self.model, self.prompts.research_prompt(topic))
        response = research_agent.invoke({"messages": [{"role": "user", "content": self.prompts.USER_INITIAL_RESEARCH}]})
        info = ""

        try:
            data = json.loads(response["messages"][-1].content)
            info = data["info"]
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
            
        return {"info": info}
    
    def _redactor_step(self, state: State):
        print("redactor step")
        topic = state.topic or "Agents"
        position = state.position or "StandAlone"
        info = state.info or "No info"
        previous_post = state.previous_post or "No Previous post"
        feedback = state.feedback or "No Feedback"

        redactor_agent = get_redactor_agent(self.model, self.prompts.redactor_prompt(topic, position, info, previous_post, feedback))
        response = redactor_agent.invoke({"messages": [{"role": "user", "content": self.prompts.USER_REDACTOR}]})
        post = response["messages"][-1].content

        return {"post": post }
    
    def _editor_step(self, state: State):
        print("editor step")
        post = state.post or  "No post"
        best = "No best post"
        worst =  "No worst post"

        previous_post = state.previous_post if state.previous_post is not None else "No previous_post"
        editor_agent = get_editor_agent(self.model, self.prompts.editor_prompt(previous_post, best, worst))
        response = editor_agent.invoke({"messages": [{"role": "user", "content": self.prompts.user_editor(post)}]})
        approved = False
        feedback = ""
        try:
            data = json.loads(response["messages"][-1].content)
            approved = data["approved"]
            feedback = data["feedback"]
            
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
        
        if approved:
            if state.position == "Final" or state.position == "StandAlone":
                return {"approved": approved , "next": "series"}
            else:
                return {"approved": approved , "next": "final"}
        else:
            return {"approved": approved ,"feedback": feedback, "next": "redactor"}
        
    def _series_orchestration_step(self, state: State):
        print("series step")
        orchestration_agent = get_series_orquestrator_agent(self.model, self.prompts.SERIES_ORCHESTRATOR_PROMPT)
        orchestration_agent.invoke({"messages": [{"role": "user", "content": self.prompts.USER_SERIES}]})

        return {"next": "final"}
    
    def _final_step(self, state: State):
        print("final step")
        series_id = get_last_series_id() if state.position != "StandAlone" else None
        set_posts((get_last_post_id() + 1), state.post, state.topic, series_id)

        return {"next": END}
    
    def run(self) -> State:
        initial_state = State()
        final_state = self.graph.invoke(initial_state)
        return State(**final_state)
    
