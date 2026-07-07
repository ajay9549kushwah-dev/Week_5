# Week 5 Submission

## Overview

This week I extended my Week 4 research agent by adding support for Skills and MCP configuration.

## Features Added

- Skills loader
- MCP configuration loader
- Dynamic skill loading
- Dynamic MCP listing
- /skills command
- /mcp command

## Skills

### Commit Skill

Runs tests, stages files and prepares a git commit.

### Review Skill

Reviews source code before committing.

## MCP

The agent reads MCP server information from config.json.

Currently configured server:

- GitHub MCP

## Testing

I tested:

- Skill discovery
- Skill loading
- MCP configuration loading
- REPL commands
- Existing Week 4 tools

## Example

Prompt:

Create a commit for my project.

The agent loads the Commit Skill and follows the workflow.

## Learning

This week helped me understand how Skills and MCP make an AI agent extensible without modifying its source code.