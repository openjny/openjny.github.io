---
title: "Linux での TCP KeepAlive 有効化方法"
slug: how-to-enable-tcp-keepalive-on-linux
date: 2021-03-11
categories:
  - Linux
tags:
  - Linux
  - Networking
  - KeepAlive
  - TCP
isCJKLanguage: true
---

Linux の TCP KeepAlive について調べたので、その備忘録です。

## TL;DR <!--more-->

TCP KeepAlive を使用するには明示的な設定が必要で、単純にソケットをオープンするだけでは有効化されません。アプリケーションが `setsockopt` を使って SO_KEEPALIVE の値を 1 に設定することで KeepAlive が有効化されます（これらの動作は Linux、Windows 共通）。

KeepAlive が有効化されているソケット上のコネクションでは、カーネルがタイマーを管理しています。これは `ss -o` で観測した時に、`timer:(keepalive, ...)` が存在するかどうかで判定できます。

アプリケーションで KeepAlive を有効化するには、2 つの方法がとれます。

- アプリケーションで `setsockopt` の呼び出しを実装する。ただし、ソースコードの編集やコンパイル/ビルドが出来る必要があります。
- `LD_PRELOAD=libkeepalive.so` を環境変数に宣言してからアプリケーションを実行する。ソースコードに手を加えなくて良いのが利点である一方、`libkeepalive.so` をシステムに導入する必要がある点、アプリケーション上の任意の TCP コネクションで TCP KeepAlive が効いてしまう点に注意が必要。

ちなみに、この記事を読まなくても [TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/) を読めば分かります。

## TCP KeepAlive とはなにか

TCP KeepAlive は、確立された TCP コネクション (対向ホスト、その間のネットワーク) の正常性を監視する仕組みです。定期的に軽量な確認パケットをやり取りすることで、コネクションが使用可能な状態であることを確認します。TCP にはロストしたパケットの検出と再送の仕組みがあるため、正常性の定期確認がなくても TCP は動作しますが、実用上必要となることが多々あります。

たとえば、ステートフル ファイアウォールが経路に含まれていると、一定時間パケットのやり取りがないコネクションがファイアウォールの判断で閉じられてしまうことがあります。これを防止するために TCP KeepAlive が使用されます。具体的には、ファイアウォールのアイドル タイムアウト値よりも短い間隔で、TCP KeepAlive の確認パケットを定期的にやり取りします。このようなステートマシン由来の必要性は、ファイアウォール、NAT などのネットワーク アプライアンス装置を使用する場合によく発生します。

まとめると、TCP KeepAlive の目的は大まかに 2 つです。これらの目的を達成するために、TCP KeepAlive はコネクション単位で有効/無効が設定できるようになっています。

- 対向ホストの正常性を監視する
- ステートマシンを含むネットワーク アプライアンス装置に起因するコネクションの切断を防止する

