# Dremio MCP Server Test Suite

## Overview

This document outlines the complete test suite for the Dremio MCP (Model Context Protocol) server.
The server provides tools to interact with a Dremio Community Edition instance containing sample datasets.

This test suite can be executed by humans and AI agents.

## Server Configuration

- **URL**: `http://localhost:7910/mcp/`
- **VS Code Setting**: `"mcp"."servers"."dremio-local"`

If there are more Dremio MCP servers, prompt the user for which one to use,
use the one above as default.

Verify that you can access the selected MCP server.
Let the user know which tools the selected server provides you,
and what its system prompt is.

## Test Categories

### 1. SQL Query Tool Tests (`RunSqlQuery`)

#### Basic Connectivity Test

```sql
SELECT 1 as test_connection
```

**Expected Result**: 
```json
{
  "results": [
    {
      "test_connection": 1
    }
  ]
}
```

#### Schema Discovery Test

```sql
SELECT * FROM INFORMATION_SCHEMA.SCHEMATA LIMIT 10
```

**Expected Schemas**: Should include:
- `$scratch`
- `@admin` (or `@bot` depending on user)
- `INFORMATION_SCHEMA`
- `Samples`
- `sys`

#### Sample Data Connectivity Test

```sql
SELECT * FROM Samples."samples.dremio.com"."NYC-weather.csv" LIMIT 5
```

**Expected Result**: NYC weather data with columns:
- `station`: Weather station ID (e.g., "USW00094728")
- `name`: Station name (e.g., "NY CITY CENTRAL PARK, NY US")
- `date`: Date in format "2009-01-01T00:00"
- `awnd`: Average wind speed
- `prcp`: Precipitation
- `snow`: Snowfall
- `snwd`: Snow depth
- `tempmax`: Maximum temperature
- `tempmin`: Minimum temperature

#### Data Analysis Test

```sql
SELECT COUNT(*) as total_records FROM Samples."samples.dremio.com"."NYC-weather.csv"
```

**Expected Result**: 3,833 total records

#### Sample Data Exploration Test

```sql
SELECT 
  MIN(tempmax) as min_temp_max,
  MAX(tempmax) as max_temp_max,
  AVG(CAST(tempmax AS DOUBLE)) as avg_temp_max
FROM Samples."samples.dremio.com"."NYC-weather.csv" 
WHERE tempmax IS NOT NULL
```

**Expected Result**: Temperature statistics showing reasonable NYC weather data


### 2. System Table Discovery Test (`GetUsefulSystemTableNames`)

**Expected Response**:
```json
{
  "information_schema.\"tables\"": {
    "description": "Information about tables in this cluster. Be sure to filter out SYSTEM_TABLE for looking at user tables. You must encapsulate TABLES in double quotes."
  }
}
```

**Note**: Currently has validation issues but provides useful information.

### 3. Schema Information Test (`GetSchemaOfTable`)

**Test Table**: `Samples`

**Expected Response**: Information about the Samples data source including available datasets.

**Note**: Currently has validation issues (server returns dict instead of list).

### 4. Description Test (`GetDescriptionOfTableOrSchema`)

#### Test Schema: `Samples`

**Test**: Get description of the Samples schema

#### Test Table: `Samples."samples.dremio.com"."NYC-weather.csv"`

**Test**: Get description of the NYC weather dataset

### 5. Lineage Test (`GetTableOrViewLineage`)

**Test Table**: `Samples."samples.dremio.com"."NYC-weather.csv"`

**Note**: May have limited lineage information for sample datasets.

## Expected Response Format

All successful SQL queries should return responses in this format:
```json
{
  "results": [
    {
      "column1": "value1",
      "column2": "value2"
    }
  ]
}
```

## Quick Test Command Sequence

To run the complete test suite, execute these MCP tool calls in sequence:

