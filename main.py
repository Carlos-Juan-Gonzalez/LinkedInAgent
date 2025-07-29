import asyncio
from src.graph import Graph
from src.scrapping.posting import create_post

def main():
    graph = Graph()
    final_state = graph.run()

    asyncio.run(create_post(final_state.post))

if __name__ == "__main__":
    main()