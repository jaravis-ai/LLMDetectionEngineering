# ./src/agent/graph.py
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Any, Dict

#Langchain Imports 
from langchain_openai import ChatOpenAI
from langchain_openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI



# StateGraph Import 
from langgraph.graph import StateGraph
from langgraph.graph import START, END

#LangChain Runnable Config
from langchain_core.runnables import RunnableConfig

#Configuration Import
from agent.configuration import Configuration

#from detection_engineering.detection_logic import IngestionAgent, ExtractionAgent, MappingAgent
from detection_engineering.detection_logic import *

#Other Imports for Threat Intelligence
from OTXv2 import OTXv2  
from attackcti import attack_client



_ = load_dotenv()  # take environment variables from .env.

#Env Variables
OTX_API_KEY = os.getenv("OTX_API_KEY")


def get_llm(configurable: Configuration):
    #from langchain.chat_models import ChatOpenAI
    #llm = ChatOpenAI(
    #    model_name=configurable.llm,
    #    temperature=configurable.temperature,
    #    max_retries=configurable.max_retries,
    #    verbose=configurable.verbose,
    #    #openai_api_key=os.getenv("OPENAI_API_KEY"),
    #    #openai_api_key="sk-...",
    #)
    #return llm
    """Helper function to initialize LLM based on configuration.

    Uses JSON mode if use_tool_calling is False, otherwise regular mode for tool calling.

    Args:
        configurable: Configuration object containing LLM settings

    Returns:
        Configured LLM instance
    """
    if configurable.llm == "gpt-4o":

        #llm = ChatOpenAI(
        #model_name=configurable.llm,
        #temperature=configurable.temperature,
        #max_retries=configurable.max_retries,
        #verbose=configurable.verbose,
        #openai_api_key=os.getenv("OPENAI_API_KEY"),
        #openai_api_key="sk-...",
    #)
        llm = AzureOpenAI(
            #model_name=os.getenv("MODEL"),
            model_name=configurable.llm,
            deployment_name=os.getenv("MODEL"),
            #temperature=configurable.temperature,
            #max_retries=configurable.max_retries,
            #verbose=configurable.verbose,
            #openai_api_key=os.getenv("AZURE_API_KEY"),
            api_key=os.getenv("AZURE_API_KEY"),
            azure_endpoint="https://bfsi-genai-demo.openai.azure.com/",
            #openai_api_version=os.getenv("API_VERSION"),
            api_version=os.getenv("API_VERSION"),
            #azure_deployment=os.getenv("MODEL"),
        )
        llm = AzureChatOpenAI(
            #model_name=os.getenv("MODEL"), 
            azure_deployment=os.getenv("MODEL"),
            api_key=os.getenv("AZURE_API_KEY"),
            azure_endpoint="https://bfsi-genai-demo.openai.azure.com/",
            api_version=os.getenv("API_VERSION"),
            temperature=configurable.temperature,
            max_retries=configurable.max_retries,
            verbose=configurable.verbose,
            max_tokens=4000,
        )
    else:    # For o3-mini models reasoning model 
        llm = ChatOpenAI(
            model_name=configurable.llm,
            #temperature=configurable.temperature,
            max_retries=configurable.max_retries,
            verbose=configurable.verbose,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            #openai_api_key="sk-...",
        )
    return llm





# Define the state schema for the agent
class AgentState(BaseModel):
    question: str
    answer: str = ""
    pulses: list = []
    techniques: list = []




#----------------- Example Agents -----------------



""" # Define a simple node function
def respond(state: "AgentState", config: RunnableConfig):
    # Extract configuration
    configurable = Configuration.from_runnable_config(config)
    llm = get_llm(configurable)
    # Use the LLM to generate a response
    print(f"Question: {state.question}")
    response = llm.invoke(f"Answer the question: {state.question}")
    print(type(response))
    #print(response.__dict__)
    state.answer = response.content
    return {"answer": state.answer} """



# Define a simple node function
#def respond(state: AgentState):
#    state.answer = "Hello! You asked: " + state.question
#    return state


#Detection Engineering Agents
### LLM in Detection Engineering 
# --- Ingestion Agent Boilerplate ---
class IngestionAgent:
    def run(self, state: AgentState, config: RunnableConfig):
        # TODO: Add ingestion logic here
        otx = OTXv2(OTX_API_KEY)
        print("[*] fetching recent pulses from OTX...")
        #pulses = fetch_otx_pulses(otx, max_pages=100)
        pulses = fetch_otx_pulses_raw(OTX_API_KEY, max_pages=1,per_page=20)
        print(f"[*] fetched {len(pulses)} pulses (summary)")
        state.pulses = pulses
        # Fetch ATT&CK techniques
        print("[*] fetching ATT&CK techniques via attackcti...")
        techniques = fetch_attack_techniques()
        state.techniques = techniques
        print(f"[*] got {len(techniques)} techniques")
        print("IngestionAgent: ingesting data...")
        # Example: state.data = ingest_data(state.input)
        return state
    
# --- Extraction Agent Boilerplate ---
class ExtractionAgent:
    def run(self, state: AgentState, config: RunnableConfig):
        # TODO: Add extraction logic here
        print("ExtractionAgent: extracting entities...")
        # Example: state.entities = extract_entities(state.data)
        return state
    
# --- Mapping Agent Boilerplate ---
class MappingAgent:
    def run(self, state: AgentState, config: RunnableConfig):
        # TODO: Add mapping logic here
        print("MappingAgent: mapping extracted data...")
        # Example: state.mapped = map_entities(state.entities)
        return state

# Example: Add agents as nodes in the graph
ingestion_agent = IngestionAgent()
extraction_agent = ExtractionAgent()
mapping_agent = MappingAgent()


# Create the state graph
graph = StateGraph(state_schema=AgentState,config_schema=Configuration, 
                   #config_type=RunnableConfig,
                   #name="JaraviS Agent", description="A simple agent that answers questions.",
                   #version="0.1.0",
                   )


graph.add_node("ingestion", ingestion_agent.run)
#graph.add_node("extraction", extraction_agent.run)
#graph.add_node("mapping", mapping_agent.run)

# Example: Set up the flow between agents
graph.set_entry_point("ingestion")
graph.add_edge("ingestion",END)
#graph.add_edge("ingestion", "extraction")
#graph.add_edge("extraction", "mapping")
#graph.add_edge("mapping", END)


""" # Add the node to the graph. This node will interrupt when it is invoked.
graph.add_node("node1", respond)
#graph.add_edge("__start__", "node1")
#graph.add_edge("node1", "__end__")
graph.set_entry_point("node1")
#graph.add_edge(START, "node1")
graph.add_edge("node1", END) """






#g1 = graph.compile()
#g1.name = "JaraviS Agent"



#@graph.node()
#def respond(state: AgentState):
#    state.answer = "Hello! You asked: " + state.question
#    return state