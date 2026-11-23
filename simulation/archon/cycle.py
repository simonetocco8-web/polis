import time

from .contracts import DECISION_SCHEMA, PROMPT, VERSION, digest, inspect_decision, proposal, require
from .provider import cents_micro, decision_latency, estimate_input

DEFAULTS = {"max_calls": 6, "input_tokens": 12000, "output_tokens": 750, "budget_micro_usd": 0,
            "input_micro_usd_per_token": 0, "output_micro_usd_per_token": 0, "timeout": 30,
            "technical_attempts": 1, "max_proposals_per_period": 1}


def manifest(config, provider, observation):
    run_id = digest([observation["universe"], observation["mandate"], provider.name, provider.model,
                     observation["nomos"], config])
    return {"version": VERSION, "run_id": run_id, "simulator": "Nomos v0.5.0 / Archon v0.6.0",
            "universe": observation["universe"], "replica": observation["universe"], "mandate": observation["mandate"],
            "provider": provider.name, "model_requested": provider.model, "prompt": "1.0",
            "prompt_sha256": digest(PROMPT.read_text()), "decision_schema_sha256": digest(DECISION_SCHEMA),
            "delays": {k: row["delay"] for k, row in observation["indicators"].items()}, "config": config,
            "nomos_initial": observation["nomos"], "mode": "exploratory-smoke" if provider.name == "openai" else "offline"}


def run(archive, nomos, provider, config):
    obs = nomos.view()
    require(obs["mandate"] and obs["open"], "mandate_or_period_closed")
    spec = manifest(config, provider, obs)
    if not archive.events:
        archive.append("manifest", **spec)
    else:
        saved = archive.events[0]["data"]
        require({**spec, "nomos_initial": saved["nomos_initial"], "run_id": saved["run_id"]} == saved, "run_configuration_changed")
    key = f"archon-{digest([obs['universe'], obs['mandate']])[:16]}-{obs['period'] + 1}"
    existing = {e["kind"]: e["data"] for e in archive.events[1:] if e["data"]["key"] == key}
    if "decision" in existing:
        return existing["decision"]
    if "prepared" in existing:
        prepared = existing["prepared"]
    else:
        failure = None
        usage = None
        choice = None
        payload = None
        started = time.monotonic()
        model_data = {key: obs[key] for key in ("period", "day", "indicators", "catalog", "max_duration")}
        model_data["acts"] = [{k: v for k, v in act.items() if k != "id"} for act in obs["acts"]]
        upper = cents_micro(config["input_tokens"], config["output_tokens"], config)
        if "reserved" in existing:
            # A previous request with an unknown outcome is never re-issued.
            failure = "interrupted"
        else:
            reservations = [e for e in archive.events if e["kind"] == "reserved" and e["data"]["call"]]
            exceeded = any(event["kind"] == "prepared" and event["data"]["error"] == "usage_limit"
                           for event in archive.events)
            eligible = (not exceeded and len(reservations) < config["max_calls"]
                        and (len(reservations) + 1) * upper <= config["budget_micro_usd"])
            inputs_fit = estimate_input(model_data) <= config["input_tokens"]
            already_submitted = nomos.receipt(key) is not None
            archive.append("reserved", key=key, observation=obs, observation_sha256=digest(obs),
                           call=bool(eligible and inputs_fit and not already_submitted), model_input_sha256=digest(model_data))
            if already_submitted:
                failure = "already_submitted"
            elif not eligible:
                failure = "budget_exhausted"
            elif not inputs_fit:
                failure = "input_limit"
            else:
                try:
                    reply = provider.decide(model_data, config)
                    usage = {"model_actual": reply.model, "response_id": reply.response_id, "input_tokens": reply.input_tokens,
                             "output_tokens": reply.output_tokens, "estimated_micro_usd":
                             cents_micro(reply.input_tokens, reply.output_tokens, config)}
                    require(type(reply.input_tokens) is int and 0 <= reply.input_tokens <= config["input_tokens"]
                            and type(reply.output_tokens) is int and 0 <= reply.output_tokens <= config["output_tokens"],
                            "usage_limit")
                except Exception as error:
                    if isinstance(error, ValueError) and error.args == ("usage_limit",):
                        failure = "usage_limit"
                    elif isinstance(error, TimeoutError) or type(error).__name__ == "APITimeoutError":
                        failure = "timeout"
                    else:
                        failure = "provider_error"
                else:
                    try:
                        choice = inspect_decision(reply.output, obs)
                        payload = proposal(choice, obs, key) if choice["outcome"] == "PROPOSE" else None
                    except (ValueError, UnicodeError, RecursionError):
                        choice = None
                        failure = "invalid_model_output"
        prepared = archive.append("prepared", key=key, outcome=choice["outcome"] if choice else "PROVIDER_FAILURE",
                                  choice=choice, payload=payload, error=failure, usage=usage,
                                  validation="valid" if choice else ("invalid" if failure == "invalid_model_output" else "not_run"),
                                  latency_ms=decision_latency(started))["data"]
    receipt = None
    transmission = "not_required"
    if prepared["payload"]:
        try:
            receipt = nomos.receipt(key)
            if receipt is None:
                nomos.submit(prepared["payload"])
                receipt = nomos.receipt(key)
            require(receipt and receipt["payload"] == prepared["payload"], "receipt_mismatch")
            transmission = "recorded"
            receipt = {name: receipt[name] for name in ("checks", "state", "formal_state", "event")}
        except (ValueError, OSError):
            # The prepared record can reconcile after a transport error with no second model call.
            return {"key": key, "outcome": prepared["outcome"], "transmission": "pending_reconciliation"}
    return archive.append("decision", key=key, outcome=prepared["outcome"], transmission=transmission, receipt=receipt)["data"]