1. `mcp_local_dremio__RunSqlQuery` - Basic connectivity test
2. `mcp_local_dremio__RunSqlQuery` - Schema discovery
3. `mcp_local_dremio__RunSqlQuery` - Sample data connectivity
4. `mcp_local_dremio__RunSqlQuery` - Data analysis (record count)
5. `mcp_local_dremio__RunSqlQuery` - Sample data exploration (temperature stats)
6. `mcp_local_dremio__GetUsefulSystemTableNames` - System tables
7. `mcp_local_dremio__GetSchemaOfTable` - Schema information
8. `mcp_local_dremio__GetDescriptionOfTableOrSchema` - Description tests

## Test Success Criteria

✅ **Core functionality working**:
- Basic SQL connectivity established
- Sample data accessible and queryable
- NYC weather dataset contains expected 3,833 records
- Temperature data analysis produces reasonable results
- No authentication or connection errors

## Current Test Status (July 10, 2025)

### ✅ CONFIRMED WORKING

1. ✅ Basic Connectivity Test - Simple queries execute successfully
2. ✅ Sample Data Access - NYC weather data accessible with 3,833 records
3. ✅ Data Analysis - Can count records and analyze temperature data
4. ✅ Schema Discovery - Can list available schemas including Samples
5. ✅ System Table Discovery - Returns system table names (validation issues are non-blocking)
6. ✅ Schema Information - Returns table schema details (validation issues are non-blocking)
7. ✅ Record Count & Statistics - Can count records and compute temperature statistics

### ⚠️ PARTIALLY WORKING

1. ⚠️ Description functionality - Tool exists but may have validation issues with sample data
2. ⚠️ Lineage functionality - Tool exists but may have validation issues with sample data
3. ⚠️ MCP Protocol Validation - Some tools return dict vs list format issues (functionality works)

### ✅ CORE FUNCTIONALITY VALIDATED

**All essential MCP-SQL operations confirmed working:**

- SQL query execution via MCP
- Schema and table discovery
- Sample data access and analysis
- System table enumeration
- Statistical computations

Demo is fully functional for its intended purpose.

## Sample Queries for Testing

### Basic Data Exploration

```sql
-- Get weather station information
SELECT DISTINCT station, name FROM Samples."samples.dremio.com"."NYC-weather.csv" LIMIT 5;

-- Get date range of data
SELECT MIN(date) as earliest_date, MAX(date) as latest_date 
FROM Samples."samples.dremio.com"."NYC-weather.csv";

-- Get records with snow
SELECT * FROM Samples."samples.dremio.com"."NYC-weather.csv" 
WHERE CAST(snow AS DOUBLE) > 0 LIMIT 5;
```

### Advanced Analysis

```sql
-- Monthly temperature averages
SELECT 
  EXTRACT(YEAR FROM CAST(date AS TIMESTAMP)) as year,
  EXTRACT(MONTH FROM CAST(date AS TIMESTAMP)) as month,
  AVG(CAST(tempmax AS DOUBLE)) as avg_max_temp,
  AVG(CAST(tempmin AS DOUBLE)) as avg_min_temp
FROM Samples."samples.dremio.com"."NYC-weather.csv"
WHERE tempmax IS NOT NULL AND tempmin IS NOT NULL
GROUP BY EXTRACT(YEAR FROM CAST(date AS TIMESTAMP)), EXTRACT(MONTH FROM CAST(date AS TIMESTAMP))
ORDER BY year, month
LIMIT 10;
```

## Troubleshooting

If tests fail:

1. **Check Docker services**: `docker compose ps`
2. **Verify Dremio is healthy**: Access <http://localhost:9047>
3. **Check MCP server logs**: `docker compose logs dremio-mcp`
4. **Verify token refresh**: `docker compose logs token-refresher`
5. **Test MCP endpoint**: Ensure VS Code MCP configuration is correct

---

*Last Updated: July 10, 2025*
*Server Status: ✅ Core SQL functionality confirmed working with Dremio sample data*
