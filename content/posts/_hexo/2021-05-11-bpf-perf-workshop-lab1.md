---
title: "[bpf-perf-workshop] lab1: レイテンシ調査"
slug: bpf-perf-workshop-lab1
date: 2021-05-11
categories:
  - Linux
tags:
  - Linux
  - Brendan Gregg
  - パフォーマンスチューニング
  - eBPF
  - bcc
isCJKLanguage: true
---

Brendan Gregg 氏のハンズオン ワークショップ "bpf-perf-workshop" より、最初の課題 (アプリケーション レイテンシの調査課題) "lab2" をやってみました。

## 課題 <!--more-->

今回の問題はこちら。

[bpf-perf-workshop/lab1.md at master · brendangregg/bpf-perf-workshop](https://github.com/brendangregg/bpf-perf-workshop/blob/master/lab1.md)

> Problem Statement
> An application has higher-than expected latency, including latency outliers. Why, and how can performance be improved?

思ったようにパフォーマンスが出ない (i.e. 実行レイテンシが大きい) アプリケーション `./lab001` に対して、その理由と改善方法を調査しろ、という課題。

## 60秒分析

まずは、有名な 60 秒分析で CPU、Memory、FileSystem/Disks、Network のいずれがボトルネックになっているかフィーリングを掴む。

[Linux Performance Analysis in 60,000 Milliseconds | by Netflix Technology Blog | Netflix TechBlog](https://netflixtechblog.com/linux-performance-analysis-in-60-000-milliseconds-accc10403c55)

```
root@vm-ubuntu:~# uptime
 12:31:53 up 30 min,  3 users,  load average: 1.99, 1.37, 0.65
```

`lab001` を実行した後の `uptime` の結果が上。後半 3 つの値は、それぞれ直近 1, 5, 15 分での load average (移動指数平均) を表している。

Linux での load average は、TASK_RUNNING + TASK_UNINTERRUPTIBLE 状態なタスク数の総和を表してることに注意すれば、`lab001` を実行したことでこれらタスクの数が増えてきていることが確認できる。

```
root@vm-ubuntu:~# dmesg | tail
[   13.055942] audit: type=1400 audit(1620907273.224:11): apparmor="STATUS" operation="profile_load" profile="unconfined" name="/usr/lib/snapd/snap-confine" pid=841 comm="apparmor_parser"
[   18.327127] IPv6: ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[   23.839985]  sda: sda1
[   26.123281] EXT4-fs (sda1): mounted filesystem with ordered data mode. Opts: (null)
[   26.588156] new mount options do not match the existing superblock, will be ignored
[   57.834818] hv_balloon: Max. dynamic memory size: 16384 MB
[  109.372614] SGI XFS with ACLs, security attributes, realtime, no debug enabled
[  109.466644] JFS: nTxBlock = 8192, nTxLock = 65536
[  109.531712] ntfs: driver 2.1.32 [Flags: R/O MODULE].
[  109.685490] QNX4 filesystem 0.2.3 registered.
```

`dmesg -T` とか見てみるとよく分かるけど、`lab001` を起動してからは特に異常が発生した様子はない。

```
root@vm-ubuntu:~# vmstat -S M 1
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  1      0  14846     88    786    0    0    77   342   56  187  1  0 96  3  0
 0  1      0  14846     88    786    0    0     0  1696  556 1637  0  0 97  2  0
 0  1      0  14846     88    786    0    0     0  3712  372 1641  0  0 80 19  0
 0  1      0  14846     88    786    0    0     0  1776  355 1681  0  0 76 24  0
 0  1      0  14846     88    786    0    0     0  3788  540 1747  0  1 93  6  0
```

- UNINTERRUPTIBLE_SLEEP 状態なタスクが常に 1 つある
- User (us), System (sy) 時間ともにほとんど消費していない
- I/O 待ち (wa) 時間が比較的多い (24 %を占めるときもある)
- Swap In/Out はゼロで問題なし
- 空きメモリも余裕がある

以上の点から、CPU やメモリでのボトルネックではなく、I/O でのボトルネック説が疑われる。

```
root@vm-ubuntu:~# mpstat -P ALL 1
Linux 5.4.0-1047-azure (vm-ubuntu)      05/13/21        _x86_64_        (4 CPU)

12:43:52     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
12:43:53     all    0.25    0.00    0.50   13.07    0.00    0.00    0.00    0.00    0.00   86.18
12:43:53       0    0.00    0.00    0.00   51.52    0.00    0.00    0.00    0.00    0.00   48.48
12:43:53       1    0.00    0.00    1.00    2.00    0.00    0.00    0.00    0.00    0.00   97.00
12:43:53       2    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
12:43:53       3    0.00    0.00    1.01    0.00    0.00    0.00    0.00    0.00    0.00   98.99

12:43:53     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
12:43:54     all    0.25    0.00    1.00    2.99    0.00    0.00    0.00    0.00    0.00   95.76
12:43:54       0    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
12:43:54       1    1.00    0.00    0.00    3.00    0.00    0.00    0.00    0.00    0.00   96.00
12:43:54       2    0.00    0.00    1.98    7.92    0.00    0.00    0.00    0.00    0.00   90.10
12:43:54       3    0.00    0.00    1.00    0.00    0.00    0.00    0.00    0.00    0.00   99.00

12:43:54     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
12:43:55     all    0.00    0.00    0.50    1.50    0.00    0.00    0.00    0.00    0.00   97.99
12:43:55       0    0.00    0.00    0.00    0.00    0.00    1.00    0.00    0.00    0.00   99.00
12:43:55       1    0.00    0.00    1.00    3.00    0.00    0.00    0.00    0.00    0.00   96.00
12:43:55       2    0.00    0.00    1.00    4.00    0.00    0.00    0.00    0.00    0.00   95.00
12:43:55       3    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
```

論理 CPU ごとに負荷がばらけているわけではなく、CPU#0 で I/O Wait が発生するタスクが実行されている模様。

```
root@vm-ubuntu:~# pidstat 1
Linux 5.4.0-1047-azure (vm-ubuntu)      05/13/21        _x86_64_        (4 CPU)

12:45:12      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
12:45:13        0        11    0.99    0.00    0.00    0.00    0.99     3  rcu_sched
12:45:13        0       380    0.00    1.98    0.00    0.00    1.98     2  jbd2/sdb1-8
12:45:13        0      5689    0.00    0.99    0.00    0.00    0.99     1  lab001
12:45:13        0      7009    0.99    0.00    0.00    0.00    0.99     3  pidstat

12:45:13      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
12:45:14        0       380    0.00    1.00    0.00    0.00    1.00     2  jbd2/sdb1-8
12:45:14        0      5689    0.00    1.00    0.00    0.00    1.00     1  lab001
12:45:14        0      7009    0.00    1.00    0.00    0.00    1.00     3  pidstat

12:45:14      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
12:45:15        0       380    0.00    2.00    0.00    1.00    2.00     2  jbd2/sdb1-8
12:45:15        0      5689    0.00    1.00    0.00    0.00    1.00     1  lab001
```

pidstat が表示するパーセンテージは、全 CPU の総和である点に注意。あまり有益な情報は得られていない。


```
root@vm-ubuntu:~# iostat -xz 1

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.25    0.00    0.00    1.76    0.00   97.99

Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
sdb              0.00  325.00      0.00   1748.00     0.00   112.00   0.00  25.63    0.00    3.00   0.68     0.00     5.38   3.06  99.60

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.00    0.00    0.25    1.51    0.00   98.24

Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
sdb              0.00  262.00      0.00   3424.00     0.00    86.00   0.00  24.71    0.00    3.79   0.80     0.00    13.07   3.83 100.40

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.00    0.00    0.25   12.56    0.00   87.19

Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
sdb              0.00  276.00      0.00   1472.00     0.00    92.00   0.00  25.00    0.00    3.59   0.78     0.00     5.33   3.64 100.40
```

`/dev/sdb`  に対して、Write 命令が多く見られる。具体的には、以下の通り:

- 秒あたりの Read リクエスト完了数 (r/s) はゼロ
- 秒あたりの Write リクエスト完了数 (w/s) は 300 近い
- 秒あたりの Read セクタ量 (rkB/s) はゼロ
- 秒あたりの Write セクタ量 (wkB/s) は数千 Kbyte 近い

また、Write 側のキューサイズ (wavgqu-sz) が恒常的に 1 を超えた値を記録しているので、物理デバイス I/O の飽和が発生していることが、ここからもわかる。

なお、Write リクエストのマージ率 (%wrqm) が 25% と比較的高いことから、同じようなセクタへの書き込みが多く発生していそうな匂いがする。

```
root@vm-ubuntu:~# free -m
              total        used        free      shared  buff/cache   available
Mem:          16013         295       14840           0         877       15431
Swap:             0           0           0
```

free + buff/cache ないしは available に全然余裕があるので、問題なし。`dmseg` で `oom-killer` も観測していない。

```
root@vm-ubuntu:~# sar -n DEV 1
Linux 5.4.0-1047-azure (vm-ubuntu)      05/13/21        _x86_64_        (4 CPU)

13:04:38        IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s   %ifutil
13:04:39           lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
13:04:39         eth0      1.00      0.00      0.06      0.00      0.00      0.00      0.00      0.00

13:04:39        IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s   %ifutil
13:04:40           lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
13:04:40         eth0      1.00      2.00      0.06      1.49      0.00      0.00      0.00      0.00

13:04:40        IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s   %ifutil
13:04:41           lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
13:04:41         eth0      1.00      1.00      0.06      0.60      0.00      0.00      0.00      0.00
```

使用率 (%ifutil) を見ても全然余裕があるし、実際発生しているパケットの数や量 (*pck/s, *kB/s) も少ない。

```
root@vm-ubuntu:~# sar -n TCP,ETCP 1
Linux 5.4.0-1047-azure (vm-ubuntu)      05/13/21        _x86_64_        (4 CPU)

13:07:05     active/s passive/s    iseg/s    oseg/s
13:07:06         0.00      0.00      1.00      0.00

13:07:05     atmptf/s  estres/s retrans/s isegerr/s   orsts/s
13:07:06         0.00      0.00      0.00      0.00      0.00

13:07:06     active/s passive/s    iseg/s    oseg/s
13:07:07         0.00      0.00      1.00      2.00

13:07:06     atmptf/s  estres/s retrans/s isegerr/s   orsts/s
13:07:07         0.00      0.00      0.00      0.00      0.00

13:07:07     active/s passive/s    iseg/s    oseg/s
13:07:08         0.00      0.00      1.00      2.00

13:07:07     atmptf/s  estres/s retrans/s isegerr/s   orsts/s
13:07:08         0.00      0.00      0.00      0.00      0.00
```

念の為みてみたが、TCP レベルの stats でも問題ない。

```
root@vm-ubuntu:~# top

top - 13:08:08 up  1:07,  4 users,  load average: 2.05, 2.01, 1.90
Tasks: 157 total,   1 running,  89 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.2 us,  0.6 sy,  0.0 ni, 92.6 id,  6.5 wa,  0.0 hi,  0.2 si,  0.0 st
KiB Mem : 16398260 total, 15191744 free,   306500 used,   900016 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 15798152 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
  380 root      20   0       0      0      0 D   1.3  0.0   0:33.53 jbd2/sdb1-8
 5689 root      20   0    6564   3016   1136 D   1.0  0.0   0:30.62 lab001
  418 root       0 -20       0      0      0 I   0.3  0.0   0:04.96 kworker/0:1H-kb
 8713 root      20   0   44560   3988   3344 R   0.3  0.0   0:00.05 top
    1 root      20   0   78000   9032   6572 S   0.0  0.1   0:02.95 systemd
```

`D` (UNINTERRUPTIBLE_SLEEP) なプロセス 2 つが top の上位にきているので、こいつらが I/O (write) を占領していると考えるのが妥当そう。


## bcc tools

上記の 60 秒 (自分がやると数分かかる) 分析によって、PID=5689 の `lab001` が　I/O Write を大量に発行しているために、システムに負荷がかかっている可能性が高いことがわかった。
続いて、bcc の一般的なツールを使って、更に詳細に分析していくことにする。

[bcc/tutorial.md at master · iovisor/bcc](https://github.com/iovisor/bcc/blob/master/docs/tutorial.md#1-general-performance)

### execsnoop

```
root@vm-ubuntu:~/bcc/tools# ./execsnoop.py
PCOMM            PID    PPID   RET ARGS
pgrep            9213   2672     0 /usr/bin/pgrep -U omsagent omiagent
sh               9214   2672     0 /bin/sh -c /opt/omi/bin/omicli wql root/scx "SELECT PercentUserTime, PercentPrivilegedTime, UsedMemory, PercentUsedMemory FROM SCX_UnixProc
omicli           9216   9214     0 /opt/omi/bin/omicli wql root/scx SELECT PercentUserTime, PercentPrivilegedTime, UsedMemory, PercentUsedMemory FROM SCX_UnixProcessStatisticalInformation where Ha
grep             9217   9214     0 /bin/grep =
sh               9219   2672     0 /bin/sh -c /opt/omi/bin/omicli wql root/scx "SELECT PercentUserTime, PercentPrivilegedTime, UsedMemory, PercentUsedMemory FROM SCX_UnixProc
```

特に 5689 から child process が生成されているわけではない。

### opensnoop

```
root@vm-ubuntu:~/bcc/tools# ./opensnoop.py -p $(pgrep -nx lab001)
PID    COMM               FD ERR PATH
```

新たに file を open している訳ではない


### ext4slower (or btrfs*, xfs*, zfs*)

```
root@vm-ubuntu:~/bcc/tools# ./ext4slower.py
Tracing ext4 operations slower than 10 ms
TIME     COMM           PID    T BYTES   OFF_KB   LAT(ms) FILENAME
13:22:38 lab001         5689   S 0       0          10.15 lab001.log
13:22:38 lab001         5689   S 0       0          11.70 lab001.log
13:22:39 lab001         5689   S 0       0          11.76 lab001.log
13:22:39 lab001         5689   S 0       0          10.42 lab001.log
13:22:39 lab001         5689   S 0       0          10.02 lab001.log
```

同じ path の file に対して、`S` の種別のオペレーションが多発している。`ext4slower.py` の実装を見ると、Type は以下のように定義されている。

- `R`: read
- `W`: write
- `O`: open
- `S`: fsync

つまり、1 秒間に数回の高頻度で fsync が実施されていることがわかる。

### biolatency

```
root@vm-ubuntu:~/bcc/tools# ./biolatency.py -D -Q
Tracing block device I/O... Hit Ctrl-C to end.
^C

disk = b'sdb'
     usecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 39       |****                                    |
        64 -> 127        : 356      |****************************************|
       128 -> 255        : 316      |***********************************     |
       256 -> 511        : 169      |******************                      |
       512 -> 1023       : 74       |********                                |
      1024 -> 2047       : 16       |*                                       |
      2048 -> 4095       : 4        |                                        |
      4096 -> 8191       : 258      |****************************            |
      8192 -> 16383      : 210      |***********************                 |
     16384 -> 32767      : 12       |*                                       |
     32768 -> 65535      : 1        |                                        |
```

Disk queue に入ってから完了するまでのレイテンシー分布を表示。分布が二峰になっているので、レイテンシーが遅いほうの分布は特定プログラム (i.e. lab001) による影響と仮設できる。

### biosnoop

```
root@vm-ubuntu:~/bcc/tools# ./biosnoop.py
TIME(s)     COMM           PID    DISK    T SECTOR     BYTES  LAT(ms)
0.000000    jbd2/sdb1-8    380    sdb     W 2406576    4096      3.21
0.000348    lab001         5689   sdb     W 9009528    4096      0.21
0.000524    jbd2/sdb1-8    380    sdb     W 2406584    8192      0.14
0.004578    ?              0              R 0          0         4.00
0.007575    jbd2/sdb1-8    380    sdb     W 2406600    4096      2.96
0.007825    lab001         5689   sdb     W 9009528    4096      0.17
0.007917    jbd2/sdb1-8    380    sdb     W 2406608    8192      0.06
```

やはり lab001 による Write リクエストが多く発生している。ext4 用のジャーナリングシステムである `jdb2` が連動していること、lab001 が発行する wirte のサイズが 4096 であることを考慮して、以下のように推測できる:

- lab001 が頻繁に書き込みしているファイルシステムは ext4 であり、その block size はデフォルトの 4096 byte である。

ファイルシステムに疎いので、また別の機会に ext4 と jdb2 について調べてみたい。

### cachestat

```
root@vm-ubuntu:~/bcc/tools# ./cachestat.py
    HITS   MISSES  DIRTIES HITRATIO   BUFFERS_MB  CACHED_MB
       0        0      720    0.00%           93        782
     132        0      211  100.00%           93        782
       0        0      724    0.00%           93        782
     106        0      210  100.00%           93        782
       0        0      716    0.00%           93        782
     112        0      220  100.00%           93        782
       0        0      708    0.00%           93        782
```

ファイルシステムでのキャッシュヒット率には問題はなし。

### tcpconnect

```
root@vm-ubuntu:~/bcc/tools# ./tcpconnect.py
Tracing connect ... Hit Ctrl-C to end
PID    COMM         IP SADDR            DADDR            DPORT
1628   python3      4  10.0.0.4         168.63.129.16    80
1628   python3      4  10.0.0.4         168.63.129.16    32526
1628   python3      4  10.0.0.4         168.63.129.16    80
1628   python3      4  10.0.0.4         169.254.169.254  80
1628   python3      4  10.0.0.4         168.63.129.16    80
```

Azure VM でホストした Ubuntu マシンだったので、管理用エージェント (waagent) が仮想 IP と通信している様子が見えた。それ以外に怪しい点はなし。

### tcpaccept

```
root@vm-ubuntu:~/bcc/tools# ./tcpaccept.py
PID     COMM         IP RADDR            RPORT LADDR            LPORT
```

passive TCP コネクション (accept 経由の TCP コネクション確立) は特に発生なし。

### tcpretrans

```
root@vm-ubuntu:~/bcc/tools# ./tcpretrans.py
Tracing retransmits ... Hit Ctrl-C to end
TIME     PID    IP LADDR:LPORT          T> RADDR:RPORT          STATE
```

TCP コネクションの再送もなし。

### runqlat

```
root@vm-ubuntu:~/bcc/tools# ./runqlat.py
Tracing run queue latency... Hit Ctrl-C to end.
^C
     usecs               : count     distribution
         0 -> 1          : 200      |**                                      |
         2 -> 3          : 779      |*********                               |
         4 -> 7          : 1761     |********************                    |
         8 -> 15         : 3433     |****************************************|
        16 -> 31         : 1086     |************                            |
        32 -> 63         : 91       |*                                       |
        64 -> 127        : 649      |*******                                 |
       128 -> 255        : 9        |                                        |
       256 -> 511        : 3        |                                        |
       512 -> 1023       : 3        |                                        |
      1024 -> 2047       : 1        |                                        |
      2048 -> 4095       : 1        |                                        |
```

ran queue レイテンシの分布を見ても、queue 内で長い間待たされている Task はほぼないので、CPU の飽和は認められない。

## 答え合わせ

実行していたアプリケーションのソースコードは下記に存在する。

[bpf-perf-workshop/lab001.c at master · brendangregg/bpf-perf-workshop](https://github.com/brendangregg/bpf-perf-workshop/blob/master/src/lab001.c)

- `fsync` を伴う `write` (os_write 関数) を永遠に回すプログラム
- 128 byte もしくは 2 Mbyte ずつ、zero 埋めされた配列を os_wirte で書き込んでいく。
- ファイルサイズ (50 Mbyte) の最後まで zero 配列を書き込んだら、`lseek` で offset=0 に戻って再度やり直し。

ということで、`fsync` を伴っているために、128 byte の書き込みを行うときは、ext4 の block size である 4096 byte に書き込みが expand される。そのため、殆どが無駄な I/O になってしまっていることがわかる。以下の `biosnoop.py` からも、4096 byte の物理 I/O (FIleSytem -> Disk の要求) が発生していることが確認できる。

```
root@vm-ubuntu:~/bcc/tools# ./biosnoop.py | grep lab001
TIME(s)     COMM           PID    DISK    T SECTOR     BYTES  LAT(ms)
...
2.197601    jbd2/sdb1-8    380    sdb     W 2384488    4096      3.45
2.197816    lab001         5689   sdb     W 8997120    4096      0.08
2.198063    jbd2/sdb1-8    380    sdb     W 2384496    8192      0.19
2.203421    ?              0              R 0          0         5.34
2.207513    jbd2/sdb1-8    380    sdb     W 2384512    4096      4.06
2.209320    lab001         5689   sdb     W 8997120    524288    0.47
2.209352    lab001         5689   sdb     W 8998144    524288    0.49
2.209510    lab001         5689   sdb     W 8999168    524288    0.64
2.209675    lab001         5689   sdb     W 9000192    524288    0.80
2.209854    lab001         5689   sdb     W 9001216    4096      0.97
2.209957    jbd2/sdb1-8    380    sdb     W 2384520    8192      0.06
2.229271    ?              0              R 0          0        19.30
2.232790    jbd2/sdb1-8    380    sdb     W 2384536    4096      3.48
2.233011    lab001         5689   sdb     W 9001216    4096      0.11
2.233180    jbd2/sdb1-8    380    sdb     W 2384544    8192      0.10
2.237200    ?              0              R 0          0         4.00
```

なお、途中で 524288 byte の write 要求 4 つ続く箇所があるが、これが 2 Mbyte の書き込みに相当する。

ext4 が物理 I/O を 524,288 byte に丸めこんでいるために 4 つに分割されていると推測できるが、今の知識では ext4 ファイルシステムが物理 I/O を計算する方法がわかららず、なぜ 4 分割されているのか (128 blocks 分で物理 I/O を発行しているのか) わからなかった。これは今後の課題としたい。


### 対応策: fsync をやめる

最も単純かつ効果の高い対応方法は `fsync` をやめることだろう。つまり、`lab001.c` に下記の変更を加える。

```diff
- fsync(fd);
+ //fsync(fd);
```

再コンパイルして得られた新たなアプリケーションでは、下記のように I/O の改善が見られた。
文章にすると、「file system の write buffer (キャッシュ) によって、物理 I/O の発行数が減り、`lab001` や ext4 ジャーナリングシステムが I/O 待ちすることがなくなった」というところでしょうか。

```
root@vm-ubuntu:~/bcc/tools# uptime
 14:54:26 up  2:53,  5 users,  load average: 1.03, 1.23, 1.62

root@vm-ubuntu:~/bcc/tools# vmstat -S k 1
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 15414116 102080 949317    0    0    19   601  108  351  0  1 93  6  0
 1  0      0 15414108 102080 949317    0    0     0     0  100  261  2 23 75  0  0
 1  0      0 15414108 102080 949317    0    0     0     4  111  303  2 23 75  0  0
 1  0      0 15414108 102080 949317    0    0     0 96860   96  255  1 16 74 10  0
 1  0      0 15414206 102080 949317    0    0     0     0   54  243  2 24 75  0  0
 1  0      0 15414206 102080 949321    0    0     0     0   75  212  2 24 75  0  0
 1  0      0 15414206 102080 949321    0    0     0     0   68  175  1 24 75  0  0
 1  0      0 15414206 102080 949321    0    0     0     0   44  112  2 23 75  0  0
 1  0      0 15414206 102080 949321    0    0     0     4  219  462  2 24 74  0  0
 1  0      0 15414206 102080 949317    0    0     0     4  637 1297  2 24 74  0  0

root@vm-ubuntu:~/bcc/tools# iostat -xz 1
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           2.26    0.00   23.06    0.00    0.00   74.69

Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
sdb              0.00    1.00      0.00      4.00     0.00     0.00   0.00   0.00    0.00    0.00   0.00     0.00     4.00   4.00   0.40
```

### その他の対応策

おそらく他に効果のある対応は以下の通り (最後の方はシステムワイドな変更なので、多分実現可能性は低そう)。

- 論理 I/O (write) の書き込みサイズを、統一して大きくする
- 同じ箇所 (論理 offset) の書き込みを繰り返すスレッドに分割する (e.g. thread0 は offset = [0, 4096] を担当)
- ファイルシステム (ext4) のブロックサイズを、論理 I/O にあわせて調節する
- ファイルシステムでジャーナリングを無効化する
