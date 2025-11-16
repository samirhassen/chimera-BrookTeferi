# Quick Start Guide - Project Chimera

## Prerequisites
- Docker and Docker Compose installed
- Terminal/Command Prompt access

## 5-Minute Setup

1. **Start all services**:
   ```bash
   docker-compose up --build
   ```

2. **Wait 10-15 seconds** for all services to start and register

3. **Test the system** (in a new terminal):
   ```bash
   curl -X POST http://localhost:8080/plan-and-run \
     -H "Content-Type: application/json" \
     -d '{"instruction": "Generate a project intelligence brief: analyze system logs for errors, but ensure all sensitive identifiers are sanitized before analysis, and then produce a summarized report with a visual asset"}'
   ```

4. **View formatted output** in the JSON response under `formatted_output`

## Verify Services

Check that all agents are registered:
```bash
curl http://localhost:8080/agents
```

You should see three agents: `sanitizer`, `log_analyst`, and `report_gen`.

## Stop Services

Press `Ctrl+C` in the terminal running docker-compose, or:
```bash
docker-compose down
```

## Troubleshooting

- **Port already in use**: Stop any services using ports 5001, 5002, 5003, or 8080
- **Agents not registering**: Wait a few more seconds and check logs with `docker-compose logs`
- **Connection errors**: Ensure Docker is running and all containers started successfully

For more details, see [README.md](README.md)

