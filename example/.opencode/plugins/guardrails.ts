/**
 * Guardrail hooks for OpenCode 2 – data protection & code quality.
 *
 * Most hard rules live declaratively in opencode.json (`policies`): no other provider,
 * no reading .env / data/raw / data/interim, not even via the shell. This plugin adds what
 * policies cannot express:
 *
 * 1. execute.before – also blocks tools whose *path* argument points into protected data
 *    (glob/grep search paths), with a message that tells the agent what to do instead.
 * 2. shell create.before – removes the API keys from the agent's shell environment.
 * 3. execute.after – runs ruff after every edit of a .py file and appends the lint result
 *    to the tool output, so the agent sees and fixes errors itself (feedback loop).
 */
import { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"

const PROTECTED = [/(^|[\/\s"'])\.env($|[\s"'])/, /(^|[\/\s"'])data\/(raw|interim)(\/|$|[\s"'])/]
const SECRET_ENV_VARS = ["LLM_API_KEY", "IONOS_API_KEY"]
const MESSAGE =
  "Access denied (privacy hook): raw/interim data (data/raw/, data/interim/) and .env must " +
  "not be sent to the model. Write code that processes the data locally and prints only counts."

export default Plugin.define({
  id: "correlaid.guardrails",
  async setup(ctx) {
    await ctx.tool.hook("execute.before", (event: any) => {
      const input = event.input ?? {}
      for (const key of ["path", "filePath", "pattern", "include", "workdir"]) {
        const value = input[key]
        if (typeof value === "string" && PROTECTED.some((re) => re.test(value))) {
          throw new Error(MESSAGE)
        }
      }
    })

    await ctx.shell.hook("create.before", (event: any) => {
      for (const name of SECRET_ENV_VARS) event.env[name] = undefined
    })

    await ctx.tool.hook("execute.after", (event: any) => {
      if (event.status !== "completed" || !["edit", "write"].includes(event.tool)) return
      const file = String(event.input?.path ?? event.input?.filePath ?? "")
      if (!file.endsWith(".py")) return
      try {
        execFileSync("uv", ["run", "ruff", "format", file], { stdio: "ignore" })
        execFileSync("uv", ["run", "ruff", "check", "--fix", file], { encoding: "utf8" })
      } catch (err: any) {
        const lint = String(err?.stdout ?? "").trim()
        const content = event.result?.content
        if (lint && Array.isArray(content)) {
          const text = `[ruff hook] Please fix these lint errors:\n${lint}`
          event.result = { ...event.result, content: [...content, { type: "text", text }] }
        }
      }
    })
  },
})
