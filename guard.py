"""
guard.py — TrustGuard output validation
"""

from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from judge import LLMJudge

guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[],
    judge=LLMJudge(),
)