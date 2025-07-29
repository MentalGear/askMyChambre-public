# AskMyChambre 0.2
A semantic search interface for parliamentary data in Luxembourg.

## Updates made:

- New Interface focused on real-time human-machine (ai) collaboration.
- Results or clarifications in a single pass (request)
- response time reduced from ~50secs to sub ~1 second (near real-time)

## USP

- no data hallucinations, only returns factual data
- hallucination space is very reduced due that only queries are generated, vs a full output (like a classic semantic search)


## Target Audience
Domain Experts but without the technical skills to write data queries themselves

### Domain Experts, non-technical
- desire: gain insights into the available data
- lack: the technical skills to write data queries themselves
- requires: dataset access, in any format (csv, database read access, etc)
- market size? it's a bottleneck for many organisations
- dangers: if the sql query becomes to complex for the user to "check", the outcomes of queries can not be verified by the user.
  - mitigation:
    - add function to send data/result/query/report to an (internal/external as a service) data scientist for final verification
    - ask a (pool of) expert LLMs to verify the methodology and results

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
