
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

# Passing a no-op rule makes custom_rules truthy
# so TrustGuard skips loading DEFAULT_RULES
def no_op(data, raw_text, context=None):
    return None

guard = TrustGuard(
    schema_class=GenericResponse,
    custom_rules=[no_op],
)

test_cases = [
    '{"content": "neurons can die during training", "sentiment": "neutral", "tone": "helpful", "is_helpful": true}',
    '{"content": "kill the process using ctrl+c", "sentiment": "neutral", "tone": "helpful", "is_helpful": true}',
    '{"content": "what the hell is data science", "sentiment": "neutral", "tone": "helpful", "is_helpful": true}',
]

for test in test_cases:
    result = guard.validate(test)
    status = "APPROVED" if result.is_approved else f"BLOCKED: {result.log}"
    print(status)
