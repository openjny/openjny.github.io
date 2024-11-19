---
title: "Velocity 2015, Linux Performance Tools, Brendan Gregg: 方法論"
slug: velocity-2015-linux-perf-tools-methodologies
date: 2020-06-21
categories:
  - Linux
tags:
  - Brendan Gregg
  - Linux
  - パフォーマンス チューニング
isCJKLanguage: true
---

Gregg 先生が 2015 年の Velocity Conference で公演した "Linux Performance Tools, Brendan Gregg" を YouTube で見つけたので、今日ははじめのトラブルシューティングの方法論についてまとめました。

## <!--more-->

## 公演について

- [Linux Performance Tools, Brendan Gregg, part 1 of 2 - YouTube](https://www.youtube.com/watch?v=FJW8nGV4jxY)
- [Linux Performance Tools, Brendan Gregg, part 2 of 2 - YouTube](https://www.youtube.com/watch?v=zrr2nUln9Kk)

> Tutorial by Brendan Gregg of Netflix for O'Reilly Velocity conference 2015 Santa Clara.

スライドは次のページから見れます。

- [Velocity 2015 linux perf tools](https://www.slideshare.net/brendangregg/velocity-2015-linux-perf-tools)

## アンチパターン

まずはじめにトラブルシューティングのアンチパターンを紹介していました。

### Street Light Anti-Method

{{< figure src="2020-06-21-velocity-2015-linux-perf-tools-methodologies/streetlight-anti-method.png" caption="" >}}

- 財布を落とした場所のうち、探しやすい電灯付近しか探さない男の風刺画
- パフォーマンスが悪化した時、多くの人は状況を診断するための観測ツール (observability tools) を使うが、使いやすいものやインターネットでたまたま見かけたものしか使わない
- スコーピングを意識しない診断では真の原因はわからないことが多い

### Drunk Man Anti-Method

- 手当り次第調整できるパラメータをランダムに変更していって、治るまで続ける方法
- 自分の考える Cons
  - 治った理由を説明できない
  - もっと問題を悪くするリスクがある
  - 次のトラブルシューティングに活かすことが出来ない

### Blame Someone Else Anti-Method

よくあるたらい回しの手続き

1. 自分が責任をおっていないコンポーネントをひとつ見つける
2. そのコンポーネントが原因であると仮説をたてる
3. コンポーネントを担当するチームに調査依頼する
4. もし仮説が間違っていたら手順 1 に戻る

## 方法論 (methodorogies)

方法論を説明する前に、Gregg 先生は `./lab002` の名前のユーザー プログラムを実行して、聴衆にトラシューするよう促していました。`vmstat` や `top` などの様々な実行結果を見てみたいという意見がありましたが、結局おかしなところは見つからず、最後に面白い結末でデモは終了します。実は `./lab002` は何も実行していなかったのです。

この例は方法論の重要性を如実に表しています。つまり、やみくみに実行するトラブル シューティングが役に立たないということです。

自分にとってもこれは非常に面白いデモだったので印象に残っています。以下では、発表で紹介があったいくつかの方法論をまとめますが、Gregg 先生の本をみると他にも様々な方法論を体系立てているようなので、そちらも時間があるときに見てみたいですね。

### Problem Statement Method

これは問題のスタートポイントを定めるための方法論。Gregg がサン・マイクロシステムズのサポートをしていた間、チケット起票時に必ず確認していた事項らしい。

1. パフォーマンス問題が発生していると**考えた**きっかけとなったものは何か?
2. **これまで**問題なくシステムが動いていた実績があるか?
3. 最近何か**変わった**ものはないか? (e.g. ソフトウェア、ハードウェア、負荷)
4. パフォーマンス問題は**レイテンシ**や実行時間の観点で表現できるか?
5. その問題は**他の**人やアプリケーションに影響を与えているか?
6. **環境**は何か? (e.g. ソフトウェア、ハードウェア、インスタンスタイプ、バージョン、構成情報)

### Workload Characterizaton Method

ワークロードを定量化して把握するため、4 つの情報を収集する方法論。これで大体の問題は解決するらしい。

- **Who**: 誰が負荷を与えているか (e.g. PID, UDI, IP Address)
- **Why**: なぜ負荷を与える処理が実行されているか (e.g. code path, stack trace)
- **What**: 負荷は何か (e.g. IPOS, tput, type, r/w)
- **How**: 時間が経過すると負荷はどうなっていくか

### USE Method

各リソース (CPU, ディスク、メモリ、etc) で 3 つのメトリックをチェックすれば答えが導かれるという方法論。

- **Utilizaton**: リソースがサービスを提供するのに平均してどれくらい時間がかかったか
- **Saturation**: 提供できない余剰のタスクがリソースにどれくらいあったか (典型的にはキューの長さ)
- **Errors**: エラーイベントの数

逆に言えば、これら以外のメトリックは見なくても良いという安心感をあたえる。これについて、Gregg 氏は「暗黙的な未知 (unknown-unknowns) が 明示的な未知 (known-unknwons) となる」という表現をしている。

例えば、ネットワークのコンポーネント (NIC) で USE Method を適用すると、以下のようになる。

- U: 送信/受信におけるパケットのバイト数
- S: 送信/受信におけるペンディング パケット数
- E: ポリシー以外の理由でドロップされたパケット数

Kubernetes で実際に USE Method を適用してみたという記事があるので、参考になると思う。また、本家の USE Method の解説には推奨される解釈方法などの詳細が記載されている。

- [A Deep Dive into Kubernetes Metrics — Part 2 - FreshTracks.io](https://blog.freshtracks.io/a-deep-dive-into-kubernetes-metrics-part-2-c869581e9f29)
- [The USE Method](http://www.brendangregg.com/usemethod.html)

### Off-CPU Analysis

{{< figure src="2020-06-21-velocity-2015-linux-perf-tools-methodologies/off-cpu-analysis.png" caption="" >}}

USE Method を使えば、沢山のデバイスレベルの問題 (e.g. ネットワーク インターフェイスがビジー状態) を容易に発見できるが、一方でロック競合のような複雑に条件が絡みあっている問題を発見することは出来ない。この時役立つのが Off-CPU Analysis。

Off-CPU Anaysis の観点では、パフォーマンス問題は以下の 2 種類に大別できる。

- On-CPU: スレッドが CPU 上で実行されている時の問題
- Off-CPU: I/O、ロック、タイマ、ページング (スワッピング) のような待ちが発生している時の問題。簡単に言えば `time` コマンドの `{real} - ({user} + {sys})` が長い時の話。

Off-CPU Analysis は Off-CPU のパフォーマンス問題を分析する方法論で、実行状態から外れた I/O 待ち、Block、Idle 状態のスレッドを調査する為に用いられる。

Linux だと eBPF 等のトレーサーで調査が出来るらしいが詳細はわからない。本人の公式ページを見るのが良い。

- [Off-CPU Analysis](http://www.brendangregg.com/offcpuanalysis.html)

### CPU Profile Method

{{< figure src="2020-06-21-velocity-2015-linux-perf-tools-methodologies/flame-graph.png" caption="" >}}

- プロファイラで CPU profile を取得する
- 実行時間が全体のうち 1 %以上のすべてのソフトウェアを理解するのがよい (が、難しい・・・)

Flame Graph と呼ばれる CPU プロファイルを可視化するツールを使って効率的に分析できる。

- [Flame Graphs](http://www.brendangregg.com/flamegraphs.html)
- [perf使ってみた - Qiita](https://qiita.com/saikoro-steak/items/bf066241eeef1141ef5f)
- [perf + Flame Graphs で Linux カーネル内のボトルネックを特定する - ablog](https://yohei-a.hatenablog.jp/entry/20150706/1436208007)


### RTFM Method

パフォーマンス ツールやメトリック等の道具そのものの理解を目的とした方法論。特にソースコードを読んで、実験してみる方法が効果的とのこと。

- Linux の man ページ
- 書籍
- ウェブ検索
- 同僚
- 技術トーク、スライド
- サポート サービス
- ソースコード
- 実験

## 参考文献

- [Linux Performance Tools, Brendan Gregg, part 1 of 2 - YouTube](https://www.youtube.com/watch?v=FJW8nGV4jxY)
- [Linux Performance Tools, Brendan Gregg, part 2 of 2 - YouTube](https://www.youtube.com/watch?v=zrr2nUln9Kk)
- [Brendan Gregg: Overview](http://www.brendangregg.com/overview.html)
