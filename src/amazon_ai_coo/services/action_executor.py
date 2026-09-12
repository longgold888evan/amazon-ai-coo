from __future__ import annotations

from amazon_ai_coo.domain.models import ActionProposal, ExecutionResult


class ActionExecutor:
    """Execution boundary.

    V0 is intentionally dry-run only. Amazon Ads/SP-API write adapters will implement
    the same method once auth, idempotency and rollback policies are in place.
    """

    async def execute(self, action: ActionProposal) -> ExecutionResult:
        return ExecutionResult(
            action_id=action.id,
            success=True,
            provider="dry_run",
            message=f"Dry-run accepted: {action.action_type.value}",
            raw={"target": action.target, "parameters": action.parameters},
        )
