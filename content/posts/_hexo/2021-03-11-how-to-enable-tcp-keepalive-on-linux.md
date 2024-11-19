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

## <!--more-->

## TL;DR

Linux は TCP KeepAlive に対応していますが、普通に `socket` を開くだけだと有効化されません。既定では無効の状態です。アプリケーションが `setsockopt` システムコールを (第 3 引数 = 1 で) 呼び出して、初めて TCP KeepAlive が有効化されます (ちなみに既定で TCP KeepAlive が無効なのは、Windows でも同様です)。

アプリケーションで TCP KeepAlive を有効化するには、2 つの方法がとれます。

- アプリケーションで `setsockopt` を実装する。ただし、ソースコードの編集やコンパイル/ビルドが出来る必要があります。
- `LD_PRELOAD=libkeepalive.so` を環境変数に宣言してからアプリケーションを実行する。ソースコードに手を加えなくて良いのが利点である一方、`libkeepalive.so` をシステムに導入する必要があるのと、アプリ上の任意の TCP コネクションで TCP KeepAlive が効いてしまうのが欠点。

こんな記事を読まなくても、必要なことは [TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/) に全部書いてあります。

## TCP KeepAlive とはなにか

TCP KeepAlive とは、TCP コネクションがアクティブな状態なのか (対向側やその間のネットワークが死んでないか) を検知する為の正常性監視の仕組みです。TCP のレイヤーで実装されているので、基本的にカーネルで制御する義務があります。HTTP KeepAlive とは全くの別物であることに注意しましょう。

主たる目的は正常性監視ですが、定期的にパケットを送信する仕組みとして TCP KeepAlive が使われることもあります。ネットワーク データパス上に存在する L4 のネットワーク アプライアンス機器には、しばしばタイムアウトが実装されています。このような機器ではフローテーブル等で通信の状態を保持しておかなければならず、タイムアウトがなければリソース枯渇を招く為です。

例えば、30 分間ずっと無通信状態の TCP コネクションがあれば、それ以降のパケットはフォワーディングしないアプライアンスがあったとします。ここに、TCP KeepAlive を導入する動機があります。TCP KeepAlive で 10 分毎に死活監視を行えば、長時間 TCP コネクションが非活性になるのを予防できます。

まとめると、TCP KeepAlive の目的は大まかに 2 つです。これらの目的を達成するために、TCP KeepAlive はコネクション単位で有効/無効が設定できるようになっています。

* 対向の正常性を監視すること
* 非活性なネットワークを活性化させて、コネクション切断を防ぐこと

## どうすれば TCP KeepAlive を有効化できるのか

結論から言えば、Linux で TCP KeepAlive を有効化するには `setsockopt` システムコールを使う必要があります。以下のようなシステムコールが `strace` で確認できれば、その TCP コネクションで TCP KeepAlive が有効になります (そうでない限り無効です)。

```
setsockopt(<sockfd>, SOL_SOCKET, SO_KEEPALIVE, [1], 4)
```

※ 第 3 引数が `[0]` の場合、明示的な無効化を意味します。

### socket とシステムコール

そもそもの話として、Linux や Windows 等の標準的な OS では、TCP コネクションを活用したいアプリケーションは socket と呼ばれる特殊なファイルを開きます。例えば、Python3 で (socket を開いて) サーバーに接続するクライアントを作る時は、以下のようなコードを書くでしょう。

```py
import socket
import time

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('8.8.8.8', 53))
    time.sleep(5)
```

このプログラムを動かしてみると、`socket.sendall` や `socket.recv` がないので何もクライアントから送受信することは無い (e.g. HTTP のプロトコルに則っていない) のですが、TCP の 3way handshake やクローズの処理は正常に行えていることが確認できます。これだけで TCP コネクションの確立はできてしまうんですね。

