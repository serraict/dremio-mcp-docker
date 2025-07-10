# Bootstrap Script for AI Agents

**AI Agent: Read this entire document to guide the user through setting up their Dremio MCP Docker environment.**

This script provides step-by-step instructions for you (the AI agent) to guide a human user through setting up a complete Dremio + MCP environment for data analysis collaboration.

## 🎯 Your Mission

Guide the user through setup so that at the end:

1. Dremio Community Edition is running with sample data
2. MCP server is connected and working
3. You and the user can collaborate on data analysis tasks
4. The user understands how to use the system

## 📋 Prerequisites Check

**First, verify the user has these requirements:**

1. **Docker & Docker Compose installed**
   - Ask them to run: `docker --version` and `docker compose version`
   - Should see version information for both

2. **Required ports available**
   - Ask them to check if ports 9047 and 7910 are free
   - Command: `lsof -i :9047 && lsof -i :7910` (should show nothing if ports are free)

3. **VS Code with MCP support** (or other MCP client)
   - Confirm they have VS Code or another MCP-compatible client

## 🚀 Step-by-Step Setup Guide

### Step 1: Environment Configuration

**Guide the user through:**

If you have the ability to execute commands, do so,
but show everything tho the user
and explain what you are doing.

1. **Copy the environment template:**

   ```bash
   cp .env.example .env
   ```

2. **Explain what they need to configure:**
   - The `.env` file contains credentials for the Dremio admin user
   - Default is `DREMIO_USERNAME=admin` and `DREMIO_PASSWORD=admin123`
   - They can use these defaults or choose their own credentials
   - **Important:** Remember what they choose - they'll need it later!

3. **Let them edit `.env` if desired:**
   - If they want custom credentials, help them edit the file
   - Otherwise, the defaults work fine

4. **Download the required Docker images**

    ```bash
    docker compose pull
    ```

### Step 2: Dremio Initial Setup

**This is crucial - guide them through Dremio web UI setup:**

0. **Start the Dremio service**

    ```bash
    docker compose up dremio -d
    ```

1. **Open Dremio web interface:**
   - URL: http://localhost:9047
   - Tell them to wait 1-2 minutes if it's not ready immediately

2. **First-time setup wizard:**
   - They'll see a setup wizard for first admin user
   - **Important:** They must use the SAME credentials as in their `.env` file
   - If they used defaults: username `admin`, password `admin123`
   - If they customized: use those same credentials

3. **Add sample data source:**
   - After user creation, Dremio may offer sample data sources
   - Guide them to add "Samples" data source if available
   - This provides NYC weather data and other sample datasets

### Step 3: Start the entire stack

**Guide them through starting Docker services:**

1. **Start the remaining services**
   ```bash
   docker compose up -d
   ```

2. **Check service status:**

   ```bash
   docker compose ps
   ```

3. **What to expect:**
   - All three services should show "Up" status
   - Dremio should show "(healthy)" after a minute
   - If any service fails, check logs: `docker compose logs [service-name]`

### Step 4: Validation & Testing

**Verify everything is working:**

1. **Check all services are healthy:**

   ```bash
   docker compose ps
   ```

2. **Check token refresh is working:**

   ```bash
   docker compose logs token-refresher --tail 10
   ```

   - Should see "Token refresh completed successfully"
   - If you see "401 Unauthorized", the credentials don't match between .env and Dremio

3. **Verify MCP server is running:**

   ```bash
   docker compose logs dremio-mcp --tail 10
   ```

   - Should see "Listening on port 7910" and "StreamableHttp endpoint"

### Step 5: MCP Client Configuration

**Help them configure their MCP client (VS Code example):**

1. **Add MCP server to VS Code settings:**
   - Open VS Code settings (JSON format)
   - Add this to the settings:

   ```json
   "mcp": {
     "servers": {
       "dremio-local": {
         "url": "http://localhost:7910/mcp/"
       }
     }
   }
   ```

2. **Restart VS Code** to load the MCP server

### Step 6: Test the Connection

**Validate end-to-end functionality:**

1. **Test basic connection:**
   - Try using MCP tools to query: `SELECT 1 as test`
   - Should return a result

2. **Test sample data:**
   - Query sample data: `SELECT * FROM Samples."samples.dremio.com"."NYC-weather.csv" LIMIT 5`
   - Should return NYC weather data

3. **Celebrate success!** 🎉

## 🔧 Troubleshooting Guide

**Common issues and solutions:**

### Issue: Token refresh fails (401 Unauthorized)

**Solution:** Credentials mismatch between `.env` file and Dremio admin user

- Check `.env` file credentials
- Check what they used when setting up Dremio admin user
- These MUST match exactly
- If needed, recreate admin user or update `.env` file

### Issue: Port already in use

**Solution:**

- Find what's using the port: `lsof -i :9047` or `lsof -i :7910`
- Stop conflicting service or change port in docker-compose.yml

### Issue: MCP server not responding

**Solution:**

- Check if token refresh is working first
- Restart services: `docker compose restart`
- Check logs: `docker compose logs dremio-mcp`

### Issue: Can't access sample data

**Solution:**

- Verify sample data was added in Dremio web UI
- Check exact table path in Dremio UI (under "Samples" source)
- Use proper quoting in SQL queries

## 🎯 Success Criteria

**When setup is complete, confirm these work:**

✅ Dremio web UI accessible at http://localhost:9047  
✅ Can login with admin credentials  
✅ Sample data visible in Dremio  
✅ MCP server responding in VS Code (or client)  
✅ Can query sample data via MCP tools  
✅ Token refresh working automatically  

## 🚀 Ready to Collaborate!

**Once everything is working, guide them to try:**

1. **Explore the data:**
   - "Show me what sample data is available"
   - "What's in the NYC weather dataset?"

2. **Start analysis:**
   - "Help me analyze temperature trends in the weather data"
   - "Create a summary of the weather data"

3. **Learn the system:**
   - "What other data analysis can we do together?"
   - "How does this MCP setup help with data work?"

## 📝 Notes for AI Agents

- **Be patient** - Docker startup can take 1-2 minutes
- **Double-check credentials** - This is the most common issue
- **Test each step** - Don't move forward until current step works
- **Celebrate success** - Make them feel accomplished!
- **Be ready to troubleshoot** - Use the troubleshooting section
- **End goal focus** - Get them ready for data collaboration, not just setup

---

**Remember: Your goal is to get the user from "empty folder" to "ready to collaborate on data analysis" in the smoothest way possible!**
