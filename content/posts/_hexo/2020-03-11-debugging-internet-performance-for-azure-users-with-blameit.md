---
title: "和訳: Who’s to blame? Debugging Internet performance for Azure users with BlameIt"
slug: debugging-internet-performance-for-azure-users-with-blameit
date: 2020-03-11
categories:
  - Azure
tags:
  - Azure
  - Networking
isCJKLanguage: true
---

Azure にアクセスするユーザーが低レイテンシで快適にサービスを利用できるように、Microsoft では ISP (自律システム) の障害を検知するシステムを活用しています。そのシステム "BlameIt" を紹介する公式ブログがあったので、それを和訳してみました。

[Who’s to blame? Debugging Internet performance for Azure users with BlameIt - Microsoft Research](https://www.microsoft.com/en-us/research/blog/whos-to-blame-debugging-internet-performance-for-azure-users-with-blameit/)

## <!--more-->

Microsoft の Azure は、様々な種類のサービスをホストするために、世界 6 大陸に渡って数千ものエッジ サイトを保有しています。それらのサイトでは、検索・コミュニケーション・ストレージといった幅広い製品を利用するお客様やエンタープラズの顧客に応えるべく、多くの対話的な (レイテンシーにシビアな) サービスをホストしています。エッジ ロケーションは、ユーザーからの通信が Microsoft のネットワークに入る最初の窓口となることから、世界中に広がるエッジのおかげで、ユーザーは非常に低いレイテンシーで Microsoft のサービスに到達することが出来ます。

従来の研究成果から、レイテンシーの増加に伴ってユーザーの定着度合いが急激に低くなることが知られています。レイテンシが低いことの重要性を知るために、何も論文を読む必要はなく、必要なのは単にスマホやパソコンから誰かにビデオ通話をかけることだけです。低レイテンシやラウンド トリップ タイム (Round Trip Time; RTT) の大切さは、特にレイテンシが高い時に顕著に現れます。ビデオ通話の音声や映像がラグだらけで、自然な会話が阻害されてしまうのです。実際、[Skype を使った過去の調査](https://www.microsoft.com/en-us/research/publication/via-improving-internet-telephony-call-quality-using-predictive-relay-selection/) からも、良い UX にはネットワークの重要性が明らかになっています。

上で挙げた例は、ネットワークの低レイテンシの重要性を示しています。それと同時に、どうにも回避できない低速化がネットワークに見られた場合、システムがそれを認識して、できるだけ早く修復できる必要が有ることもわかります。ここで登場するのが BlameIt のテクノロジーです。BlameIt は、クライアントからクラウド / その戻りの経路に含まれる自律システム (Autonomous System; AS) のうち、どの AS に問題があるのか、正確にかつリアルタイムに特定しようとします。[SIGCOMM 2019 で発表した “Zooming in on Wide-area Latencies to a Global Cloud Provider" というタイトルの論文](https://www.microsoft.com/en-us/research/publication/zooming-in-on-wide-area-latencies-to-a-global-cloud-provider/) で、具体的に BlameIt がどのように問題の AS を特定するか説明しています。この成果は、Microsoft Research と Azure Networking チームの長年の協力の末、実を結んだものです。

{{< figure src="https://www.microsoft.com/en-us/research/uploads/prod/2019/08/blameit_figure_1.png" caption="" >}}

## クライアント=クラウド間のレイテンシと AS の役割を理解する

ユーザーは、Microsoft のネットワークとの直接的なピアリング経由か、複数の AS を経由することで Azure にアクセスします (なお、人によっては、AS を「ホップ」と呼ぶことがあります)。Azure のエッジサイトが世界中に広がっていることは、クライアント AS とクラウド間のホップ AS が少ないことを意味するものの、クライアント側でレイテンシが増加することはあります。そのような状況で、ユーザーとしてはどの AS  が "犯人" なのか、より正確には、経路中のどの AS がレイテンシー低下を引き起こしているのか知りたいはずです。

障害 AS の場所を特定することは非常に重要です。RTT の低下には多くの原因が考えられます。

* サーバーへの高負荷によって生じた、クラウド ネットワークでの輻輳
* クライント側 ISP のメンテナンスに起因する問題
* トランジット AS 内部での経路の更新

できる限り迅速に障害 AS を特定することで、Azure のネットワーク オペレータが egress の AS を切り替えるなどして、ユーザーへのインパクトを最小限に留める事ができます。ただし、重要なのは障害 AS の特定を正確かつ迅速に行わなければならない点です。この数年で DC 間や DC 内通信は非常に進歩しており、クライント=クラウド間の通信コストは、相対的にクラウド サービスのボトルネックになりつつあることにも注意を向ける必要があるでしょう。

## 待て待て、それ誰か前にやってないの？

なかなか鋭いですね。インターネットの end-to-end 通信において、パフォーマンス低下を各 AS の寄与に分解する問題は、一部のインターネット コミュニティで長年の興味対象となっています。既存手法は、パッシブ型 / アクティブ型という 2 つのカテゴリーに大別することができますが、両カテゴリーの中核には課題があります。それは、AS 構造が単一のエンティティによって決定されるものではないという難しさを克服することです。

{{< figure src="https://www.microsoft.com/en-us/research/uploads/prod/2019/08/blameit_figure_2.png" caption="" >}}

パッシブ型の方法では、end-to-end のレイテンシを測定し、各 AS のレイテンシへの寄与を解きます (数学的に言えば、例えば、線形方程式を利用します)。しかしながら、情報を十分に収集することは多くの場合で難しく、その場合、不定方程式を解かざるを得ません。アクティブ型の方法においても、能動的に打ち続けるプローブに依存することから、測定のコストが非常に高いという問題があります。コストの高い手法は、Microsoft のような大規模ネットワークにはスケールしません。

## BlameIt: 良いとこ取りのハイブリッド構成

BlameIt では、2 段階のアプローチを採用しています。つまり、測定オーバーヘッドが小さいパッシブ型の分析と、より障害特定能力に優れたアクティブ型のプローブを組み合わせます。

{{< figure src="https://www.microsoft.com/en-us/research/uploads/prod/2019/08/Blamelt_08_2019_SiteR_1400x788-e1565217136579.png" caption="" >}}

**Phase 1:** パッシブ型で収集した TCP ハンドシェイクのデータだけでは、障害 AS を特定するには至りませんが、障害発生ポイントが「クラウド」「中間」「クライアント」のいずれの AS セグメントに存在するか絞り込むには十分です。

**Phase 2:** 「中間」の AS に障害が発生したと Phase 1 で判定され、さらにインパクトの大きい障害と判定された時だけ、BlameIt はアクティブ型プローブ (traceroute) を Azure Front Door から送信します。 

BlameIt は従来手法での落とし穴をどのように回避したのでしょうか？抽象的に言えば、BlameIt は 2 つの主要なドメイン知識 (経験的に知られている事実) を活用します。ひとつは、障害発生時には通信経路の 1 つの AS のみが障害状態であり、複数の AS が同時に障害を起こすことはないということ。二つ目は、より大きな範囲で障害が起きているよりも、小さな範囲で障害が起きている確率のほうが高いということです。例えば、クラウドに接続しているすべてのクライアントで RTT 値が悪い場合は、クラウドに障害が起きている可能性が高いです（すべてのクライアントが同時に不良となっているとは考えにくい）[^1]。

[^1]: 複数仮説が考えられる時、よりシンプルに説明する仮説を採用するこの戦略は、統計分析の世界では「オッカムの剃刀」として知られています。

## BlameIt は現在 Azure で動いています!

Azure のエッジサイトでは、分析用のクラスターで BlameIt を定期的に実行し、継続的に RTT ストリームの収集および集約を行っています。分析の結果に応じて、オペレーターに優先順位付きのアラートが飛んだり、クライアントへの traceroute (アクティブ型プローブ) が自動的にトリガーされます。また、BlameIt の詳細な出力は、調査を容易にするためにオペレーターにも提供されます。

{{< figure src="https://www.microsoft.com/en-us/research/uploads/prod/2019/08/BlameIt-Blog-2nd-Image_08_2019_Site_1400x788-e1565216438287.png" caption="" >}}

BlameIt によって障害と判定された AS を、人力で報告された 88 のインシデントと比較したところ、すべてのインシデントの障害を正しく特定できたことが明らかになりました。さらに、BlameIt の選択的なアクティブ型プローブは、アクティブ型プローブのみに依存する従来手法よりも、traceroute 実行回数が 2 桁近く少なくすみました。

現在も BlameIt が動作中であることを活かして、レイテンシを特定するだけでなく、パケットロスや帯域幅低下が発生した場合の原因特定にも焦点を当てたいと考えています。また、BlameIt 機能を使ってより高いレベル (e.g. アプリケーション) のサービス影響も調査し、それに応じて BlameIt を調整したいと考えています。

{{< figure src="https://www.microsoft.com/en-us/research/uploads/prod/2019/08/team_blameit.jpg" caption="" >}}
