# Dremio MCP Server Test Suite

## Overview

This document outlines the complete test suite for the Dremio MCP (Model Context Protocol) server.
The server provides tools to interact with a Dremio data lakehouse containing horticultural/flower production data.

This test suite can be executed by humans and ai agents.

## Server Configuration

- **URL**: `http://localhost:7910/mcp/`
- **VS Code Setting**: `"mcp"."servers"."local dremio with supergateway"`

If there are more Dremio MCP servers, prompt the user for which one to use,
use the one above as default.

Verify that you can access to selected MCP server.
Let the user know which tools the selected server provides you,
and what its system prompt is.

## Test Categories

### 1. SQL Query Tool Tests (`RunSqlQuery`)

#### Basic Connectivity Test

```sql
SELECT "count"(*) as total_products FROM Productie.producten
```

**Expected Result**: 237 total products

#### Schema Discovery Tests

```sql
-- Get all non-system schemas
SELECT DISTINCT table_schema FROM information_schema."tables" 
WHERE table_type != 'SYSTEM_TABLE' ORDER BY table_schema
```

**Expected Schemas (6 total)**:

- `Productie`
- `Productie.Controle`
- `Productie.Oppotten`
- `Vines`
- `minio.productie`
- `minio.productie.oppotten`

#### Table Discovery Test

```sql
-- Get all tables and views
SELECT table_schema, table_name, table_type FROM information_schema."tables" 
WHERE table_type != 'SYSTEM_TABLE' ORDER BY table_schema, table_name
```

**Expected Tables/Views (9 total)**:

- **5 Views**: `producten`, `registratie_controle`, `bollen_pick_lijst`, `oppotlijst`, `products`
- **4 Parquet Tables**: Raw data files in MinIO storage

#### Product Groups Analysis Test

```sql
-- Get product group distribution
SELECT DISTINCT productgroep_code, productgroep_naam, "count"(*) as product_count 
FROM Productie.producten 
WHERE productgroep_naam IS NOT NULL 
GROUP BY productgroep_code, productgroep_naam ORDER BY productgroep_code
```
**Expected Product Groups (14 total)**:
| Code | Group Name | Count |
|------|------------|-------|
| 109 | sixpack aziaat | 15 |
| 112 | 12 aziaat | 5 |
| 113 | 13 aziaat | 50 |
| 117 | 17 aziaat | 17 |
| 119 | 19 aziaat | 27 |
| 213 | 13 oriëntal | 28 |
| 217 | 17 oriëntal | 8 |
| 219 | 19 oriëntal | 39 |
| 224 | 24 oriëntal | 11 |
| 319 | 19 sensations | 7 |
| 419 | 19 longiflorum | 2 |
| 600 | snij lelies | 12 |


### 2. System Table Discovery Test (`GetUsefulSystemTableNames`)

**Expected Response**:
```json
{
  "table_name": "information_schema.\"tables\"",
  "description": "Information about tables in this cluster. Be sure to filter out SYSTEM_TABLE for looking at user tables. You must encapsulate TABLES in double quotes."
}
```

### 3. Schema Information Test (`GetSchemaOfTable`)

**Test Table**: `Productie.producten`

**Expected Response Structure**:
```json
{
  "entityType": "dataset",
  "id": "2fc91c47-e65a-4f9f-9e39-304be5632057",
  "type": "VIRTUAL_DATASET",
  "path": "Productie.producten",
  "createdAt": "2025-04-29T08:53:52.902Z",
  "tag": "73x5wUOEQDM=",
  "fields": "code: INTEGER\nnaam: VARCHAR\nactief: INTEGER\nproductgroep_code: INTEGER\nproductgroep_naam: VARCHAR",
  "tags": [
    "vine",
    "experimental"
  ],
  "description": "Alle producten die we kunnen maken op onze kwekerij.\n\n"
}
```

**Current Status**: ❌ Validation error - server returning dict instead of list

### 4. Description Test (`GetDescriptionOfTableOrSchema`)

#### Test Schema: `Productie`

**Expected Response**: Empty object `{}` (no description configured)

#### Test Table: `Productie.producten`

**Expected Response**:

```json
{
  "\"Productie\".\"producten\"": {
    "description": "Alle producten die we kunnen maken op onze kwekerij.\n\n",
    "tags": [
      "vine",
      "experimental"
    ]
  }
}
```