```bash
$ sudo tcpdump host 8.8.8.8 port 53 -ni any
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

アプリの実装を紐解く上では、どのようなシステムコールを発行しているか、という点も抑えておきましょう。なぜなら、システムコールはアプリケーションからの要求をカーネルが受け取る唯一の方法であり、後に見るように、**システムコール次第で TCP KeepAlive の有効/無効が決定される** 為です。TCP を管理するのは Kernel のネットワーク スタックなので、TCP KeepAlive に関する調節命令をアプリケーションからカーネルに出さないといけないのも納得ですね。

プログラムが発行するシステムコールを調べるには `strace` を使います。

```bash
$ strace -ff -e trace=network python3 client.py 2>&1
socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 3
connect(3, {sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("8.8.8.8")}, 16) = 0
+++ exited with 0 +++
```

さて、これらのシステムコールによって確立された TCP コネクションは、TCP KeepAlive が有効化されているのでしょうか？

初見で判定するのはなかなか難しいところなので、いくつかの既知の知識を使って読み解いて行きましょう。これから使うのは、以下の 2 つのツールです。

- `ss`: ソケットに関する統計量を取得する観測ツール。`-o (--options)` を指定すると、TCP KeepAlive の有無やそのタイマーを表示してくれる。
- `curl`: 様々なプロトコルに対応したクライアント。`--no-keepalive` を指定すると TCP KeepAlive を無効化、デフォルトのままだと TCP KeepAlive を有効化する。


### ss による TCP KeepAlive 判定

試しに先程の Python プログラムと、(TCP KeepAlive を有効化した) curl の結果を見比べてみましょう。

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

`curl` の方には、timer フィールドがあるのがわかりますね。詳細は `ss(8)` の man に載っていますが、実際、timer フィールドの有無で TCP KeepAlive の有効/無効を判定することが出来ます。具体的には、ESTABLISHED な TCP コネクションを `ss -o` で確認した時：

- `timer:(keepalive, ...)` が存在する場合、TCP KeepAlive は有効です。
- `timer:(keepalive, ...)` が存在しない場合、TCP KeepAlive は無効です。

ちなみに、timer のセマンティクスは以下の通りです。

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

- ref: [man 8 ss](https://man7.org/linux/man-pages/man8/ss.8.html)

### strace による TCP KeepAlive 判定

最初の Python プログラムでは TCP KeepAlive が有効になっていなかったことがわかりました。ここまでくればあともう一息。最後に `curl` が発行しているシステムコールを見るだけです。具体的には、TCP KeepAlive オプションによるシステムコールの差分を見てみます。

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

TCP KeepAlive が有効化されている時は `setsockopt` で指定されていますね。strace で見た時に `setsockopt(<sockfd>, SOL_SOCKET, SO_KEEPALIVE, [1], 4)`  が存在すれば有効になってそうな匂いを感じます (`TCP_KEEPIDLE` とか `TCP_KEEPINTVL` はデフォルト インターバル値の上書きと予想できます)。

Linux 関連のドキュメントを検索したところ、下記のセクション 4.2 にまさに探していた情報が載っていました。嗅覚は当たっていました :clap:

> All you need to enable keepalive for a specific socket is to set the specific socket option on the socket itself. The prototype of the function is as follows:
>
>  int setsockopt(int s, int level, int optname,
>                 const void *optval, socklen_t optlen)
>      
> The first parameter is the socket, previously created with the socket(2); the second one must be SOL_SOCKET, and the third must be SO_KEEPALIVE . The fourth parameter must be a boolean integer value, indicating that we want to enable the option, while the last is the size of the value passed before.

[TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/)

第 3 引数に `1` (の値を格納した 4 byte のメモリスペースへのポインタ) を指定すれば、第 1 引数に指定した `sockfd` の TCP KeepAlive が有効になるそうです。

## OS の仕組みでなんとかならない？

`setsockopt` でごにょごにょすれば TCP KeepAlive を有効化できるのはわかった。でもそれだとソースコードをいじらないといけなくて、めんどくさい。後は自分がアプリケーションのソースコードを保有してる/改修できるとは限らないので、なんとか OS の仕組みで TCP KeepAlive 有効化できないの？と思いますよね。

しっかりありました。`LD_PRELOAD` というものだそうです。

`LD_PRELOAD` は Linux の特別な環境変数で、動的ライブラリ/共有ライブラリへのパスを値として設定すると、任意の動的ライブラリよりもそのライブラリが優先的にリンクされてプログラムが実行されます。この機能に着目したのが、`libkeepalive.so` です。これは、`socket` を開いた時に一緒に TCP KeepAlive も有効化するように、TCP KeepAlive にチューニングされたソケット機能を提供するライブラリです。

http://libkeepalive.sourceforge.net/

実際に使ってみるとその効果がわかるので、テストプログラムを動かしてみることをおすすめします。

### テストプログラム

[TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/) のセクション 4.3 にあるプログラム `test` を動かしてみます。

* `test` は、単に socket をひとつ新たにオープンします。
* その直後、socket の TCP KeepAlive 設定 (SO_KEEPALIVE) 値を出力します。通常であれば無効化 (`0`) となっているはずの値ですね。
* その後、`setsockopt` を使って、明示的に TCP KeepAlive を有効化します。
* 再度 SO_KEEPALIVE の現在値を出力します。最後には有効 (`1`) となっているはずです。

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

何の変哲もない期待通りの動作です。繰り返しになりますが、`setsockopt` で `SO_KEEPALIVE` を 1 にセットしない限り、デフォルトでは TCP KeepAlive は無効のままです。

### libkeepalive ありのテストプログラム

続いて `libkeepalive.so` をかましてみるとどうなるか。以下の通り、デフォルトの動作が変化します。

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

$ $ LD_PRELOAD=/usr/lib/libkeepalive.so strace -e trace=network ./test
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

先程と違い `setsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], 4) = 0` が (知らない間に) 挿入されていることがわかります。これが共有ライブラリの差し替えによる効果です。ただし、`LD_PRELOAD` を使うと、アプリ上で開いた全ての socket で TCP KeepAlive が有効化されるので、その点は配慮しなくてはなりません。

## まとめ

TCP コネクション確立時に発行されるシステムコールが、プログラムの作り方やコマンドの指定方法によって異なることを確認し、`setsockopt`  が TCP KeepAlive に関わる重要なシステムコールであることを見てきました。最終的に `setsockopt` をカーネルに送らなければならないことに変わりはありませんが、共有ライブラリの差し替えテクニック (`libkeepalive`) によって、任意のプログラムで強制的に TCP KeepAlive を有効化する技術についても紹介しました。`nc` のような TCP KeepAlive に対応していないアプリをカスタマイズするのに使えそうです。


## 参考

- [TCP Keepalive HOWTO](https://tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/)
- [SO_KEEPALIVE - Windows drivers | Microsoft Docs](https://docs.microsoft.com/ja-jp/windows-hardware/drivers/network/so-keepalive)
- [Enable TCP keepalive on Redis cluster bus (gossip inside cluster) | by Rajivsharma | Medium](https://medium.com/@rajivsharma.2205/enable-tcp-keepalive-on-redis-cluster-bus-153128e412fa)
- [LinuxのTCP Keep-Aliveを確認する - CLOVER🍀](https://kazuhira-r.hatenablog.com/entry/2020/02/27/002840)
- [ss(8) - Linux manual page](https://man7.org/linux/man-pages/man8/ss.8.html)
- [eBPFやLD_PRELOADを利用した共有ライブラリの関数フック - Tier IV Tech Blog](https://tech.tier4.jp/entry/2021/03/10/160000)
- [Enable TCP keepalive of macOS and Linux in Ruby](http://quickhack.net/nom/blog/2018-01-19-enable-tcp-keepalive-of-macos-and-linux-in-ruby.html)
- [既存プログラムの関数を書き換える、強力で危険なLinux環境変数LD_PRELOAD - Qiita](https://qiita.com/developer-kikikaikai/items/f6f87b2d1d7c3e14fb52)
