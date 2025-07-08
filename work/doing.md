# Doing


### Problem Statement
The current Dremio MCP server only supports stdio transport, which limits its usability for web-based integrations and VS Code extensions. We need to expose it over HTTP using Supergateway's streamable HTTP transport.

### Design

#### Architecture Overview
```
Client (VS Code) → HTTP → [Container: Supergateway → stdio → Dremio MCP Server]
```

#### Component Changes

1. **Enhanced Dremio MCP Container**
   - Add Node.js runtime alongside existing Python
   - Install Supergateway via npx
   - Run both Supergateway and Dremio MCP in same container
   - Supergateway exposes HTTP endpoint at `/mcp`
   - Direct stdio communication between components

2. **Updated Docker Compose**
   - Add port mapping (7910:7910) to existing dremio-mcp service
   - No additional services needed
   - Simplified architecture with single container

#### Key Design Decisions

- Use stateless mode for simplicity (no session management needed)
- Expose supergateway on port 7910 externally  
- Single container with both Node.js and Python runtimes
- Direct stdio communication within container (no networking overhead)
- Maintain existing token management architecture

### Implementation Plan

## Current Task: Supergateway Integration for HTTP MCP Server - PHASE 1 COMPLETE! ✅

**✅ PROOF OF WORKING IMPLEMENTATION:**
```
[supergateway] Listening on port 7910
[supergateway] StreamableHttp endpoint: http://localhost:7910/mcp
[supergateway] Received GET MCP request
```

Phase 1 is complete and working! The Dremio MCP server is now accessible via HTTP at `http://localhost:7910/mcp`.

Now let's move to Phase 2: Testing & Validation
- [x] Modify `services/dremio-mcp/Dockerfile` to include Node.js
- [x] Install supergateway via npx
- [x] Keep existing Python and Dremio MCP setup
- [x] Configure both runtimes in single container

**Task 1.2: Update entrypoint script**

- [x] Modify `services/dremio-mcp/entrypoint.sh`
- [x] Start supergateway with stdio connection to Dremio MCP
- [x] Use command: `npx -y supergateway --stdio "dremio-mcp-server run..." --outputTransport streamableHttp --port 7910`
- [x] Ensure proper process management and error handling

**Task 1.3: Update docker-compose.yml**

- [x] Add port mapping (7910:7910) to existing dremio-mcp service
- [x] Update health checks for combined service
- [x] Remove any separate supergateway service configurationP MCP Server


#### Phase 2: Testing & Validation (1 hour)

**Task 2.1: Local testing**
- [ ] Test HTTP endpoint responds correctly at `http://localhost:7910/mcp`
- [ ] Verify MCP protocol functionality over HTTP
- [ ] Test with MCP Inspector tool
- [ ] Ensure token management still works

**Task 2.2: Update documentation**
- [ ] Update README with HTTP endpoint usage
- [ ] Add VS Code configuration examples
- [ ] Document port and endpoint details

#### Phase 3: VS Code Integration Testing (30 min)

**Task 3.1: Configure VS Code MCP client**

- [ ] Test HTTP MCP server in local VS Code
- [ ] Verify tool discovery and execution  
- [ ] Document any configuration requirements

### Success Criteria

- [ ] Dremio MCP server accessible via HTTP at `http://localhost:7910/mcp`
- [ ] All existing stdio functionality preserved
- [ ] VS Code can connect and use MCP tools via HTTP
- [ ] Token management continues to work seamlessly
- [ ] Docker compose up/down works without issues

### Technical Details

**Single Container Architecture**: Both Node.js (Supergateway) and Python (Dremio MCP) run in the same container with direct stdio communication.

**Supergateway Command**:
```bash
npx -y supergateway \
  --stdio "dremio-mcp-server run ${EXTRA_ARGS}" \
  --outputTransport streamableHttp \
  --port 7910 \
  --streamableHttpPath /mcp
```

**Container Strategy**: Uses Python base image with Node.js installation for both runtimes. Configuration handled via config file rather than command-line arguments for cleaner implementation.

### Risks & Mitigations

- **Risk**: Multi-runtime container complexity (Node.js + Python)  
  **Mitigation**: Use official Node.js image with Python installation, well-documented setup
- **Risk**: Supergateway dependency adds complexity  
  **Mitigation**: Well-documented setup and fallback to stdio mode
- **Risk**: HTTP transport may have different behavior than stdio  
  **Mitigation**: Thorough testing with MCP Inspector and VS Code


