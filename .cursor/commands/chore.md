# Chore Planning

Create a new plan in specs/*.md to resolve the `Chore` using the exact specified markdown `Plan Format`. Follow the `Instructions` to create the plan use the `Relevant Files` to focus on the right files.

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

- You're writing a plan to resolve a chore, it should be simple but we need to be thorough and precise so we don't miss anything or waste time with any second round of changes.
- **ONLY CREATE THE PLAN** - Create the plan in the `specs/*.md` file. Name it appropriately based on the `Chore`.
- **DO NOT IMPLEMENT** - Do not make any code changes. Do not run implementation commands. Only create the plan document.
- Use the plan format below to create the plan. 
- Research the codebase and put together a plan to accomplish the chore.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to accomplish the chore.
- Use your reasoning model: THINK HARD about the plan and the steps to accomplish the chore.
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
# Chore: <chore name>

## Chore Description
<describe the chore in detail>

## Relevant Files
Use these files to resolve the chore:

<find and list the files that are relevant to the chore describe why they are relevant in bullet points. If there are new files that need to be created to accomplish the chore, list them in an h3 'New Files' section.>

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

<list step by step tasks as h3 headers plus bullet points. use as many h3 headers as needed to accomplish the chore. Order matters, start with the foundational shared changes required to fix the chore then move on to the specific changes required to fix the chore. Your last step should be running the `Validation Commands` to validate the chore is complete with zero regressions.>

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

<list commands you'll use to validate with 100% confidence the chore is complete with zero regressions. every command must execute without errors so be specific about what you want to run to validate the chore is complete with zero regressions. Don't validate with curl commands.>
- `cd app/server && uv run pytest` - Run server tests to validate the chore is complete with zero regressions

## Notes
<optionally list any additional notes or context that are relevant to the chore that will be helpful to the developer>
```

## Chore
$ARGUMENTS
