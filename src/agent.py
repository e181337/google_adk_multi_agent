from google.adk.agents import LlmAgent
from src.prompts.triage_agent_prompt import TRIAGE_AGENT_INSTRUCTION, TRIAGE_AGENT_DESCRIPTION
from src.prompts.drafting_agent_prompt import DRAFTING_AGENT_INSTRUCTION, DRAFTING_AGENT_DESCRIPTION
from src.prompts.root_agent_prompt import ROOT_AGENT_INSTRUCTION , ROOT_AGENT_DESCRIPTION
from src.config import get_model_settings
from src.schemas.agent_output_schemas import IntentTriageOutput, DraftingOutput, RootOutput
from src.tools.retrieval_tool import retrieval_tool

model_settings = get_model_settings()

triage_agent = LlmAgent(name="triage_agent",
                    description=TRIAGE_AGENT_DESCRIPTION,
                    model=model_settings.triage_model,
                    instruction=TRIAGE_AGENT_INSTRUCTION,
                    output_schema=IntentTriageOutput,
                    output_key="triage_result"
                    )

drafting_agent = LlmAgent(name="drafting_agent",
                        description=DRAFTING_AGENT_DESCRIPTION,
                        model=model_settings.drafting_model,
                        instruction=DRAFTING_AGENT_INSTRUCTION,
                        output_schema=DraftingOutput,
                        output_key="drafting_result"
                        )

root_agent = LlmAgent(name="root_agent",
                    description=ROOT_AGENT_DESCRIPTION,
                    model=model_settings.root_model,
                    instruction=ROOT_AGENT_INSTRUCTION,
                    output_schema=RootOutput,
                    output_key="root_result",
                    tools=[retrieval_tool],
                    sub_agents=[triage_agent, drafting_agent]
                    )
