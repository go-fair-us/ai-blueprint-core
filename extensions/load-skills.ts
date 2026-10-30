import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const repoRoot = dirname(dirname(fileURLToPath(import.meta.url)));
// Skill packages live under the plugin, not a repo-root skills/ directory.
const skillsDir = join(repoRoot, "niaid-blueprint", "skills");
const mcpConfigPath = join(repoRoot, "niaid-blueprint", "mcp.json");
// Committed Pi templates. One file per prompts/evals procedure.
const evalPromptsDir = join(repoRoot, "extensions", "prompts");

function evalPromptPaths(): string[] {
	if (!existsSync(evalPromptsDir)) {
		return [];
	}
	return readdirSync(evalPromptsDir)
		.filter((name) => name.endsWith(".md"))
		.sort()
		.map((name) => join(evalPromptsDir, name));
}

function localSkillNames(): string[] {
	if (!existsSync(skillsDir)) {
		return [];
	}
	return readdirSync(skillsDir, { withFileTypes: true })
		.filter((entry) => entry.isDirectory() && existsSync(join(skillsDir, entry.name, "SKILL.md")))
		.map((entry) => entry.name)
		.sort();
}

type McpServerConfig = {
	command?: string;
	args?: string[];
	env?: Record<string, string>;
	cwd?: string;
	url?: string;
	headers?: Record<string, string>;
	type?: string;
};

function pluginMcpServers(): Array<[string, McpServerConfig]> {
	if (!existsSync(mcpConfigPath)) {
		return [];
	}
	const parsed = JSON.parse(readFileSync(mcpConfigPath, "utf8")) as {
		mcpServers?: Record<string, McpServerConfig>;
	};
	return Object.entries(parsed.mcpServers ?? {});
}

export default function (pi: ExtensionAPI) {
	for (const [name, config] of pluginMcpServers()) {
		pi.registerMcpServer(name, config);
	}

	pi.on("resources_discover", () => {
		return {
			skillPaths: [skillsDir],
			promptPaths: evalPromptPaths(),
		};
	});

	pi.on("session_start", (_event, ctx) => {
		if (!ctx.hasUI) {
			return;
		}
		const names = localSkillNames();
		const label = names.length > 0 ? names.join(", ") : "(none)";
		ctx.ui.notify(
			`niaid-blueprint skills: ${label}; eval prompts: ${evalPromptPaths().length}`,
			"info",
		);
	});
}
