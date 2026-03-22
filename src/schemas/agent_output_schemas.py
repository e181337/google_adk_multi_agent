from pydantic import BaseModel, Field
from typing import Optional

class IntentTriageOutput(BaseModel):
    intent_label: str = Field(description="Short label describing the user's intent (e.g., 'summarize', 'draft', 'rewrite', 'question_answering').")
    needs_retrieval: bool = Field(description="Indicates whether external information retrieval is required to fulfill the user's request.")
    draft_goal: str = Field(description="A concise instruction describing what the drafting agent should produce as the final output.")
    last_retrieval_query: Optional[str] = Field(default=None,
                                                description="Search query to use for retrieving relevant information if retrieval is needed; otherwise null.")

class DraftingOutput(BaseModel):
    final_answer: str = Field(description="Final user-facing response generated based on the drafting goal and available context.")
    used_context: Optional[list[str]] = Field(default=None,
                                              description="List of retrieved context snippets that were used to generate the final answer, if any.")
    confidence: Optional[str] = Field(default=None,
                                      description="Optional confidence level of the generated answer (e.g., 'low', 'medium', 'high').")
    

class RootOutput(BaseModel):
    final_answer: str = Field(description="Final user-facing response generated after coordinating triage, retrieval, and drafting.")
    used_retrieval: Optional[bool] = Field(default=None,
                                           description="Indicates whether retrieval was used to generate the final answer.")
    retrieval_results_count: Optional[int] = Field(default=None,
                                                   description="Number of retrieved context items used in generating the response.")
    confidence: Optional[str] = Field(default=None,
                                      description="Optional confidence level of the final answer (e.g., 'low', 'medium', 'high').")