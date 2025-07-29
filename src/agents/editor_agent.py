from langgraph.prebuilt import create_react_agent



def get_editor_agent(model,prompt_query):
    editor_agent = create_react_agent(
        model=model,
        tools=[],
        prompt=prompt_query
    )
    return editor_agent
