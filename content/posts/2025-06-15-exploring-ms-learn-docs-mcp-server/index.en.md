+++
title = "Trying the Official Microsoft Learn Docs MCP Server"
description = "A summary of my experience using the official Microsoft Learn Docs MCP Server. Covers setup, features, search scope, and more."
slug = "exploring-ms-learn-docs-mcp-server"
date = "2025-06-15"
categories = ["Azure"]
tags = ["MCP", "Azure", "LLM"]
keywords = ["Azure", "MCP", "LLM"]
+++

Recently, Microsoft released the official MCP server for searching Microsoft documentation (Microsoft Learn Docs MCP Server). This is great news for Azure users like myself.

https://github.com/MicrosoftDocs/mcp

However, the implementation and architecture details are not public, so some aspects of its behavior are still unknown. In this article, I summarize what I learned from actually using the Microsoft Learn Docs MCP Server.

This article assumes you have basic knowledge of MCP. If you want to learn more about MCP, check out the following resources:

- https://modelcontextprotocol.io/introduction
- https://github.com/microsoft/mcp-for-beginners

Also, Microsoft provides other official MCP servers besides the Learn Docs MCP Server, such as the Azure MCP Server. If you're interested, see:

- https://github.com/microsoft/mcp

<!--more-->

## Setup

To use the Microsoft Learn Docs MCP Server, configure your MCP client (supporting Streamable HTTP) to use the endpoint `https://learn.microsoft.com/api/mcp`.

In VS Code (GitHub Copilot), the configuration looks like this[^vs-code-mcp-http]:
[^vs-code-mcp-http]: https://code.visualstudio.com/updates/v1_100#_mcp-support-for-streamable-http

```json:settings.json
    "mcp": {
        "inputs": [],
        "servers": {
            "msdocsmicrosoft.docs.mcp": {
                "type": "http",
                "url": "https://learn.microsoft.com/api/mcp"
            }
        }
    },
```

