# Sample Size Explainer App

## Project Purpose

An educational web app that explains sample sizes in statistics through interactive examples. The core message: **sample size effectiveness does not depend on population size**. Once you reach a certain N (typically around 1,000-1,500), you get reliable estimates regardless of whether the population is 10,000 or 320 million.

### The Problem We're Solving

Many people see a national poll in the US with ~1,200 respondents and dismiss it as unreliable because "how can 1,200 people represent 320 million?" This is a common misconception. The math of sampling shows that precision depends primarily on sample size, not on the ratio of sample to population.

### Key Statistical Concepts to Convey

1. **Margin of Error** - Depends on sample size (n), not population size (N). Formula: MOE ≈ 1/√n
2. **The "bowl of soup" analogy** - You don't need to taste the whole pot to know if it's salty, just a well-stirred spoonful
3. **Confidence Intervals** - How certain we can be about our estimate
4. **Law of Large Numbers** - Sample means converge to population mean as n increases
5. **Finite Population Correction** - Only matters when sampling a large fraction (>5%) of the population

---

## MCP Tools

You are able to use the Svelte MCP server, where you have access to comprehensive Svelte 5 and SvelteKit documentation. Here's how to use the available tools effectively:

## Available MCP Tools:

### 1. list-sections

Use this FIRST to discover all available documentation sections. Returns a structured list with titles, use_cases, and paths.
When asked about Svelte or SvelteKit topics, ALWAYS use this tool at the start of the chat to find relevant sections.

### 2. get-documentation

Retrieves full documentation content for specific sections. Accepts single or multiple sections.
After calling the list-sections tool, you MUST analyze the returned documentation sections (especially the use_cases field) and then use the get-documentation tool to fetch ALL documentation sections that are relevant for the user's task.

### 3. svelte-autofixer

Analyzes Svelte code and returns issues and suggestions.
You MUST use this tool whenever writing Svelte code before sending it to the user. Keep calling it until no issues or suggestions are returned.

### 4. playground-link

Generates a Svelte Playground link with the provided code.
After completing the code, ask the user if they want a playground link. Only call this tool after user confirmation and NEVER if code was written to files in their project.
