# Integration Tests

This directory previously contained integration tests for A2A (Agent-to-Agent) agent tools.

**Note**: Integration tests have been removed for now. This directory is kept for future use.

## Previous Test Files

The integration tests (`test_balance_agent_tools.py`) have been removed. They tested:
- `get_balance()` tool function
- `get_token_balance()` tool function
- `get_all_token_balances()` tool function

These tests required the `langchain` dependency which is not currently included in the project dependencies.

## Future

Integration tests may be re-added in the future when:
- `langchain` dependency is added to `requirements.txt`
- A2A agent integration is actively being developed
- There's a need to test the complete tool integration flow