For this article, I used [MCP Inspector](https://github.com/modelcontextprotocol/inspector) as the client to test the server. It allows you to set requests (e.g., search keywords) and view responses (e.g., matched docs) without being affected by the non-deterministic behavior of LLMs[^llm-inconsistency].

[^llm-inconsistency]: The way requests are sent to the MCP server and how responses are incorporated into answers depends on the LLM/agent. See https://github.com/MicrosoftDocs/mcp/issues/6 for a related issue.

## Features

As of 2025/6/21, the Microsoft Learn Docs MCP Server provides only the `microsoft_docs_search` tool.

This tool takes a search keyword and returns relevant official documentation content and the **English** doc URL[^msdocs-update-latency]. Here is the tool description as returned by List Tools:

> Search official Microsoft/Azure documentation to find the most relevant and trustworthy content for a user's query. This tool returns up to 10 high-quality content chunks (each max 500 tokens), extracted from Microsoft Learn and other official sources. Each result includes the article title, URL, and a self-contained content excerpt optimized for fast retrieval and reasoning. Always use this tool to quickly ground your answers in accurate, first-party Microsoft/Azure knowledge.

[^msdocs-update-latency]: English docs are referenced because updates appear there first, which is helpful.

From my tests, the search combines keyword and semantic search:

- Searching for error codes like `UserErrorGuestAgentStatusUnavailable` returns docs that mention the code.
- Fuzzy, natural language queries like "Tell me about Microsoft 365 Copilot data retention policy" also work well, in both Japanese and English, suggesting a modern semantic search implementation.

## microsoft_docs_search Characteristics

### Response

The MCP server returns a list of up to 10 content chunks (from official docs). Here is an example response:

```json
[
  {
    "title": "Troubleshoot Azure Backup failures caused by agent or extension issues",
    "content": "# Troubleshoot Azure Backup failures caused by agent or extension issues\n## Step-by-step guide to troubleshoot backup failures\n5. **Ensure the VSS writer service is up and running**: ...",
    "contentUrl": "https://learn.microsoft.com/en-us/azure/backup/backup-azure-troubleshoot-vm-backup-fails-snapshot-timeout#step-by-step-guide-to-troubleshoot-backup-failures"
  }
  // ...
]
```

Returned content is optimized for clients (LLMs/agents):

- Always includes the doc title and URL.
- Uses Markdown format (preserves doc structure).
- Each chunk starts with a heading (h1/h2).

Content is **sorted by relevance (most relevant first)**[^issue-7]. If your client can, prioritize the first chunk[^llm-context-position].

[^issue-7]: https://github.com/MicrosoftDocs/mcp/issues/7#issuecomment-2974973248
[^llm-context-position]: In RAG systems, the position of information can affect accuracy (see "Lost in the Middle").

### Search Scope

According to the GitHub page, the search covers Microsoft Learn, Azure docs, M365 docs, and other official Microsoft sources:

> Microsoft Learn, Azure documentation, Microsoft 365 documentation, and other official Microsoft sources.
> https://github.com/MicrosoftDocs/mcp?tab=readme-ov-file#-key-capabilities

I did a quick experiment to see how broad the coverage is. I picked several services from the [product directory](https://learn.microsoft.com/en-us/docs/), selected a doc page for each, and searched using the service name and page title. If the response included the product's URL, I considered it supported.

```json
{
  "query": "Dynamics 365: Integration overview for Business Central (for architects and developers)"
}
```

Results:

| Service                    | Doc URL                                                           | Supported |
| :------------------------- | :---------------------------------------------------------------- | :-------- |
| .NET                       | https://learn.microsoft.com/en-us/dotnet/                         | ✅        |
| Azure                      | https://learn.microsoft.com/en-us/azure/                          | ✅        |
| Azure Architecture Center  | https://learn.microsoft.com/en-us/azure/architecture/             | ✅        |
| Cloud Adoption Framework   | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ | ✅        |
| Well-Architected Framework | https://learn.microsoft.com/en-us/azure/well-architected/         | ✅        |
| Azure CLI                  | https://learn.microsoft.com/en-us/cli/                            | ✅        |
| C++                        | https://learn.microsoft.com/en-us/cpp/                            | ✅        |
| Dynamics 365               | https://learn.microsoft.com/en-us/dynamics365/                    | ✅        |
| Microsoft Graph            | https://learn.microsoft.com/en-us/graph/                          | ✅        |
| Microsoft 365              | https://learn.microsoft.com/en-us/microsoft-365/                  | ✅        |
| Microsoft 365 Copilot      | https://learn.microsoft.com/en-us/microsoft-copilot-service/      | ✅        |
| PowerShell                 | https://learn.microsoft.com/en-us/powershell/                     | ✅        |
| Training                   | https://learn.microsoft.com/en-us/training/                       | ✅        |
| Windows                    | https://learn.microsoft.com/en-us/windows/                        | ✅        |
| Windows Server             | https://learn.microsoft.com/en-us/windows-server/                 | ✅        |

All tested services were searchable, so coverage appears very broad. For Azure, it's great that the Architecture Center, Well-Architected Framework (WAF), and Cloud Adoption Framework (CAF) are included. Even vague queries like "Best practices for mission-critical Azure systems" return content from URLs like:

- https://learn.microsoft.com/en-us/azure/well-architected/mission-critical/mission-critical-operational-procedures#application-operations
- https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-mission-critical/mission-critical-operations

### Update Speed

The GitHub page claims "real-time updates" for the latest docs:

> - **Real-time Updates**: Access the latest Microsoft documentation as it's published.

In practice, search engines usually work on pre-processed content, so you can't always get the absolute latest docs. For example, semantic search with embeddings requires chunking and indexing in advance.

To check how up-to-date the index is, I looked at the latest commit in the GitHub history for the docs. The most recent update reflected in the docs was from 14 hours earlier:

https://github.com/MicrosoftDocs/azure-docs/commit/0dd0229ee18e326a7788f260102316fd3933b240

Searching for "OpenPBS Integration: OpenPBS scheduler configuration in Azure CycleCloud" returned content about the disk size being hardcoded to 20g, matching the update. I don't know much about CycleCloud, but it seems accurate.

{{< figure src="index-speed-01.png" caption="Search result" >}}

This matches content updated 14 hours earlier.

{{< figure src="index-speed-02.png" caption="Content after update (right) matches search result" >}}

So, at least for updates 14 hours ago, the search index is up to date. The exact latency is unclear, but it's practically short enough.

## Example: GitHub Copilot

Here's an example of using `microsoft_docs_search` in GitHub Copilot's agent mode.

Suppose you want to look up Bicep best practices in a repo with Bicep code, then generate Copilot instructions for writing Bicep code.

First, here's the answer from plain GitHub Copilot[^chat-variables]:
[^chat-variables]: Built-in tools enabled: https://code.visualstudio.com/docs/copilot/reference/copilot-vscode-features#_chat-variables

{{< figure src="demo-01.png" caption="Plain GitHub Copilot answer" >}}

The model `GPT-4.1` has a recent cutoff (2024/6), so the answer is decent, but not quite what you'd want for instructions.

Next, using [GitHub Copilot for Azure](https://learn.microsoft.com/ja-jp/azure/developer/github-copilot-azure/introduction), which provides the `azure_query_learn` tool for searching Azure docs. Asking the same question returns only one content page, so the answer is less detailed.

{{< figure src="demo-02.png" caption="GitHub Copilot for Azure answer" >}}

Finally, using `microsoft_docs_search`:

{{< figure src="demo-03.png" caption="GitHub Copilot x MCP (microsoft_docs_search) answer" >}}

The answer is based on 10 related docs, so it's much more detailed and closer to what I wanted.

## Summary

Through testing the `microsoft_docs_search` tool provided by the official Microsoft Learn Docs MCP Server, I found the following features:

- **High-precision search**: Both specific keywords (like error codes) and fuzzy natural language queries return highly relevant docs. The search combines keyword and semantic search, similar to modern engines.
- **LLM-optimized content**: Results are provided as Markdown content chunks with titles and URLs, starting with headings for easy LLM consumption. Content appears sorted by relevance, which helps RAG systems use information efficiently.
- **Broad documentation coverage**: Major Microsoft docs, including Azure, Microsoft 365, Windows, .NET, and Dynamics 365, are all searchable. For Azure users, it's especially nice that architecture docs (Architecture Center, WAF, CAF) are included.
- **Fast update reflection**: Doc updates are reflected in the search index within at least 14 hours, so you can expect to always reference the latest official info.

More clients now support Streamable HTTP (e.g., [M365 Copilot agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp#supported-transports)), making it easier to use the Microsoft Learn Docs MCP Server. I'm excited to see what new use cases will emerge!
