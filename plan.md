# Execution Plan for Distributed Printing System

1. **Environment & Dependencies**
   - Decide target language/runtime (default Python 3.12 unless team decides otherwise) and document the choice.
   - Create `requirements.txt` (or equivalent) including `grpcio`, `grpcio-tools`, `protobuf`, and testing libs (e.g. `pytest`, `pytest-asyncio`).
   - Add setup instructions: `python -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`.
   - Configure formatting/linting tools (e.g. `black`, `isort`, `ruff`) if required by faculty guidelines.

2. **Repository Structure**
   - Establish directories: `proto/`, `printer/`, `client/`, `scripts/`, `tests/`, and `docs/`.
   - Draft README outline covering quick start, architecture, and testing commands.

3. **Protocol Definition & Generation**
   - Finalize `proto/printing.proto` reflecting suggested messages/services.
   - Document any deviations from the suggested schema and justify them.
   - Generate gRPC stubs (`python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/printing.proto`).
   - Add Makefile or shell script under `scripts/` to regenerate stubs.

4. **Shared Utilities**
   - Implement Lamport clock utility module (increment on local event/send, merge on receive).
   - Create message serialization helpers and logging utilities to standardize output format `[TS: ...] CLIENT ...`.

5. **Printer Server Implementation**
   - Build gRPC service in `printer/server.py` implementing `PrintingService.SendToPrinter`.
   - Add CLI options for port (`--port`, default 50051) and simulated delay duration.
   - Ensure responses include confirmation message and updated Lamport timestamp.
   - Write basic unit test mocking a request to verify log output and delayed response.

6. **Client Node Architecture**
   - Design client CLI (`client/main.py`) accepting `--id`, `--port`, `--server`, and peer list (`--clients`).
   - Instantiate both gRPC server (for MutualExclusionService) and client stubs (for printer & peers).
   - Maintain internal state: Lamport clock, request queue, outstanding replies.
   - Provide status reporting (e.g. periodic console prints of queue state).

7. **Ricart-Agrawala Logic**
   - Implement request handling: on local print request, increment clock, broadcast `AccessRequest` to peers, enqueue self.
   - Handle incoming `AccessRequest`: compare Lamport timestamps, decide immediate reply vs deferral.
   - Implement `ReleaseAccess` broadcasting after print completion and draining deferred replies.
   - Document algorithm decisions in code comments referencing RA paper.

8. **Printing Workflow**
   - Develop automatic job generation with random intervals (configurable range via CLI).
   - Before contacting printer, ensure mutual exclusion granted; after completion, log confirmation and release access.
   - Handle RPC errors/timeouts with retries and fallback logging.

9. **Testing Strategy**
   - Unit tests: Lamport clock operations, comparison logic for RA, serialization helpers.
   - Integration tests: spin up in-process gRPC server(s) to validate full RA flow for 2–3 clients.
   - Manual tests: documented scripts to launch server + 3 clients (ports 50051–50054) verifying concurrent access ordering.
   - Include logging verification to ensure timestamps monotonicity.

10. **Operational Scripts & Documentation**
    - Provide shell scripts in `scripts/` to run printer and N clients (e.g. `run_server.sh`, `run_client.sh`).
    - Compose `docs/execution.md` detailing step-by-step execution, parameters, and expected outputs.
    - Prepare final report outline covering architecture, algorithm analysis, testing results, and lessons learned (per instructions).
    - Validate everything on clean checkout using documented commands, update README with final instructions, and ensure deadline compliance.

