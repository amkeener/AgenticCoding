# Bug Planning

Create a new plan in specs/*.md to resolve the `Bug` using the exact specified markdown `Plan Format`. Follow the `Instructions` to create the plan use the `Relevant Files` to focus on the right files.

## CRITICAL WORKFLOW ENFORCEMENT

**YOU MUST FOLLOW THIS EXACT WORKFLOW - NO EXCEPTIONS:**

1. **READ THIS FILE FIRST** - Understand the complete workflow before starting
2. **ONLY CREATE THE PLAN** - Write the plan document in `specs/*.md`. DO NOT make any code changes.
3. **WAIT FOR APPROVAL** - After creating the plan, present it and wait for explicit user approval to implement
4. **DO NOT IMPLEMENT** - Implementation happens via `/implement <plan>` command, NOT in this step

**VIOLATION CHECKLIST - Before proceeding, verify:**
- [ ] I have read and understood this entire command file
- [ ] I will ONLY create a plan document in `specs/*.md`
- [ ] I will NOT modify any code files
- [ ] I will NOT run any implementation commands
- [ ] I will present the plan and wait for user approval
- [ ] I understand implementation happens via `/implement` command

**IF YOU START IMPLEMENTING WITHOUT CREATING THE PLAN FIRST, YOU ARE VIOLATING THE WORKFLOW.**

## Instructions

- You're writing a plan to resolve a bug, it should be thorough and precise so we fix the root cause and prevent regressions.
- **ONLY CREATE THE PLAN** - Create the plan in the `specs/*.md` file. Name it appropriately based on the `Bug`.
- **DO NOT IMPLEMENT** - Do not make any code changes. Do not run implementation commands. Only create the plan document.
- Use the plan format below to create the plan. 
- Research the codebase to understand the bug, reproduce it, and put together a plan to fix it.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to fix the bug.
- Use your reasoning model: THINK HARD about the bug, its root cause, and the steps to fix it properly.
- IMPORTANT: Be surgical with your bug fix, solve the bug at hand and don't fall off track.
- IMPORTANT: We want the minimal number of changes that will fix and address the bug.
- Don't use decorators. Keep it simple.
- If you need a new library, use `uv add` and be sure to report it in the `Notes` section of the `Plan Format`.
- Respect requested files in the `Relevant Files` section.
- Start your research by reading the `README.md` file.
- **After creating the plan, present it to the user and wait for explicit approval before any implementation.**

## Relevant Files

Focus on the following files:
- `README.md` - Contains the project overview and instructions.
- `app/**` - Contains the codebase client/server.
- `scripts/**` - Contains the scripts to start and stop the server + client.

Ignore all other files in the codebase.

## Plan Format

```md
# Bug: <bug name>

## Bug Description
<describe the bug in detail, including symptoms and expected vs actual behavior>

## Problem Statement
<clearly define the specific problem that needs to be solved>

## Solution Statement
<describe the proposed solution approach to fix the bug>

## Steps to Reproduce
<list exact steps to reproduce the bug>

## Root Cause Analysis
<analyze and explain the root cause of the bug>

## Relevant Files
Use these files to fix the bug:

<find and list the files that are relevant to the bug describe why they are relevant in bullet points. If there are new files that need to be created to fix the bug, list them in an h3 'New Files' section.>

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

<list step by step tasks as h3 headers plus bullet points. use as many h3 headers as needed to fix the bug. Order matters, start with the foundational shared changes required to fix the bug then move on to the specific changes required to fix the bug. Include tests that will validate the bug is fixed with zero regressions. Your last step should be running the `Validation Commands` to validate the bug is fixed with zero regressions.>

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

<list commands you'll use to validate with 100% confidence the bug is fixed with zero regressions. every command must execute without errors so be specific about what you want to run to validate the bug is fixed with zero regressions. Include commands to reproduce the bug before and after the fix.>
- `cd app/server && uv run pytest` - Run server tests to validate the bug is fixed with zero regressions

## Notes
<optionally list any additional notes or context that are relevant to the bug that will be helpful to the developer>
```

## Bug
$ARGUMENTS

