---
title: "[bpf-perf-workshop] lab2: SSH ログイン パフォーマンス"
slug: bpf-perf-workshop-lab2
date: 2021-05-18
categories:
  - Linux
tags:
  - Linux
  - Brendan Gregg
  - パフォーマンスチューニング
  - eBPF
isCJKLanguage: true
---

Brendan Gregg 氏のハンズオン ワークショップ "bpf-perf-workshop" より、SSH 経由のコマンドのパフォーマンスに関する課題 "lab2" をやってみました。

## 課題 <!--more-->

今回の問題はこちら。

[bpf-perf-workshop/lab2.md at master · brendangregg/bpf-perf-workshop](https://github.com/brendangregg/bpf-perf-workshop/blob/master/lab2.md)

> Problem Statement
> Under load, it can take a few seconds to login to your lab system via SSH. Even when idle, it can take 1-2 seconds. Why does it take this long on an idle system, and how can this login time be reduced?

負荷の高いシステムに SSH ログインするとき、ログインに時間がかかる (数秒要することもある) のはなぜ? という課題。

## ラボ環境のセットアップ

この課題は、負荷の高い (under load と表現される) ラボ環境を用意するところから始めなければならない。

"負荷" が意味するところがわからず戸惑ったが、ワークショップのスライドの文脈を読み解くに、おそらく `lab001` を実行させた状態を under load を言っているに違いない。ということで、I/O 負荷を発生させる。なんとなく、`lab001` を 2 つ起動させてみた。

```bash
root@vm-ubuntu: ~# ./bpf-perf-workshop/lab001 &
root@vm-ubuntu: ~# ./bpf-perf-workshop/lab001 &
```

いい感じに負荷みを感じている。

```bash
root@vm-ubuntu:~# uptime
 13:37:40 up  4:23,  6 users,  load average: 3.00, 2.98, 2.68

root@vm-ubuntu:~# cat /proc/pressure/io
some avg10=73.11 avg60=70.48 avg300=72.26 total=11215650634
full avg10=73.10 avg60=70.40 avg300=72.17 total=11194499828

root@vm-ubuntu:~# vmstat -S M 1
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  1      0  14816    100    791    0    0    10   680  124  404  0  1 93  6  0
 0  1      0  14816    100    791    0    0     0  3824  579 1960  0  1 97  2  0
 0  1      0  14816    100    791    0    0     0  3920  619 2020  0  0 98  2  0
 0  1      0  14816    100    791    0    0     0  1920  741 2059  0  1 97  2  0
 0  1      0  14816    100    791    0    0     0  1756  645 1909  1  1 93  6  0

root@vm-ubuntu:~# iostat -xz 1
 avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.00    0.00    0.50   13.35    0.00   86.15

Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
sda              0.00  376.00      0.00   4032.00     0.00   124.00   0.00  24.80    0.00    2.70   0.63     0.00    10.72   2.66 100.00
```

## Before: ssh 経由コマンドのレイテンシ計測

手元のマシンから、ssh 経由の `echo hello` にかかる時間を計測してみる。

```bash
openjny@local-machine:~$ time ssh openjny@<lab-machine> -i id_rsa echo hello
hello

real    0m1.489s
user    0m0.057s
sys     0m0.002s
```

何回か計測してみたけど、たしかに `echo hello` するだけで 1 ~ 数秒の時間がかかっていることがわかる。速いのか遅いのかよくわからないけど、eBPF を使ってボトルネックの特定と高速化を試みるとしましょう。

## 調査方針

今回の分析対象は「生存期間の短いプロセスであり、事前に調査対象の PID がわかっていない」というのが最大の特徴。そのため、数秒おきに stats を出すツール (e.g. vmstat) よりも、**イベント ドリブンな**分析ツールが原因究明の鍵を握りそう。まずは、各コンポーネントで次の確認を進めたい。

- CPU: プロセス/スレッドの誕生と終了、生存期間
- メモリ: ページキャッシュの開放有無
- ファイルシステム、I/O: 新たに `open` された file の有無、ブロックデバイスへの(物理) I/O 発生状況
- ネットワーク: ESTABLISH に要した時間、パケットドロップ/再送の量、トラフィックの発生状況

使えそうな bcc のツールは以下の通り。

- (cpu) execsnoop, exitsnoop
- (memory) drsnoop, shmsnoop
- (filesystem/io) filelife, biosnoop
- (network) sofdsnoop, tcplife, tcpstates, tcpretrans

## ログの収集

収集には以下の bash script を利用した。

```bash
#!/bin/bash

BCC_TOOLS="/home/openjny/bcc/tools"
PREFIX="timeout 15s python3 -u"

# pid
ps -aux | grep ssh[d] > pid_sshd.log

# cpu
$PREFIX $BCC_TOOLS/execsnoop.py -xTU > execsnoop.log &
$PREFIX $BCC_TOOLS/exitsnoop.py --utc > exitsnoop.log &

# memory
$PREFIX $BCC_TOOLS/drsnoop.py > drsnoop.log &
$PREFIX $BCC_TOOLS/shmsnoop.py > shmsnoop.log &

# fs/io
$PREFIX $BCC_TOOLS/filelife.py > filelife.log &
$PREFIX $BCC_TOOLS/biosnoop.py > biosnoop.log &

# network
$PREFIX $BCC_TOOLS/sofdsnoop.py > sofdsnoop.log &
$PREFIX $BCC_TOOLS/tcplife.py > tcplife.log &
$PREFIX $BCC_TOOLS/tcpstates.py > tcpstates.log &
$PREFIX $BCC_TOOLS/tcpretrans.py > tcpretrans.log &

while [ $(cat tcpretrans.log | wc -l) -lt 1 ]; do
       sleep 1
done

echo "Start..."
wait
```

このスクリプトを作成している間に、bcc tools は既定で出力バッフを使うものが多く、リダイレクト時に正常に出力をパイプできない問題に遭遇。バッファが関係していそうなのはすぐわかったのだが、自分の環境では何故か `stdbuf` が効かず、python 側のオプションを利用する方法を発見するまでに時間がかかってしまった…。そして、解決方法は issue ページにあったという :cry:

[Stream Redirection Disables All Output · Issue #905 · iovisor/bcc](https://github.com/iovisor/bcc/issues/905)

採取方法は簡単で、採取スクリプトを `sudo` で実行して "Start..." が表示されてから、`ssh` 経由のコマンド (遅い! と問題になっているやつ) をローカルから実行するだけ。

### 採取後の整形

採取した (イベント ドリブンな) ログはシステム全体を対象として計測されている。このままではログが多すぎるので、対象 `ssh` コマンドの実行に関係のあるプロセスのログだけを抽出したい。まずは、`execsnoop` の結果から、今回の事象によって `sshd` から生成されたすべての (子孫) プロセスをリストアップする。

```py
# extract.py

import pandas as pd
from queue import Queue

EXECSNOOP_LOG = './execsnoop.log'
ROOT_PID = 1442

def canonical_columns(cols):
    return [c for c in cols if not c.startswith('Unnamed:')]

df_exec = pd.read_fwf(EXECSNOOP_LOG)
df_exec = df_exec[canonical_columns(df_exec.columns)]

def get_child_pids(df, root_pid):
    q = Queue()
    q.put(root_pid)
    child_pids = list()

    while not q.empty():
        pid = q.get()
        child_pids.append(pid)
        childs = set(df[df['PPID'] == pid]['PID'])
        for c in childs:
            q.put(c)
    
    return child_pids

pid_list = get_child_pids(df_exec, ROOT_PID)
print('|'.join([str(p) for p in pid_list]))
```

こいつを使って、フィルターが必要そうなログはフィルタリングをしておく。

```bash
#!/bin/bash

pids=$(python3 extract.py)

mkdir filtered
cat execsnoop.log | awk '{ if ($4 ~ /'$pids'/) { print } }' > filtered/execsnoop.log
cat exitsnoop.log | awk '{ if ($3 ~ /'$pids'/) { print } }' > filtered/exitsnoop.log
cat drsnoop.log | awk '{ if ($2 ~ /'$pids'/) { print } }' > filtered/drsnoop.log
cat shmsnoop.log | awk '{ if ($1 ~ /'$pids'/) { print } }' > filtered/shmsnoop.log
cat filelife.log | awk '{ if ($2 ~ /'$pids'/) { print } }' > filtered/filelife.log
cat biosnoop.log | awk '{ if ($3 ~ /'$pids'/) { print } }' > filtered/biosnoop.log
```

## 分析

### CPU 観点での調査

と、ここまで来て初めて気づいたが、フィルタリングが完全でないことが発覚。というのも、`execsnoop` で検知できていないプロセスの複製/実行があることで、`sshd` の子孫プロセスの列挙が不完全なものになってしまっていた。ただ、それでもいくつか重要なことがわかった。

まず、問題のコマンドが実行されたのは 14:28:58 であり、コマンド処理を担当するプロセスの PID は 27805 として生成されたことがわかる。時刻は大事な情報。

```bash
$ cat execsnoop.log | grep /usr/sbin/sshd
14:28:58 0     sshd             27805  1442     0 /usr/sbin/sshd -D -R
```

次に、多数の (少なくとも 60 以上の) プロセスが生成されている。そしてここには `/etc/update-motd.d/*` のプロセスが多く含まれる。

```bash
$ cat filtered/execsnoop.log | wc -l
60

$ cat filtered/execsnoop.log | grep 'update-motd.d'
14:28:58 0     run-parts        27820  27819    0 /bin/run-parts --lsbsysinit /etc/update-motd.d
14:28:58 0     00-header        27821  27820    0 /etc/update-motd.d/00-header
14:28:58 0     10-help-text     27825  27820    0 /etc/update-motd.d/10-help-text
14:28:58 0     50-landscape-sy  27826  27820    0 /etc/update-motd.d/50-landscape-sysinfo
14:28:58 0     50-motd-news     27832  27820    0 /etc/update-motd.d/50-motd-news
14:28:58 0     88-esm-announce  27837  27820    0 /etc/update-motd.d/88-esm-announce
14:28:58 0     90-updates-avai  27838  27820    0 /etc/update-motd.d/90-updates-available
14:28:58 0     91-contract-ua-  27840  27820    0 /etc/update-motd.d/91-contract-ua-esm-status
14:28:58 0     91-release-upgr  27841  27820    0 /etc/update-motd.d/91-release-upgrade
14:28:58 0     92-unattended-u  27849  27820    0 /etc/update-motd.d/92-unattended-upgrades
14:28:58 0     95-hwe-eol       27850  27820    0 /etc/update-motd.d/95-hwe-eol
14:28:58 0     97-overlayroot   27866  27820    0 /etc/update-motd.d/97-overlayroot
14:28:58 0     98-fsck-at-rebo  27870  27820    0 /etc/update-motd.d/98-fsck-at-reboot
14:28:58 0     98-reboot-requi  27876  27820    0 /etc/update-motd.d/98-reboot-required
```

`/etc/update-motd.d` は Ubuntu での MOTD (message of the day) 用スクリプトが格納されているパスなので、ssh との関連性は確かに高い。ここでわかった重要な事実は、ssh 経由でコマンドを実行した場合でも、(表示はされないのにも関わらず) MOTD が実行されるということだ。これは無駄な処理だと考えられる。

生存期間の観点では特記すべき点は見られなかった。最も生存期間が長いプロセスは以下 3 つで、0.04 秒程度。ただ、それ以外は特に生存期間が長いプロセスはなく、まんべんなく短い実行時間のプロセスが多数発生していたと考えるのが良さそう。

```bash
$ cat filtered/exitsnoop.log
TIME-UTC     PCOMM            PID    PPID   TID    AGE(s)  EXIT_CODE
...
14:28:58.722 lsb_release      27843  27842  27843  0.04    0
14:28:58.722 cut              27844  27842  27844  0.04    0
14:28:58.722 91-release-upgr  27842  27841  27842  0.04    0
```

### メモリ観点の調査

特に仮想メモリの飽和は観測されていないので、一旦問題ないと見なしてよいと思う。

```bash
$ cat drsnoop.log
COMM           PID     LAT(ms) PAGES

$ cat shmsnoop.log
PID    COMM                SYS              RET AR

$ dmesg -T | egrep 'oom|Out of memory'
```

### ファイルシステム、I/O 観点の調査

まずは VFS で作成され削除された file 一覧を見てみる。`systemd` でログイン時に生成されるものくらいしかなさそう。

```bash
$ cat filelife.log
TIME     PID    COMM             AGE(s)  FILE
14:28:58 27865  rm               0.00    tmp.2mxHTbBPCU
14:28:58 1      systemd          0.29    session-1245.scope
14:28:58 1352   systemd-logind   0.00    1245
14:28:58 469    systemd-journal  0.00    9:339183
14:28:58 469    systemd-journal  0.29    9:339144
14:28:58 1      systemd          0.30    user-1001.slice
14:28:58 1352   systemd-logind   0.00    1001
```

物理デバイスへの I/O も存在しない。ファイルの read や write で時間がかかってるのではないと考えられる。

```bash
$ cat filtered/biosnoop.log

# 念の為、目 grep で非対象 PID を除外して調査も実施
$ cat biosnoop.log | awk '{ if ($3 !~ /0|385|17836|17841|17829/) { print } }'

# 定常的に物理 I/O を発生させている PID を列挙するには以下を実行
# tmp=$(mktemp)
# timeout 5s biosnoop.py > $tmp
# cat $tmp | awk '{print $3}' | sed '1d' | sort | uniq | paste -sd'|'
```

### ネットワーク観点の調査

tcplife で TCP コネクション確立/終了のライフサイクルを見てみる。22 ポートとの通信が一つ存在した。送受信バイト数もそれぞれ 2 KB と少なめ。

```bash
$ cat tcplife.log
PID   COMM       LADDR           LPORT RADDR           RPORT TX_KB RX_KB MS
0     swapper/3  10.0.0.4        22    <local-ip-addr> 4146      2     2 659.94
```

ここで、生成されているプロセス数がここまで多いと、他にも通信を発生させてるプロセスはあるのでは? という疑問が発生。このログからだけだとなんとも言えないが、何度か `tcplife` のログをとってると、当該コマンドを実行して発生する TCP コネクションは 1 本だけであることがわかった。安心して、この TCP コネクションについて調査を進めるとする。

SYN を送ってから ESTAB になるまでの時間 (3-way handshake latency) は 0.012 秒。全く問題ない。

```bash
cat tcpstates.log | grep ffff8cf3ab844ec0 

SKADDR           C-PID C-COMM     LADDR           LPORT RADDR           RPORT OLDSTATE    -> NEWSTATE
ffff8cf3ab844ec0 0     swapper/3  0.0.0.0         22    0.0.0.0         0     LISTEN      -> SYN_RECV    0.000
ffff8cf3ab844ec0 0     swapper/3  10.0.0.4        22    126.149.198.88  4146  SYN_RECV    -> ESTABLISHED 0.012
ffff8cf3ab844ec0 27805 sshd       10.0.0.4        22    126.149.198.88  4146  ESTABLISHED -> FIN_WAIT1   613.626
ffff8cf3ab844ec0 0     swapper/3  10.0.0.4        22    126.149.198.88  4146  FIN_WAIT1   -> CLOSING     11.181
ffff8cf3ab844ec0 0     swapper/3  10.0.0.4        22    126.149.198.88  4146  CLOSING     -> CLOSE       35.128
```

再送も存在していないので、ネットワーク観点でボトルネックの兆候は見られない。

```bash
$ cat tcpretrans.log
Tracing retransmits ... Hit Ctrl-C to end
TIME     PID    IP LADDR:LPORT          T> RADDR:RPORT          STATE
```

### 一次見解

当該コマンドは、仮想メモリ、ファイルシステム、I/O、ネットワークの観点ではボトルネックとなる程の処理を観測していない。最も可能性があるのは、大量にプロセスが生成されていることで、特に motd によって無駄なログイン処理が発生していることが示唆された。

## 対応策

`systemd` の動作を調べるのは時間がかかりそうだったので、`/etc/update-motd.d` 自体を削除するという単純な方法で対応をしてみる。

```bash
root@vm-ubuntu:/etc# mv /etc/update-motd.d/ /etc/update-motd.d.old
```

### After: ssh 経由コマンドのレイテンシ計測

対応後のコマンド実行レイテンシを何度か計測してみた。確かに 1 秒以上時間がかかるようなことはなくなり、改善が見られた。

```bash
openjny@local-machine:~$ time ssh openjny@<lab-machine> -i id_rsa echo hello
hello

real    0m0.598s
user    0m0.034s
sys     0m0.012s
```

また、`execsnoop` で実行されるプロセス数をカウントしてみると、対応前 60 以上あった子孫プロセスが、10 程度に抑えられていることも確認できた。

## まとめ

今回の課題では、非常に生存時間が短く、かつ事前にわかっているのは `fork` 元のプロセス ID だけ、というアプリケーションのレイテンシを増加させている原因を調査しました。WEB アプリケーションへの GET 要求等、ネットワーク越しの処理はおそらくこのようなシナリオに該当するのだろう。

そして、`strace` や `tcpdump` 等が使えないセンシティブなサーバー環境でも、コンポーネントごとにワークロード計測ができることを確認できました。十分とは言えないかもしれないけど、実際にレイテンシを削減することのできる対応を考えつくことが出来たので、最低限のところまでは対応できたと思います。

ただ、`systemd` の動作がわかっていればよりプロセス間の関係、生成されたプロセスの意味が解釈しやすかったのだろうと思うと、やはり内部アーキテクチャを知っていることは重要であることを改めて感じた。また、今回は bcc だけで乗り切ったけど、`bpftrace` でだけ提供されているネットワーク系ツール等も発見したので、今後活用していきたい。
