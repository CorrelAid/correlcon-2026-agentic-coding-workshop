/**
 * Guardrail hooks for data protection & code quality.
 *
 * Hooks run deterministically – unlike instructions in AGENTS.md, which the model
 * may ignore. Rule of thumb: what must ALWAYS hold goes into a hook; what should
 * USUALLY hold goes into AGENTS.md.
 *
 * 1. tool.execute.before – blocks access to secrets (.env) and raw data (data/raw/),
 *    so their contents are never sent to the LLM.
 * 2. shell.env           – removes the API keys from the environment of shell commands
 *    run by the agent (no `echo $LLM_API_KEY`).
 * 3. tool.execute.after  – runs ruff after every change to a .py file and appends the
 *    result to the tool output: the agent sees lint errors immediately and fixes them
 *    itself (feedback loop).
 */
import type { Plugin } from "@opencode-ai/plugin"

// Paths whose CONTENT must never reach the model.
const BLOCKED_PATHS: RegExp[] = [
  /(^|[\/\s"'])\.env($|[\s"'])/, // .env (but not .env.example)
  /(^|[\/\s"'])data\/raw(\/|$|[\s"'])/, // raw data, may contain personal data
  /(^|[\/\s"'])data\/interim(\/|$|[\s"'])/, // steps 1–2, may still contain personal data
]

// Shell commands that could print secrets.
const BLOCKED_COMMANDS: RegExp[] = [/\bprintenv\b/, /^\s*env\s*$/, /\$\{?(LLM|IONOS)_API_KEY/]

const SECRET_ENV_VARS = ["LLM_API_KEY", "IONOS_API_KEY"]

function blockedReason(text: string): string | undefined {
  for (const re of BLOCKED_PATHS) {
    if (re.test(text)) {
      return (
        `Access denied (privacy hook): "${text}". ` +
        "Raw/interim data (data/raw/, data/interim/) and .env must not be sent to the model. " +
        "Work with pseudonymised data in data/processed/ or write code that " +
        "processes the data locally without reading it yourself."
      )
    }
  }
  return undefined
}

export const Guardrails: Plugin = async ({ $ }) => {
  return {
    "tool.execute.before": async (input, output) => {
      const args = output.args ?? {}

      if (input.tool === "bash") {
        const cmd = String(args.command ?? "")
        // Running code that processes raw data LOCALLY is allowed
        // (e.g. `uv run python -m project.pseudonymise`). Only printing the
        // files directly is blocked.
        const printsFile = /\b(cat|head|tail|less|more|grep|rg|awk|sed|strings|xxd|od|base64|cp|scp|curl)\b/.test(cmd)
        const reason = printsFile ? blockedReason(cmd) : undefined
        if (reason) throw new Error(reason)
        if (BLOCKED_COMMANDS.some((re) => re.test(cmd))) {
          throw new Error("Command blocked (privacy hook): could print secrets.")
        }
        return
      }

      for (const key of ["filePath", "path", "pattern", "include"]) {
        const value = args[key]
        if (typeof value !== "string") continue
        const reason = blockedReason(value)
        if (reason) throw new Error(reason)
      }
    },

    "shell.env": async (_input, output) => {
      for (const name of SECRET_ENV_VARS) output.env[name] = ""
    },

    "tool.execute.after": async (input, output) => {
      if (!["edit", "write"].includes(input.tool)) return
      const file = String(input.args?.filePath ?? "")
      if (!file.endsWith(".py")) return

      await $`uv run ruff format ${file}`.quiet().nothrow()
      const lint = await $`uv run ruff check --fix ${file}`.quiet().nothrow()
      const text = lint.stdout.toString().trim()
      if (lint.exitCode !== 0 && text) {
        output.output += `\n\n[ruff hook] Please fix these lint errors:\n${text}`
      }
    },
  }
}
