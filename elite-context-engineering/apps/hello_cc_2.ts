#!/usr/bin/env bun

import { query } from "@anthropic-ai/claude-code";

async function helloClaudeCode() {
  console.log("Starting Claude Code SDK Hello World example...\n");

  try {
    for await (const message of query({
      prompt: "Hello! Please respond with a friendly greeting and tell me what you can help me with.",
      options: {
        model: "sonnet",
        maxTurns: 1,
        systemPrompt: "You are a helpful AI assistant demonstrating the Claude Code TypeScript SDK.",
        allowedTools: []
      }
    })) {
      if (message.type === "system" && message.subtype === "init") {
        console.log(`📋 Session started: ${message.session_id}`);
        console.log(`🤖 Model: ${message.model}`);
        console.log(`🔧 Tools: ${message.tools.length} available`);
        console.log(`🏠 Working directory: ${message.cwd}\n`);
      }

      if (message.type === "result") {
        console.log("🎉 Claude Code Response:");
        console.log(message.result);
        console.log(`\n📊 Usage Stats:`);
        console.log(`- Duration: ${message.duration_ms}ms`);
        console.log(`- Cost: $${message.total_cost_usd.toFixed(6)}`);
        console.log(`- Turns: ${message.num_turns}`);
        console.log(`- Success: ${!message.is_error}`);
      }
    }
  } catch (error) {
    console.error("❌ Error occurred:", error);
    process.exit(1);
  }
}

// Run the hello world example
helloClaudeCode();