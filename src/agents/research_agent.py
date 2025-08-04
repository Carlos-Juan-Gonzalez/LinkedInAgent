from ddgs import DDGS
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from src.models import ResearchResponseSchema

@tool
def web_search(query: str) -> str:
    """Perform a search on the internet using DuckDuckGo. Returns a brief summary of the top results."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            output = []
            for r in results:
                title = r.get("title", "")
                href = r.get("href", "")
                body = r.get("body", "")
                output.append(f"{title}\n{href}\n{body}")
            return "\n\n---\n\n".join(output) if output else "No results found."
    except Exception as e:
        print(f"Error in web_search: {e}")
        return "Error: search failed"
    
def get_research_agent(model,prompt_query):
    research_agent = create_react_agent(
        model=model,
        tools=[web_search],
        prompt=prompt_query,
        response_format=("structured information to be later used for and LLM",ResearchResponseSchema)
    )
    return research_agent


