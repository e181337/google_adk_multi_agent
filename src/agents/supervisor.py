from dataclasses import dataclass


@dataclass
class SupervisorResult:
    retry: bool


class OrchestratorSupervisorAgent:

    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")

    def _validate(self, attempt: int, verification_ok: bool, compliance_ok: bool, max_retries: int) -> None:
        self._check_type(attempt, "attempt", int)
        self._check_type(max_retries, "max_retries", int)
        self._check_type(verification_ok, "verification_ok", bool)
        self._check_type(compliance_ok, "compliance_ok", bool)

        if attempt < 1:
            raise ValueError("attempt must be >= 1")

        if max_retries < 1:
            raise ValueError("max_retries must be >= 1")

    def run(
        self,
        attempt: int,
        verification_ok: bool,
        compliance_ok: bool,
        max_retries: int
    ) -> SupervisorResult:

        self._validate(attempt, verification_ok, compliance_ok, max_retries)

        if not compliance_ok:
            retry = False

        elif verification_ok:
            retry = False

        elif not verification_ok and attempt < max_retries:
            retry = True

        else:
            retry = False

        return SupervisorResult(retry)