詳細は [RFC 1122 の 4.2.3.6 TCP Keep-Alives](https://www.freesoft.org/CIE/RFC/1122/114.htm) も参照してみたください。

## TCP KeepAlive の有効・無効の確認方法

### ソケット

そもそもの話として、Linux ベースのディストリビューションや Windows といった標準的な OS では、アプリケーションは**ソケット (socket)** と呼ばれる特殊なファイルを開くことでネットワーク通信を実現します[^posix]。例えば、Python でクライアントを作る時は、以下のようなコードを書くでしょう。

[^posix]: ファイルに抽象化されたインターフェイス (socket) でプロセス通信通信 (例: ネットワーク経由の通信) を実現する仕様は、BSD Unix の Berkeley socket (BSD socket) と呼ばれる仕組みに根ざすものです。Berkeley socket のアイデアは、その後 POSIX に組み込まれ標準化が進みました。その結果、POSIX に (部分的に) 準拠した現代の OS では、一般的なアプリケーションのネットワーク通信がこの仕様に基づいています。

```py
import socket
import time

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('8.8.8.8', 53))
    time.sleep(5)
```

この単純な Python アプリケーションは、ソケットへの読み書き（`socket.sendall` と `socket.recv`）を実行していないため、TCP 上のデータのやり取りを想定していません。しかし、カーネル（ネットワークスタック）では TCP プロトコルに必要なハンドリングが行われています。たとえば、上記のアプリケーションでも、次のようなことはカーネル側で実行されます。

- 3 ウェイ・ハンドシェイク（コネクション確立の処理）
- 対向側から送信されたパケットをバイト列に再構築してソケットの受信バッファにコピー
- 4 ウェイ・ハンドシェイク（コネクション終端の処理）

実際に先程の Python アプリケーションの挙動を tcpdump で捕捉してみると、次のようになります。

```bash
$ sudo tcpdump host 8.8.8.8 port 53 -ni eth0
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on any, link-type LINUX_SLL (Linux cooked), capture size 262144 bytes
16:12:47.319493 IP 10.3.0.5.50528 > 8.8.8.8.53: Flags [S], seq 464911782, win 64240, options [mss 1460,sackOK,TS val 3113655258 ecr 0,nop,wscale 7], length 0
16:12:47.321744 IP 8.8.8.8.53 > 10.3.0.5.50528: Flags [S.], seq 2773628164, ack 464911783, win 65535,
options [mss 1430,sackOK,TS val 1138427843 ecr 3113655258,nop,wscale 8], length 0
16:12:47.321781 IP 10.3.0.5.50528 > 8.8.8.8.53: Flags [.], ack 1, win 502, options [nop,nop,TS val 3113655261 ecr 1138427843], length 0
16:12:47.321963 IP 10.3.0.5.50528 > 8.8.8.8.53: Flags [F.], seq 1, ack 1, win 502, options [nop,nop,TS val 3113655261 ecr 1138427843], length 0
16:12:47.323556 IP 8.8.8.8.53 > 10.3.0.5.50528: Flags [F.], seq 1, ack 2, win 256, options [nop,nop,TS val 1138427846 ecr 3113655261], length 0
16:12:47.323571 IP 10.3.0.5.50528 > 8.8.8.8.53: Flags [.], ack 2, win 502, options [nop,nop,TS val 3113655262 ecr 1138427846], length 0
```

### システムコール

**システムコール (systemcall, syscall)** は、ユーザー空間のアプリケーションからカーネルに対する要求を送信する手段の一つです。ハンドリングが難しくて、かつ公平な配分が求められる物理リソース（例: xPU、メモリ、ディスク、ネットワーク）を、ユーザー アプリケーションにそのまま露出させるわけにはいかないため、カーネルがリソース操作を行うためのインターフェイスを提供しています。ソケットを介したネットワーク通信も、最終的にはシステムコールの形でアプリケーションとカーネル間でやりとりされます。

そのため、ネットワーク アプリケーションの挙動を紐解くには、システムコールの観察も重要です。後で確認するように、**TCP KeepAlive の設定もシステムコールに依存しています**。

アプリケーションが発行するシステムコールを調べるには `strace` を使います。ネットワーク関連のシステムコールだけを観察には、`-e trace=network` オプションを指定します。オプションの詳細は `man strace` で確認してください。

以下は、先の Python アプリケーションで発行されているシステムコールです。

```bash
$ strace -ff -e trace=network python3 client.py 2>&1
socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 3
connect(3, {sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("8.8.8.8")}, 16) = 0
+++ exited with 0 +++
```

さて、上記のようなシステムコールによって確立された TCP コネクションは、TCP KeepAlive が有効化されているのでしょうか？

前提知識なしで判定するのはなかなか難しいところなので、いくつかのツールを使ってさらに読み解いて行きましょう。これから使うのは、以下の 2 つのツールです。

- `ss`: ソケットに関する情報を取得する観測ツール[^ss]。`-o (--options)` オプションを指定すると、TCP KeepAlive の有無やそのタイマーを表示してくれる。
- `curl`: 様々なプロトコルに対応したクライアント アプリケーション。`--no-keepalive` オプションを指定すると TCP KeepAlive を無効化し、デフォルトのままだと有効化する。

[^ss]: `ss` は `netstat` の後継コマンドで、より多くの情報を提供してくれます。`ss` は `iproute2` パッケージに含まれているので、`iproute2` がインストールされている環墩であれば、`ss` が使えるはずです。

### ss による TCP KeepAlive 判定

`ss` を使って、先程の Python アプリケーションと curl の挙動を見比べてみましょう。使用する `ss` コマンドのオプションは次の通りです。

- `-t`: TCP ソケットの情報を表示
- `-a`: LISTEN 以外のソケットも表示 (TCP の場合は ESTABLISHED 状態のコネクションのみを表示)
- `-n`: IP アドレスとポート番号を数値で表示
- `-o`: オプション情報を表示
- `-e`: 詳細情報を表示

```bash
$ python3 client.py

$ ss -tanoe 'dst 8.8.8.8'
State   Recv-Q   Send-Q   Local Address:Port    Peer Address:Port
ESTAB   0        0             10.3.0.5:52686        8.8.8.8:53  
users:(("python3",pid=29357,fd=3)) uid:1000 ino:305411 sk:196 <->
```

```bash
$ curl http://8.8.8.8:53 # --no-keepalive を指定していない (TCP KeepAlive 有効化)

$ ss -tanoe 'dst 8.8.8.8'
State   Recv-Q   Send-Q   Local Address:Port    Peer Address:Port
ESTAB   0        0             10.3.0.5:53326        8.8.8.8:53   \
users:(("curl",pid=30213,fd=3)) timer:(keepalive,1min,0) uid:1000 ino:311003 sk:19a <->
```

`curl` の方には、timer フィールドがあるのがわかりますね。詳細は [ss の man ページ](https://man7.org/linux/man-pages/man8/ss.8.html) に載っていますが、実際、timer フィールドで TCP KeepAlive の有効/無効を判定することが出来ます。具体的には、ESTABLISHED な TCP コネクションを `ss -o` で確認した時：

- keepalive の timer フィールドが存在する場合、TCP KeepAlive は有効です。
- keepalive の timer フィールドが存在しない場合、TCP KeepAlive は無効です。

timer フィールドのセマンティクスは以下の通りです。

```text
timer:(<timer_name>,<expire_time>,<retrans>)

<timer_name>
        the name of the timer, there are five kind of timer names:
        on : means one of these timers: TCP retrans timer, TCP early retrans timer and tail loss probe timer
        keepalive: tcp keep alive timer
        timewait: timewait stage timer
        persist: zero window probe timer
        unknown: none of the above timers

<expire_time>
        how long time the timer will expire

<retrans>
        how many times the retransmission occurred
```

なお、TCP の状態遷移において、時間管理が必要な場面は多々あります。たとえば、FIN を送信してからしばらく TIME_WAIT 状態でコネクションを待つ[^time-wait]のですが、ここでも時間管理は必要です。したがって、timer フィールドがあるからといって TCP KeepAlive が有効化されているとは限らないので注意してください。

[^time-wait]: 参考: [TCPのTIME-WAITを温かく見守る #TCP - Qiita](https://qiita.com/kiririmode/items/6b33aaf1b900d28de704)

{{< notice tip 結論 >}}
`ss -o` で観察した時、keepalive の timer がセットされているコネクション (socket) は、TCP KeepAlive が有効化されています。
{{< /notice >}}

### strace による TCP KeepAlive 判定

Python アプリケーションと curl の挙動の違いが分かったところで、次はシステムコールの差分を見てみましょう。ここでは、TCP KeepAlive の On/Off をスイッチできる curl コマンドを使って、その違いを `strace` で観察します。

```diff
$ strace -e trace=network -o on.log curl http://8.8.8.8:53
$ strace -e trace=network -o off.log curl http://8.8.8.8:53 --no-keepalive
$ diff on.log off.log

< setsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], 4) = 0
< setsockopt(3, SOL_TCP, TCP_KEEPIDLE, [60], 4) = 0
< setsockopt(3, SOL_TCP, TCP_KEEPINTVL, [60], 4) = 0
< getsockname(3, {sa_family=AF_INET, sin_port=htons(57040), sin_addr=inet_addr("10.3.0.5")}, [128->16]) = 0
> getsockname(3, {sa_family=AF_INET, sin_port=htons(57012), sin_addr=inet_addr("10.3.0.5")}, [128->16]) = 0
```

最後の行 (getsockname) の違いは、ソースポートの違いだけなので今回の文脈では関係ありません。重要なのは、**TCP KeepAlive を有効化する時だけ setsockopt がセットされていること**です。[TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/) のセクション 4.2 に、この動作に関する詳細が書かれています。

> All you need to enable keepalive for a specific socket is to set the specific socket option on the socket itself. The prototype of the function is as follows:
>
>  int setsockopt(int s, int level, int optname, const void *optval, socklen_t optlen)
>      
> The first parameter is the socket, previously created with the socket(2); the second one must be SOL_SOCKET, and the third must be SO_KEEPALIVE . he fourth parameter must be a boolean integer value, indicating that we want to enable the option, while the last is the size of the value passed before.
>
> There are also three other socket options you can set for keepalive when you write your application. They all use the SOL_TCP level instead of SOL_SOCKET, and they override system-wide variables only for the current socket. If you read without writing first, the current system-wide parameters will be returned.
>
> TCP_KEEPCNT: overrides tcp_keepalive_probes
>
> TCP_KEEPIDLE: overrides tcp_keepalive_time
>
> TCP_KEEPINTVL: overrides tcp_keepalive_intvl

これを簡単に要約すると次の通りです。

- `setsockopt` は、TCP KeepAlive を有効化するためのシステムコールです。
- `setsockopt` の第 2 引数に `SOL_SOCKET`、第 3 引数に `SO_KEEPALIVE`、第 4 引数に `1` (の値を格納した 4 byte のメモリスペースへのポインタ) を指定すれば、TCP KeepAlive が有効になります。
- 他にも、`TCP_KEEPCNT`、`TCP_KEEPIDLE`、`TCP_KEEPINTVL` といったオプションで、TCP KeepAlive の挙動を調整できます。各オプションは、システム全体の設定を上書きします。

なお、[tcp の man ページ](https://linux.die.net/man/7/tcp) には、各オプションの詳細が記載されています。

```text
tcp_keepalive_intvl (integer; default: 75; since Linux 2.4)
    The number of seconds between TCP keep-alive probes.

    (訳) TCP KeepAlive プローブ間の秒数。

tcp_keepalive_probes (integer; default: 9; since Linux 2.2)
    The maximum number of TCP keep-alive probes to send before giving up
    and killing the connection if no response is obtained from the other end.

    (訳) TCP KeepAlive プローブの最大数。他方からの応答が得られない場合、
    接続を切断する前に送信する TCP KeepAlive プローブの最大数。

tcp_keepalive_time (integer; default: 7200; since Linux 2.2)
    The number of seconds a connection needs to be idle before TCP begins
    sending out keep-alive probes. Keep-alives are only sent when the SO_KEEPALIVE
    socket option is enabled.The default value is 7200 seconds (2 hours). An idle
    connection is terminated after approximately an additional 11 minutes
    (9 probes an interval of 75 seconds apart) when keep-alive is enabled.

    (訳) TCP KeepAlive プローブを送信し始めるまでの接続がアイドル状態になる秒数。
    SO_KEEPALIVE ソケットオプションが有効化されている場合のみ、TCP KeepAlive プローブが
    送信されます。デフォルト値は 7200 秒 (2 時間) です。アイドル接続は、KeepAlive が
    有効化されている場合、約 11 分後に追加の 11 分間 (9 回のプローブ、75 秒間隔) で切断されます。
    なお、TCP より下のレイヤーやアプリケーションのタイムアウトは、はるかに短い場合があります。
```

オプションの設定箇所はシステム側にもあります。システム側の設定は、proc ファイルシステム (procfs) や sysctl のインターフェースで公開されています。詳細は、次のような文献を参照してみてください。

- [Using TCP keepalive under Linux](https://tldp.org/HOWTO/TCP-Keepalive-HOWTO/usingkeepalive.html)
- [Configuring TCP KeepAlive settings - IBM Documentation](https://www.ibm.com/docs/en/sim/7.0.1.13?topic=tasks-configuring-tcp-keepalive-settings)

{{< notice tip 結論 >}}
SO_KEEPALIVE ソケット オプションが明示的に設定されている場合にのみ、TCP KeepAlive が有効化されます。
{{< /notice >}}

## TCP KeepAlive 有効化を強制できる？

socket (コネクション) 単位で TCP KeepAlive を有効化できるのはわかりました。しかし、システム側で KeepAlive 有効化を強制する方法は無いのでしょうか？たとえば、何らかの事情でアプリケーションを改修できない場合では、システム側で強制できると嬉しいです。

そんな時に使えるのが libkeepalive です。libkeepalive は、共有ライブラリを動的リンクする Linux の機能を使って、TCP KeepAlive を有効化します。

- [msantos/libkeepalive: LD_PRELOAD library for enabling TCP keepalive socket options](https://github.com/msantos/libkeepalive)
- [-=| libkeepalive |=-](https://libkeepalive.sourceforge.net/)

Linux では、`LD_PRELOAD` 環境変数に共有ライブラリ（ファイル名）を設定してアプリケーションを実行すると、アプリケーションはその共有ライブラリを優先的にリンクします。これにより、特定のライブラリの関数を、ユーザー独自のものに変更することが出来ます。socket ファイルのオープンも一般には共有ライブラリを介して実行されるため、`LD_PRELOAD` により挙動の上書きが可能です。

実際に使ってみるとその効果がわかるので、テストアプリケーションを動かしてみることをおすすめします。

### テスト アプリケーションの動作確認（既定）

[TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/) あるアプリケーション "test" を動かしてみます。test は、次の挙動をします。

- socket をオープンします。
- socket の TCP KeepAlive 設定値 (SO_KEEPALIVE) を出力します。既定では無効化 (`0`) です。
- setsockopt を使って SO_KEEPALIVE を `1` にセットし、TCP KeepAlive を有効化します。
- 再度 SO_KEEPALIVE の現在値を出力します。

```bash
cat <<EOF >test.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main()
{
   int s;
   int optval;
   socklen_t optlen = sizeof(optval);

   if((s = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0) {
      perror("socket()");
      exit(EXIT_FAILURE);
   }

   if(getsockopt(s, SOL_SOCKET, SO_KEEPALIVE, &optval, &optlen) < 0) {
      perror("getsockopt()");
      close(s);
      exit(EXIT_FAILURE);
   }
   printf("SO_KEEPALIVE is %s\n", (optval ? "ON" : "OFF"));

   optval = 1;
   optlen = sizeof(optval);
   if(setsockopt(s, SOL_SOCKET, SO_KEEPALIVE, &optval, optlen) < 0) {
      perror("setsockopt()");
      close(s);
      exit(EXIT_FAILURE);
   }
   printf("SO_KEEPALIVE set on socket\n");

   if(getsockopt(s, SOL_SOCKET, SO_KEEPALIVE, &optval, &optlen) < 0) {
      perror("getsockopt()");
      close(s);
      exit(EXIT_FAILURE);
   }
   printf("SO_KEEPALIVE is %s\n", (optval ? "ON" : "OFF"));

   close(s);
   exit(EXIT_SUCCESS);
}
EOF

$ gcc -o test test.c

$ ./test
SO_KEEPALIVE is OFF
SO_KEEPALIVE set on socket
SO_KEEPALIVE is ON

$ strace -e trace=network ./test
socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
getsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [0], [4]) = 0
SO_KEEPALIVE is OFF
setsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], 4) = 0
SO_KEEPALIVE set on socket
getsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], [4]) = 0
SO_KEEPALIVE is ON
```

期待通りの動作をしてくれています。繰り返しになりますが、`setsockopt` で `SO_KEEPALIVE` を 1 にセットしない限り、デフォルトでは TCP KeepAlive は無効のままです。

### テスト アプリケーションの動作確認（libkeepalive あり）

続いて `libkeepalive.so` をかましてみるとどうなるか見ていきます。

```bash
$ wget  https://excellmedia.dl.sourceforge.net/project/libkeepalive/libkeepalive/0.3/libkeepalive-0.3.tar.gz
$ tar -xzvf libkeepalive-0.3.tar.gz
$ cd libkeepalive-0.3
$ make
$ sudo cp libkeepalive.so /usr/lib/

$ LD_PRELOAD=/usr/lib/libkeepalive.so ./test
SO_KEEPALIVE is ON
SO_KEEPALIVE set on socket
SO_KEEPALIVE is ON

$ LD_PRELOAD=/usr/lib/libkeepalive.so strace -e trace=network ./test
socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
setsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], 4) = 0
getsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], [4]) = 0
SO_KEEPALIVE is ON
setsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], 4) = 0
SO_KEEPALIVE set on socket
getsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], [4]) = 0
SO_KEEPALIVE is ON
+++ exited with 0 +++
```

先程と異なり、`setsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], 4) = 0` がソケットのオープンと共に実行されていることがわかります。これが共有ライブラリの差し替えによる効果です。

ただし、`LD_PRELOAD` を使うと、アプリ上で開いた全ての socket で TCP KeepAlive が有効化されるので、その点は配慮しなくてはなりません。

## まとめ

TCP コネクション確立時に発行されるシステムコールが、アプリケーションの作り方やコマンドの指定方法によって異なることを確認し、`setsockopt`  が TCP KeepAlive に関わる重要なシステムコールであることを見てきました。最終的に `setsockopt` をカーネルに送らなければならないことに変わりはありませんが、共有ライブラリの差し替えテクニック (`libkeepalive`) によって、任意のアプリケーションで強制的に TCP KeepAlive を有効化する技術についても紹介しました。`nc` のような TCP KeepAlive に対応していないアプリをカスタマイズするのに使えそうです。

## 参考

- [TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/)
- [SO_KEEPALIVE - Windows drivers | Microsoft Docs](https://docs.microsoft.com/ja-jp/windows-hardware/drivers/network/so-keepalive)
- [Enable TCP keepalive on Redis cluster bus (gossip inside cluster) | by Rajivsharma | Medium](https://medium.com/@rajivsharma.2205/enable-tcp-keepalive-on-redis-cluster-bus-153128e412fa)
- [LinuxのTCP Keep-Aliveを確認する - CLOVER🍀](https://kazuhira-r.hatenablog.com/entry/2020/02/27/002840)
- [ss(8) - Linux manual page](https://man7.org/linux/man-pages/man8/ss.8.html)
- [eBPFやLD_PRELOADを利用した共有ライブラリの関数フック - Tier IV Tech Blog](https://tech.tier4.jp/entry/2021/03/10/160000)
- [Enable TCP keepalive of macOS and Linux in Ruby](http://quickhack.net/nom/blog/2018-01-19-enable-tcp-keepalive-of-macos-and-linux-in-ruby.html)
- [既存アプリケーションの関数を書き換える、強力で危険なLinux環境変数LD_PRELOAD - Qiita](https://qiita.com/developer-kikikaikai/items/f6f87b2d1d7c3e14fb52)
