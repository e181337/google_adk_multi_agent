from google.adk.agents import LlmAgent

from src.prompts.root_agent_prompt import ROOT_AGENT_INSTRUCTION , ROOT_AGENT_DESCRIPTION
from src.prompts.summary_agent_prompt import SUMMARY_AGENT_INSTRUCTION, SUMMARY_AGENT_DESCRIPTION
from src.prompts.translation_agent_prompt import TRANSLATION_AGENT_INSTRUCTION, TRANSLATION_AGENT_DESCRIPTION
from src.prompts.taxonomy_agent_prompt import TAXONOMY_AGENT_INSTRUCTION, TAXONOMY_AGENT_DESCRIPTION

from src.config import get_model_settings
from src.tools.retrieval_tool import retrieval_tool
from src.tools.safety_tool import safety_tool
from src.tools.extraction_tool import entity_extraction_tool

model_settings = get_model_settings()

summary_agent = LlmAgent(name="summary_agent",
                         description=SUMMARY_AGENT_DESCRIPTION,
                         model=model_settings.summary_model,
                         instruction=SUMMARY_AGENT_INSTRUCTION,
                         output_key="summary_result"
                         )

translation_agent = LlmAgent(name="translation_agent",
                         description=TRANSLATION_AGENT_DESCRIPTION,
                         model=model_settings.translation_model,
                         instruction=TRANSLATION_AGENT_INSTRUCTION,
                         output_key="translation_result"
                         )

taxonomy_agent = LlmAgent(name="taxonomy_agent",
                         description=TAXONOMY_AGENT_DESCRIPTION,
                         model=model_settings.taxonomy_model,
                         instruction=TAXONOMY_AGENT_INSTRUCTION,
                         output_key="taxonomy_result"
                         )


root_agent = LlmAgent(
    name="root_agent",
    description=ROOT_AGENT_DESCRIPTION,
    model=model_settings.root_model,
    instruction=ROOT_AGENT_INSTRUCTION,
    output_key="root_result",
    tools=[safety_tool, retrieval_tool, entity_extraction_tool],
    sub_agents=[summary_agent, translation_agent, taxonomy_agent]
)