### 5. Lineage Test (`GetTableOrViewLineage`)

**Test Table**: `Productie.producten`

**Known Issue**: Returns 404 error - API endpoint configuration issue

## Expected Response Format

All successful queries should return responses in this format:
```json
{
  "rows": [...],
  "columns": [...],
  "row_count": number,
  "dtypes": {...}
}
```

## Common Error Patterns to Watch For

1. **"The user cancelled the tool call"** - Connection/timeout issues
2. **"acceptResponseProgress: Adding progress to a completed response"** - Server response handling bug
3. **"MCP server has stopped"** - Server not running
4. **"Method not found: tools/call"** - Missing MCP protocol handler
5. **"401 Unauthorized"** - Authentication/permission issues

## Quick Test Command Sequence

To run the complete test suite, execute these MCP tool calls in sequence:

1. `mcp_local_dremio__RunSqlQuery` - Basic connectivity
2. `mcp_local_dremio__RunSqlQuery` - Schema discovery
3. `mcp_local_dremio__RunSqlQuery` - Table discovery  
4. `mcp_local_dremio__RunSqlQuery` - Product groups analysis
5. `mcp_local_dremio__GetUsefulSystemTableNames` - System tables
6. `mcp_local_dremio__GetSchemaOfTable` - Schema information
7. `mcp_local_dremio__GetDescriptionOfTableOrSchema` - Description tests
8. `mcp_local_dremio__GetTableOrViewLineage` - Lineage test

## Test Success Criteria

✅ **Core SQL tests pass**:

- All SQL queries execute without errors
- Response format includes proper JSON structure
- Data counts match expected values
- No authentication or protocol errors

❌ **Known Issues**:

- Some tools have MCP validation errors (server returns dict instead of list)
- Lineage API returns 404 (endpoint configuration issue)

## Current Test Status (July 9, 2025)

### ✅ PASSING (5/8 tests):
1. ✅ Basic Connectivity Test - 237 products found
2. ✅ Schema Discovery Test - All 6 expected schemas found  
3. ✅ Table Discovery Test - 9 tables/views found (5 views + 4 parquet tables)
4. ✅ Product Groups Analysis Test - All 14 product groups with correct counts
5. ✅ Description Test (Table) - Returns description and tags for `Productie.producten`

### ❌ FAILING (3/8 tests):
1. ❌ System Table Discovery Test - Validation error (server returning dict instead of list)
2. ❌ Schema Information Test - Validation error (server returning dict instead of list)  
3. ❌ Lineage Test - 404 error (known API endpoint issue)

## Troubleshooting

If tests fail:

1. Check if server is running on `localhost:8000`
2. Verify MCP protocol implementation
3. Check server logs for specific error messages
4. Ensure proper authentication configuration
5. Validate response formatting in server code

---

## Bug Reports

### Bug #1: MCP Protocol Validation Error (Tools 3 & 4)

**Affected Tools:**
- `mcp_local_dremio__GetUsefulSystemTableNames`
- `mcp_local_dremio__GetSchemaOfTable`

**Issue:** MCP validation error - server returning dict when list expected

**Error Message:**
```
1 validation error for invokeOutput
result
  Input should be a valid list [type=list_type, input_value={...}, input_type=dict]
```

**Root Cause:** The MCP server is returning JSON objects (`{}`) but the MCP protocol expects arrays (`[]`) for these tool responses.

**Impact:** Tools fail with validation errors despite containing correct data.

**Fix Required:** Update server response formatting to wrap results in arrays or adjust MCP tool definitions to expect objects.

---

### Bug #2: Lineage API Endpoint Not Found

**Affected Tool:** `mcp_local_dremio__GetTableOrViewLineage`

**Issue:** API endpoint returns 404 Not Found

**Error Message:**
```
404, message='Not Found', url='https://dremio.dev.serraict.me/api/v3/catalog/2fc91c47-e65a-4f9f-9e39-304be5632057/graph'
```

**Root Cause:** Dremio API endpoint `/api/v3/catalog/{id}/graph` is not available or not configured on this instance.

**Impact:** Lineage functionality completely unavailable.

**Fix Required:** 
1. Verify Dremio version supports lineage API
2. Check if lineage feature is enabled in Dremio configuration
3. Validate API endpoint URL construction

---

*Last Updated: July 9, 2025*
*Server Status: ⚠️ Core SQL tests passing, some MCP validation issues remain*
