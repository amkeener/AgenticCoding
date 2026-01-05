#!/usr/bin/env bun

import { query } from "@anthropic-ai/claude-code";

async function main() {
  console.log("🤖 Claude Code TypeScript SDK Hello World!");
  console.log("Starting query with sonnet model...\n");

  try {
    for await (const message of query({
      prompt: "Hello! Please respond with 'Hello from Claude Code TypeScript SDK!' and tell me what the current time is.",
      options: {
        model: "sonnet",
        maxTurns: 2,
        allowedTools: ["Bash"],
        systemPrompt: "You are a helpful assistant. Always provide clear, direct responses to user requests."
      }
    })) {
      if (message.type === "result") {
        console.log("✅ Result received:");
        console.log(message.result || "No result content");
        console.log(`\n📊 Cost: $${message.total_cost_usd}`);
        console.log(`⏱️  Duration: ${message.duration_ms}ms`);
        console.log(`🔄 Turns: ${message.num_turns}`);
        console.log(`🎯 Success: ${message.subtype === "success"}`);
      } else if (message.type === "assistant") {
        console.log("🧠 Assistant thinking...");
      } else if (message.type === "system") {
        console.log("🚀 System initialized");
        console.log(`Session ID: ${message.session_id}`);
        console.log(`Model: ${message.model}`);
      }
    }
  } catch (error) {
    console.error("❌ Error:", error);
    process.exit(1);
  }
}

main().catch(console.error);