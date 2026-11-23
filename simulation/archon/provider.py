import os
import signal
import time
from dataclasses import dataclass

from .contracts import DECISION_SCHEMA, PROMPT, canonical, require


@dataclass(frozen=True)
class Reply:
    output: str
    model: str
    response_id: str | None
    input_tokens: int
    output_tokens: int


class Offline:
    name = "offline"
    model = "fixture-1.0"

    def decide(self, data, config):
        period = data["period"]
        if period == 0:
            outcome, instrument, rate = "INSUFFICIENT_INFORMATION", None, None
        elif period == 1:
            outcome, instrument, rate = "PROPOSE", "income-tax", 1525
        elif period == 2:
            outcome, instrument, rate = "PROPOSE", "sales-tax", 540
        else:
            outcome, instrument, rate = "ABSTAIN", None, None
        output = canonical({
            "outcome": outcome, "instrument": instrument, "rate_bp": rate,
            "duration_months": 1 if rate else None, "problem": "Fascicolo tecnico deterministico.",
            "objective": "Verificare il ciclo giuridico.", "alternative": "Mantenimento delle aliquote.",
            "rationale": "Risposta della fixture offline.", "uncertainty": "Copertura informativa preliminare.",
            "expected_effect": "Risposta del gettito da osservare.",
        })
        return Reply(output.decode(), self.model, None, 0, 0)


class OpenAIProvider:
    name = "openai"

    def __init__(self, model, timeout):
        require(model and len(model) <= 120 and all(c.isalnum() or c in "-._:" for c in model), "ARCHON_MODEL non valido")
        require(os.environ.get("OPENAI_API_KEY"), "OPENAI_API_KEY assente. La modalità offline è disponibile.")
        import httpx
        from openai import OpenAI
        self.model = model
        self.client = OpenAI(base_url="https://api.openai.com/v1", max_retries=0, timeout=timeout,
                             http_client=httpx.Client(timeout=timeout, trust_env=False))

    def decide(self, data, config):
        def deadline(signum, frame):
            raise TimeoutError("provider_timeout")

        previous = signal.signal(signal.SIGALRM, deadline)
        signal.setitimer(signal.ITIMER_REAL, config["timeout"])
        try:
            response = self.client.responses.create(
                model=self.model, instructions=PROMPT.read_text(), input=canonical(data).decode(),
                max_output_tokens=config["output_tokens"], store=False,
                text={"format": {"type": "json_schema", "name": "archon_decision", "strict": True, "schema": DECISION_SCHEMA}},
            )
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)
        usage = response.usage
        require(usage is not None, "usage_missing")
        return Reply(response.output_text, response.model, response.id, usage.input_tokens, usage.output_tokens)


def estimate_input(data):
    # Conservative local guard for byte-tokenized input plus envelope allowance.
    return sum(len(item) for item in (canonical(data), PROMPT.read_bytes(), canonical(DECISION_SCHEMA))) + 1024


def cents_micro(input_tokens, output_tokens, config):
    return input_tokens * config["input_micro_usd_per_token"] + output_tokens * config["output_micro_usd_per_token"]


def decision_latency(start):
    return round((time.monotonic() - start) * 1000)
