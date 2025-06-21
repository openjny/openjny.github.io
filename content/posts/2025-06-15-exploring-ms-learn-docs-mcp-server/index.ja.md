+++
title = "Microsoft Learn Docs の公式 MCP サーバーを試す"
description = "Microsoft Learn Docs の公式 MCP サーバーを試してみた結果をまとめました。MCP サーバーの設定方法や、提供される機能、検索スコープなどについて解説します。"
slug = "exploring-ms-learn-docs-mcp-server"
date = "2025-06-15"
categories = [
    "Azure"
]
tags = ["MCP", "Azure", "LLM"]
keywords = ["Azure", "MCP", "LLM"]
isCJKLanguage = true
+++

先日、Microsoft の公式ドキュメントを検索するためのオフィシャル MCP サーバー (Microsoft Learn Docs MCP Server) が公開されました。自分のような Azure ユーザーには大変嬉しい発表です。

https://github.com/MicrosoftDocs/mcp

ただ、具体的な実装とアーキテクチャは公開されておらず、どんな動作をするのか未知な部分があります。そこで、本記事では Microsoft Learn Docs MCP Server を使ってみてわかったことを少しまとめてみました。

なお、読者には MCP の基礎知識があることを前提にしています。MCP について知りたい場合は、次のような文献をあたってみてください。

