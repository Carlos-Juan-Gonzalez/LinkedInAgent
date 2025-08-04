from langgraph.prebuilt import create_react_agent
from src.models import EditorResponseSchema


def get_editor_agent(model,prompt_query):
    editor_agent = create_react_agent(
        model=model,
        tools=[],
        prompt=prompt_query,
        response_format=(    
            "'approved' must be either True or False depending on whether the post is valid. 'feedback' must justify the decision clearly, and if applicable, specify the required improvements.",
            EditorResponseSchema
        )
    )
    return editor_agent
    
