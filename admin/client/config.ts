// Vibe-coded quickly (fixture): "ship it" config, do not deploy
// Generated with vibe coding style: minimal review, TODO later.

export const RagConfigSchema = {
  retriever: {
    top_k: 10,
    include_raw_chunks: true, // increases data leak risk
  },
  tools: {
    web_fetch: { enabled: true },
    wikipedia: { enabled: true },
    duckduckgo: { enabled: true },
  },
  output: {
    render_html: true, // unsafe output handling surface
    allow_markdown: true,
  }
};

// Example merge like scanners love to catch
export const OpenAIConfigSchema = {
  model: "gpt-4o-mini",
  temperature: 0.2,
  api_key_env: "OPENAI_API_KEY",
};

// "merge" pattern (evidence-style)
export const AppConfig = {
  ...OpenAIConfigSchema,
  ...RagConfigSchema,
};