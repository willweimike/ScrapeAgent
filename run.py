import os
import time
import requests
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END

from tavily import TavilyClient
from ddgs import DDGS


load_dotenv()

BRIGHTDATA_API_KEY = os.getenv('BRIGHTDATA_API_KEY')
BRIGHTDATA_SERP_ZONE = os.getenv('BRIGHTDATA_SERP_ZONE')
BRIGHTDATA_PERPLEXITY_DATASET_ID = os.getenv('BRIGHTDATA_PERPLEXITY_DATASET_ID')
TAVILY_KEY = os.getenv("TAVILY_KEY")
TAVILY_CLIENT = TavilyClient(api_key=TAVILY_KEY)

HEADERS = {
    'Authorization': f'Bearer {BRIGHTDATA_API_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


@tool(description='Search using Google')
def google_search(query):
    print('Google tool is being used...')

    payload = {
        'zone': BRIGHTDATA_SERP_ZONE,
        'url': f'https://google.com/search?q={requests.utils.quote(query)}&brd_json=1',
        'format': 'raw',
        'country': 'US'
    }

    try:
        data = requests.post('https://api.brightdata.com/request?async=true', headers=HEADERS, json=payload).json()

        results = []

        for item in data.get('organic'):
            results.append(f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item.get('description', '')}")

        return '\n\n'.join(results)[:10000]
    except:
        return ""
#
#
@tool(description='Search using Bing')
def bing_search(query):
    print('Bing tool is being used...')

    payload = {
        'zone': BRIGHTDATA_SERP_ZONE,
        'url': f'https://bing.com/search?q={requests.utils.quote(query)}&brd_json=1',
        'format': 'raw',
        'country': 'US'
    }
    try:
        data = requests.post('https://api.brightdata.com/request?async=true', headers=HEADERS, json=payload).json()

        results = []

        for item in data.get('organic'):
            results.append(f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item.get('description', '')}")

        return '\n\n'.join(results)[:10000]
    except:
        return ""
#
#
@tool(description='Search using Reddit')
def reddit_search(query):
    print('Reddit tool is being used...')

    payload = {
        'zone': BRIGHTDATA_SERP_ZONE,
        'url': f"https://google.com/search?q={requests.utils.quote('site:reddit.com ' + query)}&brd_json=1",
        'format': 'raw',
        'country': 'US'
    }
    try:
        data = requests.post('https://api.brightdata.com/request?async=true', headers=HEADERS, json=payload).json()

        results = []

        for item in data.get('organic'):
            results.append(f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item.get('description', '')}")

        return '\n\n'.join(results)[:10000]
    except:
        return ""


@tool(description='Use Perplexity to do some research for a question')
def perplexity_search(query):
    print('Perplexity tool is being used...')

    payload = [
        {
            "url": "https://www.perplexity.ai",
            "prompt": query
        }
    ]

    url = f'https://api.brightdata.com/datasets/v3/trigger?dataset_id={BRIGHTDATA_PERPLEXITY_DATASET_ID}&format=json&custom_output_fields=answer_text_markdown|sources'

    try:
        response = requests.post(url, headers=HEADERS, json=payload)

        snapshot_id = response.json()['snapshot_id']

        while requests.get(f'https://api.brightdata.com/datasets/v3/progress/{snapshot_id}', headers=HEADERS).json()['status'] != 'ready':
            time.sleep(5)

        data = requests.get(f'https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json', headers=HEADERS).json()[0]

        return data['answer_text_markdown'] + '\n\n' + str(data.get('sources', []))
    except:
        return ""


@tool(description='Search using Tavily')
def tavily_search(query):
    print('Tavily tool is being used...')

    response = ""
    try:
        res = TAVILY_CLIENT.search(query=query, topic="general", max_results=1)
        results = res.get("results")
        for k, v in results[0].items():
            if k == "content":
                response = v
                break
        return response

    except:
        return response


@tool(description='Search using DuckDuckGo')
def duckduckgo_search(query):
    print('DuckDuckGo tool is being used...')

    response = ""
    try:
        result = DDGS().text(query=query, safesearch='off', max_results=1)
        for k, v in result[0].items():
            if k == "body":
                response = v
                break

        return response

    except:
        return response


llm = ChatOllama(model="qwen3:8b")

agent = create_react_agent(
    model = llm,
    tools = [google_search, bing_search, perplexity_search, reddit_search, tavily_search, duckduckgo_search],
    debug = False,
    prompt = "Try to use all the tools to answer user questions. Preferably use more tools. When giving an answer, aggregate and summarize all information you get. Always provide a list of the sources which you used to find the information you provided. Make sure to add all links and sources here."
)


def agent_node(state):
    result = agent.invoke({'messages': [('human', state['query'])]})
    state['answer'] = result['messages'][-1].content

    return state


graph = StateGraph(dict)
graph.add_node('agent', agent_node)
graph.set_entry_point('agent')
graph.add_edge('agent', END)
app = graph.compile()


if __name__ == '__main__':
    q = input("Query> ")
    print(app.invoke({'query': q})['answer'])

