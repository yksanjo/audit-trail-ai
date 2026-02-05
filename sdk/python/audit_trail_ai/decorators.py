"""Decorators for automatic audit logging."""
import functools
import time
from typing import Any, Callable, Optional

from audit_trail_ai.client import AuditClient
from audit_trail_ai.types import ComplianceStandard, DecisionType


def audit_llm_call(
    client: AuditClient,
    model_name: Optional[str] = None,
    provider: str = "openai",
    decision_type: DecisionType = DecisionType.GENERATION,
    compliance_standards: Optional[list[ComplianceStandard]] = None,
):
    """Decorator to automatically audit LLM calls.
    
    Args:
        client: AuditClient instance
        model_name: Model name (can be extracted from function if not provided)
        provider: LLM provider
        decision_type: Type of decision
        compliance_standards: Compliance standards to apply
        
    Example:
        >>> client = AuditClient(api_key="key")
        >>> @audit_llm_call(client, model_name="gpt-4")
        ... def ask_question(prompt: str) -> str:
        ...     return openai.ChatCompletion.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract prompt from args or kwargs
            prompt = kwargs.get('prompt') or (args[0] if args else '')
            
            # Call the function
            start_time = time.time()
            result = func(*args, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response
            response = result
            if hasattr(result, 'choices'):
                response = result.choices[0].message.content
            
            # Extract token usage if available
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(result, 'usage'):
                prompt_tokens = result.usage.prompt_tokens
                completion_tokens = result.usage.completion_tokens
            
            # Log the interaction
            client.log_llm_interaction(
                model_name=model_name or func.__name__,
                prompt=str(prompt),
                response=str(response),
                provider=provider,
                decision_type=decision_type,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                compliance_standards=compliance_standards,
            )
            
            return result
        return wrapper
    return decorator
