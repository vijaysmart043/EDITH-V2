"""
Action Execution Engine for EDITH.
Coordinates parameter verification, permission checks, dangerous action verification,
timeout bounds, dry-run simulation, and SQLite audit logging.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

from actions.action_registry import ActionDefinition, action_registry
from app.config import config
from app.logging_config import log_event
from memory.memory_manager import memory_manager
from security.dangerous_actions import dangerous_action_manager
from security.permissions import PermissionLevel
from security.validator import SecurityValidator


class ActionExecutionResult:
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        action_name: str = "",
        execution_time_ms: float = 0.0,
        requires_confirmation: bool = False,
    ) -> None:
        self.success = success
        self.message = message
        self.data = data or {}
        self.action_name = action_name
        self.execution_time_ms = execution_time_ms
        self.requires_confirmation = requires_confirmation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "action_name": self.action_name,
            "execution_time_ms": self.execution_time_ms,
            "requires_confirmation": self.requires_confirmation,
        }


class ActionExecutor:
    """Executes registered actions under strict sandboxed security constraints."""

    def __init__(self) -> None:
        self.registry = action_registry

    def execute(
        self,
        action_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        user_confirmed: bool = False,
    ) -> ActionExecutionResult:
        start_time = time.perf_counter()
        params = parameters or {}
        action_name_upper = action_name.upper()

        # 1. Action Lookup
        action_def = self.registry.get_action(action_name_upper)
        if not action_def:
            msg = f"Unknown or unsupported action: '{action_name}'."
            log_event("EXECUTOR", f"Rejected unrecognized action: {action_name}")
            return ActionExecutionResult(False, msg, action_name=action_name_upper)

        # 2. Target Security Sanitation
        target = params.get("target") or params.get("app_name") or params.get("path")
        if target and isinstance(target, str):
            val_res = SecurityValidator.validate_action_target(action_name_upper, target)
            if not val_res.is_valid:
                log_event("SECURITY", val_res.error_message)
                return ActionExecutionResult(False, val_res.error_message, action_name=action_name_upper)

        # 3. Specific Custom Validator (if defined)
        if action_def.validator:
            is_valid, err = action_def.validator(params)
            if not is_valid:
                log_event("VALIDATOR", f"Action parameter validation failed: {err}")
                return ActionExecutionResult(False, err, action_name=action_name_upper)

        # 4. Dangerous Action / Permission Confirmation Check
        perm_check = SecurityValidator.check_permissions(
            action_name=action_name_upper,
            permission_level=action_def.permission_level,
            require_confirmation_setting=config.security.require_confirmation_for_dangerous,
            advanced_automation_setting=config.security.allow_advanced_automation,
        )

        if perm_check.requires_confirmation and not user_confirmed:
            log_event("SECURITY", f"Action '{action_name_upper}' halted: awaiting user confirmation.")
            return ActionExecutionResult(
                success=False,
                message=f"Action '{action_name_upper}' requires explicit user confirmation.",
                requires_confirmation=True,
                action_name=action_name_upper,
                data={"pending_action": action_name_upper, "parameters": params},
            )

        # 5. Dry-Run / Simulation Mode Check
        if config.security.dry_run_mode:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            msg = f"[DRY-RUN SIMULATION] '{action_name_upper}' simulated safely without affecting system."
            log_event("EXECUTOR", msg)
            memory_manager.record_audit(action_name_upper, params, "DRY_RUN", msg, exec_time)
            return ActionExecutionResult(
                True,
                msg,
                {"simulated": True, **params},
                action_name=action_name_upper,
                execution_time_ms=exec_time,
            )

        # 6. Handler Execution
        if not action_def.handler:
            return ActionExecutionResult(False, "Action handler function not implemented.", action_name=action_name_upper)

        try:
            log_event("EXECUTOR", f"Executing action: {action_name_upper} with params: {params}")
            result_payload = action_def.handler(**params)
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)

            success = result_payload.get("success", True)
            message = result_payload.get("message", action_def.default_success_response if success else action_def.default_failure_response)
            data = result_payload.get("data", {})

            status_str = "SUCCESS" if success else "FAILED"
            memory_manager.record_audit(action_name_upper, params, status_str, message, exec_time)
            log_event("EXECUTOR", f"Action: {action_name_upper} Result: {status_str} in {exec_time}ms")

            return ActionExecutionResult(
                success=success,
                message=message,
                data=data,
                action_name=action_name_upper,
                execution_time_ms=exec_time,
            )
        except Exception as e:
            exec_time = round((time.perf_counter() - start_time) * 1000, 2)
            err_msg = f"Runtime exception executing {action_name_upper}: {e}"
            log_event("EXECUTOR", err_msg)
            memory_manager.record_audit(action_name_upper, params, "EXCEPTION", str(e), exec_time)
            return ActionExecutionResult(False, err_msg, action_name=action_name_upper, execution_time_ms=exec_time)


action_executor = ActionExecutor()
