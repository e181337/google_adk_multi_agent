from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from src.prompts.root_agent_prompt import (
    ROOT_AGENT_INSTRUCTION, 
    ROOT_AGENT_DESCRIPTION)
from src.prompts.summary_agent_prompt import (
    SUMMARY_AGENT_INSTRUCTION, 
    SUMMARY_AGENT_DESCRIPTION)
from src.prompts.translation_agent_prompt import (
    TRANSLATION_AGENT_INSTRUCTION, 
    TRANSLATION_AGENT_DESCRIPTION)
from src.prompts.taxonomy_agent_prompt import (
    TAXONOMY_AGENT_INSTRUCTION, 
    TAXONOMY_AGENT_DESCRIPTION)
from src.prompts.router_agent_prompt import (
    ROOTER_AGENT_INSTRUCTION,
    ROOTER_AGENT_DESCRIPTION)
from src.prompts.final_response_agent import (
    FINAL_RESPONSE_AGENT_INSTRUCTION, 
    FINAL_RESPONSE_AGENT_DESCRIPTION)
from src.prompts.task_execution_agent_prompt import (
    TASK_EXECUTION_AGENT_DESCRIPTION,
    TASK_EXECUTION_AGENT_INSTRUCTION,
)
from src.prompts.support_agent_prompt import (
    SUPPORT_AGENT_DESCRIPTION,
    SUPPORT_AGENT_INSTRUCTION)

from src.prompts.entity_extraction_prompt import (
    ENTITY_EXTRACTION_AGENT_DESCRIPTION,
    ENTITY_EXTRACTION_TOOL_INSTRUCTION)
from src.prompts.paralel_execution_prompt import PARALEL_EXECUTION_AGENT_DESCRIPTION
from src.config import get_model_settings
from src.tools.retrieval_tool import retrieval_tool
from src.tools.safety_tool import safety_tool
from src.tools.extraction_tool import entity_extraction_tool

model_settings = get_model_settings()

# Router Agent => decide where to route the summary, translation, taxonomy, support
router_agent = LlmAgent(
                    name="router_agent",
                    description=ROOTER_AGENT_DESCRIPTION,
                    model=model_settings.root_model,
                    instruction=ROOTER_AGENT_INSTRUCTION, 
                    output_key="route_result")

# Summary Agents
summary_agent = LlmAgent(name="summary_agent",
                         description=SUMMARY_AGENT_DESCRIPTION,
                         model=model_settings.summary_model,
                         instruction=SUMMARY_AGENT_INSTRUCTION,
                         output_key="summary_result"
                         )

parallel_summary_agent = LlmAgent(name="parallel_summary_agent",
                                  description=SUMMARY_AGENT_DESCRIPTION,
                                  model=model_settings.summary_model,
                                  instruction=SUMMARY_AGENT_INSTRUCTION,
                                  output_key="parallel_summary_result"
                                  )

# Taxonomy agent
taxonomy_agent = LlmAgent(name="taxonomy_agent",
                         description=TAXONOMY_AGENT_DESCRIPTION,
                         model=model_settings.taxonomy_model,
                         instruction=TAXONOMY_AGENT_INSTRUCTION,
                         output_key="taxonomy_result"
                         )

parallel_taxonomy_agent = LlmAgent(name="parallel_taxonomy_agent",
                                   description=TAXONOMY_AGENT_DESCRIPTION,
                                   model=model_settings.taxonomy_model,
                                   instruction=TAXONOMY_AGENT_INSTRUCTION,
                                   output_key="parallel_taxonomy_result"
                                   )

# Translation agent
translation_agent = LlmAgent(name="translation_agent",
                         description=TRANSLATION_AGENT_DESCRIPTION,
                         model=model_settings.translation_model,
                         instruction=TRANSLATION_AGENT_INSTRUCTION,
                         output_key="translation_result"
                         )
# entity extraction
entity_extraction_agent = LlmAgent(name="entity_extraction_agent",
                         description=ENTITY_EXTRACTION_AGENT_DESCRIPTION,
                         model=model_settings.extraction_model,
                         instruction=ENTITY_EXTRACTION_TOOL_INSTRUCTION,
                         output_key="entity_extraction_result"
                         )

entity_extraction_agent_paralel = LlmAgent(name="paralel_entity_extraction_agent",
                         description=ENTITY_EXTRACTION_AGENT_DESCRIPTION,
                         model=model_settings.extraction_model,
                         instruction=ENTITY_EXTRACTION_TOOL_INSTRUCTION,
                         output_key="paralel_entity_extraction_result"
                         )

# Paralel execution agent
parallel_analysis_agent = ParallelAgent(name="parallel_analysis_agent",
                                        description=PARALEL_EXECUTION_AGENT_DESCRIPTION,
                                        sub_agents=[parallel_taxonomy_agent,
                                                    parallel_summary_agent,
                                                    entity_extraction_agent_paralel]) 


# Support agent =>  handle customer query
support_agent = LlmAgent(
    name="support_agent",
    description=SUPPORT_AGENT_DESCRIPTION,
    model=model_settings.root_model,
    instruction=SUPPORT_AGENT_INSTRUCTION,
    output_key="support_result",
    tools=[safety_tool, retrieval_tool],
)

# Execution agent => decide which one to call
task_execution_agent = LlmAgent(
    name="task_execution_agent",
    description=TASK_EXECUTION_AGENT_DESCRIPTION,
    model=model_settings.root_model,
    instruction=TASK_EXECUTION_AGENT_INSTRUCTION,
    sub_agents=[translation_agent, summary_agent, taxonomy_agent, support_agent, entity_extraction_agent],
)
# generate final answer for customer
final_response_agent = LlmAgent(
    name="final_response_agent",
    description=FINAL_RESPONSE_AGENT_DESCRIPTION,
    model=model_settings.root_model,
    instruction=FINAL_RESPONSE_AGENT_INSTRUCTION,
    output_key="final_response_result",
)
# main agent
root_agent = SequentialAgent(
    name="root_agent",
    description=ROOT_AGENT_DESCRIPTION,
    sub_agents=[
        router_agent,
        task_execution_agent,
        parallel_analysis_agent,
        final_response_agent,
    ],
)