- [Introduction - Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [mcp-for-beginners/translations/ja/README.md at main · microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners/blob/main/translations/ja/README.md)

また、Microsoft が提供している MCP サーバーは、Microsoft Learn Docs MCP Server だけではありません。Azure MCP Server など、他のオフィシャル実装も気になる場合は、以下をチェックしてみてください。

- https://github.com/microsoft/mcp

<!--more-->

## 設定方法

Microsoft Learn Docs MCP Server を使用するには、Streamable HTTP に対応する MCP クライアントで、エンドポイントに `https://learn.microsoft.com/api/mcp` を指定します。

VS Code (GitHub Copilot) では、次のような構成に相当します[^vs-code-mcp-http]。
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

今回は MCP サーバーの動作確認が主な目的なので、クライアントに [MCP Inspector](https://github.com/modelcontextprotocol/inspector) を使いました。MCP サーバーに発行するリクエスト (e.g. 検索キーワード) を設定したり、MCP サーバーからのレスポンス (e.g. 検索にヒットした公式ドキュメント) を閲覧する機能があるため、LLM の非決定的な振る舞い[^llm-inconsistency]に邪魔されずに検証できます。

[^llm-inconsistency]: MCP サーバーにどんな要求を渡すか、サーバーからのレスポンスをどう回答に盛り込むかは、LLM やエージェントの動作依存です。早速、https://github.com/MicrosoftDocs/mcp/issues/6 で類似事象が報告されてました。

## 提供される機能

2025/6/21 現在、Microsoft Learn Docs MCP Server が提供する機能 (リソース/プロンプト/ツール) は、`microsoft_docs_search` ツールのみです。

このツールは、検索キーワードを入力に受取、それに関連する公式ドキュメントのコンテンツと **英語版**のドキュメント URL[^msdocs-update-latency] を返却します。以下は、List Tools 実行時に返却される (LLM/エージェントが参照する) ツールの説明文です。

> Search official Microsoft/Azure documentation to find the most relevant and trustworthy content for a user's query. This tool returns up to 10 high-quality content chunks (each max 500 tokens), extracted from Microsoft Learn and other official sources. Each result includes the article title, URL, and a self-contained content excerpt optimized for fast retrieval and reasoning. Always use this tool to quickly ground your answers in accurate, first-party Microsoft/Azure knowledge.

> [^msdocs-update-latency]: ドキュメントの更新もオリジナルである英語版が最も早いので、参照されるドキュメントが英語なのはありがたいです。

検索を試してみた結果、キーワード検索とセマンティック検索を混ぜ合わせた検索スタイルのようです:

- `UserErrorGuestAgentStatusUnavailable` のようなエラーコードを直接検索キーワードにすると、そのエラーコードが記述されているドキュメントをしっかり拾ってくれます。
- `Microsoft 365 Copilot のデータ保持ポリシーについて知りたい` のような自然言語によるファジーな検索にも対応しています。入力文に関しては、日本語でも英語でも問題ないようなので、最近の言語モデルを使ったセマンティック検索が実装されていると予想されます。

## microsoft_docs_search の特徴

### レスポンス

MCP サーバーからのレスポンスは、 最大 10 個のコンテンツ (公式ドキュメントのチャンク) のリストです。以下は、実際のレスポンスの例です。

```json
[
  {
    "title": "Troubleshoot Azure Backup failures caused by agent or extension issues",
    "content": "# Troubleshoot Azure Backup failures caused by agent or extension issues\n## Step-by-step guide to troubleshoot backup failures\n5. **Ensure the VSS writer service is up and running**: Follow these steps To [Troubleshoot VSS writer issues](https://learn.microsoft.com/en-us/azure/backup/backup-azure-vms-troubleshoot#extensionfailedvsswriterinbadstate---snapshot-operation-failed-because-vss-writers-were-in-a-bad-state).\n6. **Follow backup best practice guidelines**: Review the [best practices to enable Azure VM backup](https://learn.microsoft.com/en-us/azure/backup/backup-azure-vms-introduction#best-practices).\n7. **Review guidelines for encrypted disks**: If you're enabling backup for VMs with encrypted disk, ensure you've provided all the required permissions. To learn more, see [Back up and restore encrypted Azure VM](https://learn.microsoft.com/en-us/azure/backup/backup-azure-vms-encryption).\n## UserErrorGuestAgentStatusUnavailable - VM agent unable to communicate with Azure Backup\n**Error code**: UserErrorGuestAgentStatusUnavailable **Error message**: VM Agent unable to communicate with Azure Backup\nThe Azure VM agent might be stopped, outdated, in an inconsistent state, or not installed. These states prevent the Azure Backup service from triggering snapshots.\n1. **Open Azure portal > VM > Settings > Properties pane** > ensure VM **Status** is **Running** and **Agent status** is **Ready**. If the VM agent is stopped or is in an inconsistent state, restart the agent\n1.1. For Windows VMs, follow these steps to restart the Guest Agent.\n1.2. For Linux VMs, follow these steps to restart the Guest Agent.\n2. **Open Azure portal > VM > Settings > Extensions** > Ensure all extensions are in **provisioning succeeded** state. If not, follow these steps to resolve the issue.",
    "contentUrl": "https://learn.microsoft.com/en-us/azure/backup/backup-azure-troubleshoot-vm-backup-fails-snapshot-timeout#step-by-step-guide-to-troubleshoot-backup-failures"
  },
  {
    "title": "Troubleshoot Azure Windows VM Agent issues",
    "content": "# Troubleshoot Azure Windows VM Agent issues\n## Troubleshooting checklist\nFor any VM extension to be able to run, Azure VM Guest Agent must be installed and working successfully. If you see that Guest Agent is reported as **Not ready**, or if an extension is failing and returning an error message such as `VMAgentStatusCommunicationError`, follow these steps to begin troubleshooting Guest Agent.\n### Step 1: Check whether the VM is started\nTo verify that the VM is started, follow these steps:\n1. In the [Azure portal](https://portal.azure.com), search for and select **Virtual machines**.\n2. In the list of VMs, select the name of your Azure VM.\n3. In the navigation pane of your Azure VM, select **Overview**.\n4. If the VM isn't turned on already, locate the list of actions at the top of the **Overview** page, and then select the **Start** link.\nAlso, verify that the operating system (OS) is started and running successfully.\n### Step 2: Check whether Guest Agent is ready\nWhile you're still on the VM overview page of the Azure portal, select the **Properties** tab. If the **Agent status** field has a value of **Ready**, verify that the **Agent version** field value satisfies the [minimum supported version](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/windows/support-extensions-agent-version). The following screenshot shows where you can find these fields.\nIf the Guest Agent status is **Ready** but you have an issue that involves a VM extension, see [Azure virtual machine extensions and features](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/overview) to review troubleshooting suggestions.\nIf the Guest Agent status is **Not ready** or blank, then either Guest Agent isn't installed or it isn't working correctly.\n### Step 3: Check whether the Guest Agent services are running\n1. [Use Remote Desktop Protocol (RDP) to connect to your VM](https://learn.microsoft.com/en-us/azure/virtual-machines/windows/connect-rdp).\n Note\n The Guest Agent isn't necessary for RDP connectivity to work successfully. If you experience issues that affect RDP connectivity to your VM, see [Troubleshoot Remote Desktop connections to an Azure virtual machine](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/windows/troubleshoot-rdp-connection).\n2. On your VM, select **Start**, search for *services.msc*, and then select the **Services** app.\n3. In the **Services** window, select the **RdAgent** service.",
    "contentUrl": "https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/windows/windows-azure-guest-agent#troubleshooting-checklist"
  },
  {
    "title": "Troubleshoot Azure Windows VM Agent issues",
    "content": "# Troubleshoot Azure Windows VM Agent issues\n## Troubleshooting checklist\n4. Select the **Action** menu, and then select **Properties**.\n5. On the **General** tab of the **Properties** dialog box, make sure that the following conditions are true, and then select the **OK** or **Cancel** button:\n5.1. The **Startup type** drop-down list is set to **Automatic**.\n5.2. The **Service status** field has a value of **Running**.\n6. In the **Services** window, select the **WindowsAzureGuestAgent** service.\n7. Repeat steps 4 and 5.\nIf the services don't exist, the Guest Agent probably isn't installed. In this case, you can [manually install the Guest Agent](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/agent-windows#manual-installation). Before you do a manual installation, [check the installation prerequisites](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/agent-windows#prerequisites).\n### Step 4: Test WireServer connectivity\nTo run successfully, Guest Agent requires connectivity to the WireServer IP (host IP) address `168.63.129.16` on ports `80` and `32526`. For instructions about how to test connectivity to this IP address, see the [Troubleshoot connectivity](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16#troubleshoot-connectivity) section of [What is IP address 168.63.129.16?](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)\nIf any of the tests in that section don't connect, check for issues that might cause any of the following components to block access to IP address `168.63.129.16`:\n1. A firewall\n2. A proxy\n3. An application\n### Step 5: Review log files\nCheck the following log locations for any notable errors:\n1. *C:\\WindowsAzure\\Logs\\WaAppAgent.log*\n2. *C:\\WindowsAzure\\Logs\\TransparentInstaller.log*\nCompare any errors that you find to the following common scenarios that can cause the Azure VM Agent to show a **Not ready** status or stop working as expected.",
    "contentUrl": "https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/windows/windows-azure-guest-agent#troubleshooting-checklist"
  }
  // ...
]
```

返却されたコンテンツがクライアント (LLM/エージェント) で取り扱いやすいように、次のような工夫が施されています。

- ドキュメントのタイトルと URL が必ず含まれる。
- Markdown 形式で記述されている (ドキュメントの構造が保持される)。
- コンテンツが見出し (h1 や h2) から始まるように分割されている。

コンテンツは、**関連度順 (最も関連するものが先頭に来るよう) にソートされています**[^issue-7]。クライアントで調整できる場合は、先頭のものを優先的に使用すると良いでしょう[^llm-context-position]。

[^issue-7]: https://github.com/MicrosoftDocs/mcp/issues/7#issuecomment-2974973248
[^llm-context-position]: Lost in the Middle で代表されるように、RAG システムでは情報の埋め込み位置（順番）によって精度が変化する可能性が指摘されています。

### 検索スコープ

GitHub ページでは、検索対象のコンテンツは Microsoft Learn、Azure ドキュメント、M365 ドキュメント、その他の Microsoft のリソースと記述されています。

> Microsoft Learn, Azure documentation, Microsoft 365 documentation, and other official Microsoft sources.
> https://github.com/MicrosoftDocs/mcp?tab=readme-ov-file#-key-capabilities

実際にどの程度カバーできてるのか、簡単に実験してみます。具体的には、[製品ディレクトリ](https://learn.microsoft.com/en-us/docs/) から、サービスをいくつかピックアップします。サービスごとに適当な公式ドキュメント ページを選定し、サービス名とページ タイトルを `query` に設定して `microsoft_docs_search` を実行します。そして、レスポンスにその製品の URL が含まれていれば、サービスが検索に対応していると判断します。

```json:query の例
{ "query": "Dynamics 365: Integration overview for Business Central (for architects and developers)" }
```

結果は、次の通りとなりました。

| サービス                           | サービスのドキュメント URL                                        | 結果 (対応可否) |
| :--------------------------------- | :---------------------------------------------------------------- | :-------------- |
| .NET                               | https://learn.microsoft.com/en-us/dotnet/                         | ✅              |
| Azure                              | https://learn.microsoft.com/en-us/azure/                          | ✅              |
| Azure > Azure Architecture Center  | https://learn.microsoft.com/en-us/azure/architecture/             | ✅              |
| Azure > Cloud Adoption Framework   | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ | ✅              |
| Azure > Well-Architected Framework | https://learn.microsoft.com/en-us/azure/well-architected/         | ✅              |
| Azure CLI                          | https://learn.microsoft.com/en-us/cli/                            | ✅              |
| C++                                | https://learn.microsoft.com/en-us/cpp/                            | ✅              |
| Dynamics 365                       | https://learn.microsoft.com/en-us/dynamics365/                    | ✅              |
| Microsoft Graph                    | https://learn.microsoft.com/en-us/graph/                          | ✅              |
| Microsoft 365                      | https://learn.microsoft.com/en-us/microsoft-365/                  | ✅              |
| Microsoft 365 Copilot              | https://learn.microsoft.com/en-us/microsoft-copilot-service/      | ✅              |
| PowerShell                         | https://learn.microsoft.com/en-us/powershell/                     | ✅              |
| Training                           | https://learn.microsoft.com/en-us/training/                       | ✅              |
| Windows                            | https://learn.microsoft.com/en-us/windows/                        | ✅              |
| Windows Server                     | https://learn.microsoft.com/en-us/windows-server/                 | ✅              |

検証したサービスはすべて検索可能だったので、かなり広域なコンテンツがカバーされているだろうと考えられます。

Azure 関連で言えば、アーキテクチャセンター、Well-Architected Framework (WAF)、Could Adoption Framework (CAF) が対象に含まれているのが嬉しいです。例えば、`ミッションクリティカルな Azure システムのベストプラクティス` のように雑にクエリを投げても、次のような URL からコンテンツを取って来てくれます。

- https://learn.microsoft.com/en-us/azure/well-architected/mission-critical/mission-critical-operational-procedures#application-operations
- https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-mission-critical/mission-critical-operations

### 更新の反映スピード

GitHub のページでは、「最新の情報が取得できる」と記述されています。

> - **Real-time Updates**: Access the latest Microsoft documentation as it's published.

一般に、検索エンジンは前処理したコンテンツを検索対象とするため、真に最新のコンテンツが検索できるとは限りません。たとえば、流行りの文書埋め込みによるセマンティック検索なんかでは、検索対象のチャンク化とインデックス化の前処理が必要です。

そこで、どこまで最新の情報が取れるのか確認してみます。GitHub 上の更新履歴を見ると、ドキュメントでの反映が確認できた最新の更新が以下のコミットでした。これは、確認の **14 時間前** に加わったドキュメント更新です。

https://github.com/MicrosoftDocs/azure-docs/commit/0dd0229ee18e326a7788f260102316fd3933b240

`OpenPBS Integration: OpenPBS scheduler configuration in Azure CycleCloud` で検索すると、ディスクサイズが 20g にハードコーディングされている、みたいな趣旨の内容が含まれていました。CycleCloud は何もしりませんが、そうなんだろうという感じです。

{{< figure src="index-speed-01.png" caption="検索結果" >}}

これは、14 時間前に更新されたコンテンツと一致しています。

{{< figure src="index-speed-02.png" caption="更新後 (右側) のコンテンツが検索結果と一致" >}}

したがって、少なくとも 14 時間前の更新であれば、検索に反映されていることがわかりました。厳密なインデックス更新のレイテンシは分からないものの、実用上十分短いレイテンシであるものと考えられます。

## 動作例: GitHub Copilot

GitHub Copilot のエージェントモードで `microsoft_docs_search` を使用した場合の動作例を紹介します。

Bicep コードが含まれるレポジトリ上で、Bicep のベストプラクティスを調べてみます。この質問をした後、Bicep コードを記述するための GitHub Copilot インストラクション (.github/instructions/...) を作ってもらう想定です。

まずは、素の GitHub Copilot[^chat-variables] を使った際の回答です。
[^chat-variables]: Built-in ツールは有効化しています: https://code.visualstudio.com/docs/copilot/reference/copilot-vscode-features#_chat-variables

{{< figure src="demo-01.png" caption="素の GitHub Copilot の回答" >}}

使用したモデル `GPT-4.1` は、カットオフ日が 2024/6 と比較的新しいため、それなりの回答を作ってくれました。ですが、インストラクションに変換したいかと言われると微妙です。

続いて、[GitHub Copilot for Azure](https://learn.microsoft.com/ja-jp/azure/developer/github-copilot-azure/introduction) を使って回答を生成してみます。GitHub Copilot for Azure は、自分の Azure リソースにアクセスしてコンテキストを付与するための GitHub Copilot 向け拡張機能ですが、簡易的に Azure ドキュメントを検索する `azure_query_learn` ツールを備えます。ここでは、そのツールを呼び出して同じ質問をします。

{{< figure src="demo-02.png" caption="GitHub Copilot for Azure の回答" >}}

グラウンディングできている点は先程よりも一歩前進ですが、自分が期待する回答とほど遠い結果となりました。サーバーとのやり取りを見ると、レスポンスに含まれるコンテンツ ページが一つだけだったので、取得できる情報の少なさがボトルネックのようです。

最後に、`microsoft_docs_search` を使用して回答を生成してみます。

{{< figure src="demo-03.png" caption="GitHub Copilot x MCP (microsoft_docs_search) の回答" >}}

見切れてしまっていますが、10 件の関連ドキュメントによる回答なので詳細な部分まで踏み込んだ説明になっています。試したシナリオの中では最も期待する回答に近いものが得られました。

## まとめ

本記事では、Microsoft Learn Docs の公式 MCP サーバー (Microsoft Learn Docs MCP Server) が提供する `microsoft_docs_search` ツールの検証を通して、次のような特徴があることを確認しました。

- **高精度な検索能力**: エラーコードのような具体的なキーワードから、「Microsoft 365 Copilot のデータ保持ポリシーについて知りたい」といった自然言語によるファジーなクエリまで、どちらも高い精度で関連性の高いドキュメントを抽出できました。キーワード検索とセマンティック検索を組み合わせた、最新の検索エンジンに近い挙動をしていると考えられます。
- **LLM に最適化されたコンテンツ形式**: 検索結果は、タイトルと URL を含む Markdown 形式のコンテンツ チャンクとして提供されます。各チャンクはドキュメントの見出しから始まり、LLM が扱いやすいように工夫されています。返却されるコンテンツは関連度順にソートされているように見え、これは RAG システムにおける情報の利用効率を高めるのに役立つでしょう。
- **広範なドキュメントの網羅**: Azure、Microsoft 365、Windows、.NET、Dynamics 365 など、Microsoft の主要な公式ドキュメントが幅広く検索対象に含まれていることを確認しました。特に Azure のアーキテクチャ関連ドキュメント（Azure Architecture Center, Well-Architected Framework, Cloud Adoption Framework）がカバーされているのは、Azure ユーザーにとって大きなメリットです。
- **迅速な情報反映**: GitHub でのドキュメント更新から少なくとも 14 時間後には、その内容が MCP サーバーの検索結果に反映されていることを確認しました。これにより、常に最新の公式情報を参照できることが期待できます。

[M365 Copilot エージェントも Streamable HTTP に対応](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp#supported-transports)していますし、Microsoft Learn Docs MCP Server を手軽に使えるクライアントは増えてきています。これからどんな活用事例が生まれてくるのか、非常に楽しみです。
