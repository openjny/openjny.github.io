+++
title = "ブログを Hugo に引っ越した"
slug = "migrate-blog-to-hugo"
date = "2024-11-18"
tags = [
    "hugo",
    "shortcodes"
]
categories = [
    "その他",
]
# series = ["Demonstração do Tema"]
+++

数年間更新してなかった個人ブログを再度整備しようと思い、あわせて SSG を Hugo に乗り換えてみました。これはその備忘録的なポストです。

## <!--more-->

## なぜ Hugo なのか

深い理由はないです。いままで Hexo の vuepress テーマを使っていて、特に使いづらいと感じたことはなかったものの、次のような点は少し気になっていました。

- **Community Centrality**: 更新頻度が高いわけではないので最悪塩漬けでも良いと思ってました。ただ、[GitHub のスター数](https://jamstack.org/generators/)とか見てるとやっぱり Hexo の人気はそこまで高くなく、更新頻度も他の SGG と比べると見劣りする点は否めないです。
- **マルチ言語サポート**: 英語で発信したい機会も増えてきました。日本語は zenn で、英語は [Medium](https://medium.com/@openjny) でポストするようにしてたんですが、Medium の執筆体験はお世辞にも良いものとは言えない...（脚注使えない、埋め込みできない、etc）。
- **node_modules**: Node.js だとファイルシステムに負荷がかかりがちなので、シングルバイナリで完結する Hugo のほうがありがたい（気がする）。

## 乗り換え作業

### テーマ

テーマは `hugo-coder` にしました。特にこだわりはないです。シンプルで、マルチ言語対応で、ブログとプロジェクト書けるようなテーマが欲しかったです。`hugo-coder` はその条件を満たしていたのと、更新頻度の高さや Star の多さも安心感があったので選びました。

[luizdepra/hugo-coder: A minimalist blog theme for hugo.](https://github.com/luizdepra/hugo-coder)

### URL

`hugo.toml` でパーマリンクのスタイルを設定しました。

```toml
[permalinks]
posts = '/:year/:month/:day/:slug/'
```

### フォント

中国語フォントを無効化するため `themes/hugo-coder/assets/scss/_variables.scss` でフォント指定を変更しました。

```diff
$font-family: -apple-system,
BlinkMacSystemFont,
"Segoe UI",
Roboto,
Oxygen-Sans,
Ubuntu,
Cantarell,
"Helvetica Neue",
Helvetica,
- "游ゴシック",
- "PingFang SC",
- STXihei,"华文细黑",
- "Microsoft YaHei","微软雅黑",
- SimSun,"宋体",
- Heiti,"黑体",
+ // "游ゴシック",
+ // "PingFang SC",
+ // STXihei,"华文细黑",
+ // "Microsoft YaHei","微软雅黑",
+ // SimSun,"宋体",
+ // Heiti,"黑体",
sans-serif;
```

フォントを小さくするため `_base.scss` も調整しました。

```diff
html {
  box-sizing: border-box;
-  font-size: 62.5%;
+  font-size: 57.5%;
}

.container {
  margin: 1rem auto;
- max-width: 90rem;
+ max-width: 100rem;
# ...
```
