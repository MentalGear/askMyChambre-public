# AskMyChambre 0.2
A semantic search interface for parliamentary data in Luxembourg.

## Updates made:

- New Interface focused on real-time human-machine (ai) collaboration.
- Results or clarifications in a single pass (request)
- response time reduced from ~50secs to sub ~1 second (near real-time)

## USP

- no data hallucinations, only returns factual data
- hallucination space is very reduced due that only queries are generated, vs a full output (like a classic semantic search)

## Setup

0. have nodejs installed (optionally `pnpm` instead of npm)

1. in the folder with package.json (root) (replace with `npm` if you dont' have `pnpm`)
- `pnpm i`
- `pnpm dev`

## Limitations

- The server can become unresponsive. This is due to sqlite and the node server running on a single-threaded instance, so if the generated sql query is long running or otherwise blocking, the whole server can become unresponsive. In this case, you have to restart the dev server. This was attempted but not addressed since ultimately if this project continues it will be moved to a proper analytical database anyways.

- chat autoscroll is not working for sqlite markdown generation

## Target Audience

**Domain Experts without Technical Querying Skills**

### Overview

These users possess deep subject-matter expertise but lack the technical ability to write or validate data queries (e.g., SQL). Their goal is to derive meaningful insights from existing datasets without relying on technical intermediaries for every question.

### Characteristics

* **Desires:**

  * Gain actionable insights from available data
  * Explore trends, anomalies, and relationships relevant to their field
* **Limitations:**

  * Lack of knowledge or experience with query languages like SQL
  * Limited ability to validate complex queries or data pipelines
* **Requirements:**

  * Access to relevant datasets (e.g., CSV files, database read access)
  * Intuitive interfaces for querying or filtering data without coding
  * Transparency in the logic and results of queries

### Market Relevance

* This user group represents a major pain point for many organizations: data bottlenecks caused by reliance on technical staff for routine questions.
* Empowering non-technical domain experts can dramatically accelerate decision-making and reduce load on data teams.

### Risks and Mitigations

* **Risk:**

  * Complex queries may become opaque, preventing users from verifying outcomes or catching errors in logic.
* **Mitigations:**

  * Include a built-in option to escalate or forward the query/result/report to a data scientist (internal or via a managed service) for validation
  * Integrate a secondary verification layer using expert-level LLMs to review methodology, assumptions, and outputs

---

Let me know if you’d like this tailored to a specific use case (e.g. healthcare, finance, etc.) or rewritten in a more casual/product-marketing tone.

## Tech stack

- SvelteKit
- TailwindCSS
- AI SDK
- Vite

# sv

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```bash
# create a new project in the current directory
npx sv create

# create a new project in my-app
npx sv create my-app
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.


## Copyright / License

All commercial rights reserved.
