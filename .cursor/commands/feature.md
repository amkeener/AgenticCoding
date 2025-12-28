# Feature Planning

Create a new plan in specs/*.md to implement the `Feature` using the exact specified markdown `Plan Format`. Follow the `Instructions` to create the plan use the `Relevant Files` to focus on the right files.

## CRITICAL WORKFLOW ENFORCEMENT

**YOU MUST FOLLOW THIS EXACT WORKFLOW - NO EXCEPTIONS:**

1. **READ THIS FILE FIRST** - Understand the complete workflow before starting
2. **RESEARCH PHASE** - Thoroughly research and understand the codebase architecture, patterns, and existing implementations BEFORE planning
3. **PLANNING PHASE** - Only AFTER research is complete, create the plan document in `specs/*.md`. DO NOT make any code changes.
4. **WAIT FOR APPROVAL** - After creating the plan, present it and wait for explicit user approval to implement
5. **DO NOT IMPLEMENT** - Implementation happens via `/implement <plan>` command, NOT in this step

**VIOLATION CHECKLIST - Before proceeding, verify:**
- [ ] I have read and understood this entire command file
- [ ] I will conduct thorough research BEFORE creating the plan
- [ ] I will understand existing patterns, architecture, and code structure
- [ ] I will ONLY create a plan document in `specs/*.md` after research is complete
- [ ] I will NOT modify any code files
- [ ] I will NOT run any implementation commands
- [ ] I will present the plan and wait for user approval
- [ ] I understand implementation happens via `/implement` command

**IF YOU START IMPLEMENTING OR CREATE A PLAN WITHOUT THOROUGH RESEARCH FIRST, YOU ARE VIOLATING THE WORKFLOW.**

## Instructions

### PHASE 1: RESEARCH (MANDATORY - DO THIS FIRST)

**BEFORE writing any plan, you MUST conduct thorough research:**

1. **Read the README.md** - Understand the project structure, purpose, and conventions
2. **Explore the codebase architecture** - Understand how the application is structured:
   - How does the frontend communicate with the backend?
   - What are the existing API patterns and endpoints?
   - How is data stored and managed?
   - What are the existing UI/UX patterns?
3. **Identify similar features** - Find existing features that are similar to what you're planning:
   - How are they implemented?
   - What patterns do they follow?
   - What can you learn from them?
4. **Understand dependencies** - Identify what libraries, frameworks, and tools are used
5. **Map the data flow** - Understand how data flows through the application
6. **Identify integration points** - Understand where your feature will integrate with existing code

**Research Checklist:**
- [ ] Read README.md completely
- [ ] Explored server-side code structure and patterns
- [ ] Explored client-side code structure and patterns
- [ ] Identified similar features and their implementation patterns
- [ ] Understood database schema and data models
- [ ] Understood API endpoints and request/response patterns
- [ ] Understood UI components and styling patterns
- [ ] Identified all files that will need to be modified or created

### PHASE 2: PLANNING (ONLY AFTER RESEARCH IS COMPLETE)

- You're writing a plan to implement a net new feature that will add value to the application.
- **ONLY CREATE THE PLAN** - Create the plan in the `specs/*.md` file. Name it appropriately based on the `Feature`.
- **DO NOT IMPLEMENT** - Do not make any code changes. Do not run implementation commands. Only create the plan document.
- Use the `Plan Format` below to create the plan. 
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to implement the feature successfully.
- Use your reasoning model: THINK HARD about the feature requirements, design, and implementation approach based on your research.
- Follow existing patterns and conventions you discovered during research. Don't reinvent the wheel.
- Design for extensibility and maintainability.
- If you need a new library, use `uv add` and be sure to report it in the `Notes` section of the `Plan Format`.
- Respect requested files in the `Relevant Files` section.
- **After creating the plan, present it to the user and wait for explicit approval before any implementation.**

## Relevant Files

**During your RESEARCH phase, focus on understanding these areas:**

### Core Documentation
- `README.md` - Contains the project overview, architecture, and instructions. **READ THIS FIRST.**

### Server-Side Code
- `app/server/**` - Contains the codebase server:
  - `server.py` - Main FastAPI application and routes
  - `core/data_models.py` - Pydantic models for request/response
  - `core/*.py` - Core business logic modules
  - `tests/**` - Test patterns and examples

### Client-Side Code
- `app/client/**` - Contains the codebase client:
  - `src/main.ts` - Main application logic
  - `src/api/client.ts` - API client patterns
  - `index.html` - HTML structure
  - `src/style.css` - Styling patterns

### Scripts
- `scripts/**` - Contains the scripts to start and stop the server + client.

**Research these files to understand patterns before planning. Ignore all other files in the codebase.**

## Plan Format

**IMPORTANT: Only use this format AFTER completing your research phase. The plan should reflect deep understanding of the codebase.**

```md
# Feature: <feature name>

## Research Summary
<briefly summarize what you learned during research phase:
- Key architectural patterns discovered
- Similar features and how they're implemented
- Integration points identified
- Files that will be affected
- Dependencies and libraries used>

## Feature Description
<describe the feature in detail, including its purpose and value to users>

## User Story
As a <type of user>
I want to <action/goal>
So that <benefit/value>

## Problem Statement
<clearly define the specific problem or opportunity this feature addresses>

## Solution Statement
<describe the proposed solution approach and how it solves the problem>

## Relevant Files
Use these files to implement the feature:

<find and list the files that are relevant to the feature describe why they are relevant in bullet points. If there are new files that need to be created to implement the feature, list them in an h3 'New Files' section.>

## Implementation Plan
### Phase 1: Foundation
<describe the foundational work needed before implementing the main feature>

### Phase 2: Core Implementation
<describe the main implementation work for the feature>

### Phase 3: Integration
<describe how the feature will integrate with existing functionality>

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

<list step by step tasks as h3 headers plus bullet points. use as many h3 headers as needed to implement the feature. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include creating tests throughout the implementation process. Your last step should be running the `Validation Commands` to validate the feature works correctly with zero regressions.>

## Testing Strategy
### Unit Tests
<describe unit tests needed for the feature>

### Integration Tests
<describe integration tests needed for the feature>

### Edge Cases
<list edge cases that need to be tested>

## Acceptance Criteria
<list specific, measurable criteria that must be met for the feature to be considered complete>

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

<list commands you'll use to validate with 100% confidence the feature is implemented correctly with zero regressions. every command must execute without errors so be specific about what you want to run to validate the feature works as expected. Include commands to test the feature end-to-end.>
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions

## Notes
<optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the developer>
```

## Feature
$ARGUMENTS

