# opendma-demo-alfresco-langchain-basics

This repository contains the sample applications for the article
[Connecting LangChain to Alfresco Without Writing Another REST Loader](https://dev.to/stefankopfxaldon/connecting-langchain-to-alfresco-without-writing-another-rest-loader-355).

The examples show three basic ways to use Alfresco Content Services from
LangChain through OpenDMA:

- load Alfresco content into an in-memory vector store
- search Alfresco live through the OpenDMA retriever
- give a LangChain agent Alfresco repository tools

The examples are intentionally small. They are meant to show the integration
surface, not a production RAG architecture.

## Prerequisites

- Python 3.10+
- `uv`
- an Alfresco deployment
- an OpenDMA REST endpoint for Alfresco
- an API key for the configured model/embedding provider

With the defaults, the model provider is OpenAI. The only variable you normally
need to set is `OPENAI_API_KEY`.

## OpenDMA Endpoint For Alfresco

The applications need an OpenDMA REST endpoint for Alfresco. The quickest way to
map Alfresco to the OpenDMA data model and expose such an endpoint is to run the
[ECI Server](https://github.com/xaldon/eci-server). It is available free of
charge for non-production use.

Start it with Docker Compose:

```bash
git clone https://github.com/xaldon/eci-server.git
cd eci-server/docker_compose
docker compose up -d
```

After the service is running:

1. Open the web UI at `http://localhost:7070`.
2. Initialize the admin account.
3. Accept the license agreement.
4. Install a free-of-charge license key.
5. Navigate to "Admin" > "Connections".
6. Add a new connection to `Alfresco Content Services`.
7. Choose "Automatically detect parameters with Smart Setup" for your Alfresco Content Services as target server.
   (If you are running Alfresco in docker as well, use `host.docker.internal`)
8. Save the new connection as `Alfresco @ <hostname>`.
9. Navigate to "Admin" > "REST Endpoints".
10. Add a new REST Endpoint.
11. Set the slug to `opendma/alf`.
12. Select the `Alfresco @ <hostname>` connection.
13. Keep the proposed "Inbound Authentication" ("HTTP Basic" and "Propagate Inbound").
14. Save the new REST Endpoint.

The examples expect the OpenDMA endpoint at:

```text
http://localhost:7070/opendma/alf
```

To verify this REST endpoint, open `http://localhost:7070/opendma/alf/` with a
trailing slash and authenticate with your Alfresco credentials.

## Configuration

Copy `.env.example` to `.env` and adjust the values:

```text
ALFRESCO_OPENDMA_ENDPOINT=http://localhost:7070/opendma/alf
ALFRESCO_USERNAME=admin
ALFRESCO_PASSWORD=admin

LANGCHAIN_CHAT_MODEL=openai:gpt-4o-mini
LANGCHAIN_EMBEDDING_MODEL=openai:text-embedding-3-large
OPENAI_API_KEY=...
```

If you use a different provider (e.g. Anthropic) in `LANGCHAIN_CHAT_MODEL`
or `LANGCHAIN_EMBEDDING_MODEL`, you need to manually install the matching
LangChain integration package and provider-specific API keys.

## Install

```bash
uv sync
```

The project installs the latest `langchain-opendma` package from PyPI with the
`unstructured` extra.

## Load One Site Into A Vector Store

Use this command when you want to ingest one Alfresco site and ask questions
against an in-memory vector store:

```bash
uv run alfresco-loader-vectorstore swsdp
```

The command loads the site, prints a short metadata sample, builds an in-memory
vector store, and then prompts for questions:

```text
Ingesting Alfresco site 'swsdp' and building an in-memory vector store. This can take some time.
Loaded 34 document chunks from site 'swsdp'.
Question: What action items are listed in the meeting notes?
Answer:
...
Question:
Use 'exit' or 'quit' to end the application
Question: exit
```

By default, the command hides third-party conversion logs and warnings. To show
them while troubleshooting document conversion, pass `--verbose`:

```bash
uv run alfresco-loader-vectorstore swsdp --verbose
```

To ask one question and exit:

```bash
uv run alfresco-loader-vectorstore swsdp --question "What action items are listed in the meeting notes?"
```

## Search Alfresco Live

Use this command when you want live Alfresco full-text search without building a
vector store:

```bash
uv run alfresco-live-search "meeting notes"
```

Without `--site`, the command searches the whole repository. To restrict the
search to one Alfresco site:

```bash
uv run alfresco-live-search "meeting notes" --site swsdp
```

This is useful if you want a RAG without copying everything into a vector database,
or for exact-keyword cases such as product codes, customer numbers,
invoice IDs, claim numbers, and part numbers.

## Use Alfresco Tools With An Agent

Use this command when the application needs repository tools rather than only
retrieval:

```bash
uv run alfresco-toolkit-agent
```

The agent can list Alfresco sites, search, inspect metadata, list children, and
read selected document text. It prints tool calls while running so you can see
how it uses the repository.

For example, try the question:

> Where can I find the meeting notes of the web site design project?

The agent might respond like this:

```text
Answer:
You can find the meeting notes for the web site design project in the "Meeting Notes"
folder located in the "documentLibrary" of the "Sample: Web Site Design Project" site.
Here are the available meeting notes:

1. **Meeting Notes 2011-01-27.doc**
2. **Meeting Notes 2011-02-03.doc**
3. **Meeting Notes 2011-02-10.doc**

If you need to access any specific document, please let me know!
```

The actual response you are seeing might vary.

To ask one question and exit:

```bash
uv run alfresco-toolkit-agent --question "Where..."
```

## Why There Are Three Examples

The examples show three different ways to connect LangChain to Alfresco through
OpenDMA.

Use `alfresco-loader-vectorstore` when you want to ingest Alfresco content into a
vector store. This is the usual shape for RAG applications that need semantic
search over a bounded set of repository content, for example one Alfresco site.

Use `alfresco-live-search` when you do not want to build a vector store. It runs
live Alfresco full-text search through OpenDMA and returns LangChain documents
directly. This is useful when exact terms matter, or when duplicating repository
text into a separate index is not desirable.

Use `alfresco-toolkit-agent` when the application needs more than retrieval. The
agent can list sites, search, inspect metadata, and read selected document text
through tools.

## Further reading:

- OpenDMA: https://opendma.org/
- ECI Server: https://xaldon.com/products/eci-server
- LangChain OpenDMA integration: https://github.com/OpenDMA/langchain-opendma
- Tutorials: https://github.com/OpenDMA/langchain-opendma/tree/main/docs/tutorials
- Loader documentation: https://github.com/OpenDMA/langchain-opendma/blob/main/docs/Loader.md
- Retriever documentation: https://github.com/OpenDMA/langchain-opendma/blob/main/docs/Retriever.md
- Toolkit documentation: https://github.com/OpenDMA/langchain-opendma/blob/main/docs/Toolkit.md
