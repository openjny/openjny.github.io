---
title: "VuePress で始める静的サイトブログ"
slug: hello-vuepress
date: 2019-12-28
categories:
  - その他
tags:
  - ブログ
  - VuePress
  - SSG
isCJKLanguage: true
---

VuePress でのブログ環境を整えたのでその備忘録です。

## はじめに <!--more-->

自分がブログに求めることは次の点です。

- Markdown でブログ本文が記述出来る
- GHF (github flavored) や pandoc スタイルのような、汎用的な Markdown の記述で*なるべく*完結する
- mathjax/katex がエスケープなしで記述出来る
- 記事にカテゴリ/タグが使える

今までは上のような要件を満たす `hexo` と呼ばれる SGG (static site generator) を pandoc とともに利用していましたが、最近ひょんなことから知った VuePress で同じようなことが出来るみたいだったので、勉強がてら乗り換えてみました。

### VuePress

VuePress は Vue, Vue Router, webpack を利用した静的サイトジェネレーターです。

https://v1.vuepress.vuejs.org/


VuePress で生成された静的サイトは SPA になっていて、事前に HTML にコンパイルされた markdown を Vue で描写することで、モダンな感じのサイトを作成することが出来ます。

[Nuxt.js](https://nuxtjs.org/) でも似たようなことが出来ますが、両者は「汎用的なアプリ作成フレームワーク」か「静的サイト生成に特化したフレームワーク」かという違いがあります。僕もよくわかってないので詳しいことは Google 先生に聞いてみてください。

{{< notice info >}}

- [VuePress](https://vuepress.vuejs.org/)
- [VuePressとnetlifyでblogをはじめる | tomopictのblog](https://tomopict.netlify.com/posts/2018/12/31/_20181231.html)
- [Hello VuePress | memo](https://naranoshika.netlify.com/post/vuepress/hello.html)
- [VuePress をお試ししてみた - Qiita](https://qiita.com/dojineko/items/aae7e6d13479e08d49fd#%E8%87%AA%E5%8B%95%E3%83%AA%E3%83%B3%E3%82%AF%E3%81%AE%E8%A8%AD%E5%AE%9A)
- [VuePressで作ったblogに配布されているテーマを設定する - Qiita](https://qiita.com/tomopict/items/9da7cf28c9bcd5f933cb#%E7%B4%B0%E3%81%8B%E3%81%84%E8%AA%BF%E6%95%B4)
{{< /notice >}}

### Meteorlxy

[Home | vuepress-theme-meteorlxy](https://vuepress-theme-meteorlxy.meteorlxy.cn/)

公式のブログのテーマが物足りなかったので上のテーマを使ってます。

## 機能

### Container

Meteorlxy によって提供される独自拡張の一つで、`markdown-it-container` を使って注釈のような div ブロックが挿入できる。

```
::: [tip|warning|danger|details] タイトル(opt)
内容
:::
```

{{< notice info >}}
こうなります
{{< /notice >}}

また、自作コンテナの定義もできる。
以下は `.vuepress/styles/index.styl` で定義した `pre.vue-container` スタイルに基づいて、独自のコンテナを追加する例です。

```js
    },
    plugins: [
        ['container', {
            type: 'vue',
            before: '<pre class="vue-container"><code>',
            after: '</code></pre>'
        }],
        ['container', {
            type: 'ref',
            defaultTitle: 'Reference',
```

{{< notice info >}}
.
├── docs
│   ├── .vuepress _(**Optional**)_
│   │   ├── `components` _(**Optional**)_
│   │   ├── `theme` _(**Optional**)_
│   │   │   └── Layout.vue
│   │   ├── `public` _(**Optional**)_
│   │   ├── `styles` _(**Optional**)_
│   │   │   ├── index.styl
│   │   │   └── palette.styl
│   │   ├── `templates` _(**Optional, Danger Zone**)_
│   │   │   ├── dev.html
│   │   │   └── ssr.html
│   │   ├── `config.js` _(**Optional**)_
│   │   └── `enhanceApp.js` _(**Optional**)_
│   └── README.md
└── package.json
{{< /notice >}}

{{< notice info >}}
- [Markdown Extensions | VuePress](https://vuepress.vuejs.org/guide/markdown.html#custom-containers)
- [vuepress-plugin-container | VuePress Community](https://vuepress.github.io/en/plugins/container/#demo)
{{< /notice >}}

### 生の URL に対するリンク

URL テキストをリンクにするには、既定ではオフになっている `markdown-it-linkify` の linkify オプションを有効にする。

#### 構成例

``` js
  markdown: {
    linkify: true
  },
```

#### サンプル

```md
まずは https://v1.vuepress.vuejs.org/ を御覧ください。
```

まずは https://v1.vuepress.vuejs.org/ を御覧ください。

#### 参考

- [VuePress をお試ししてみた - Qiita](https://qiita.com/dojineko/items/aae7e6d13479e08d49fd#%E8%87%AA%E5%8B%95%E3%83%AA%E3%83%B3%E3%82%AF%E3%81%AE%E8%A8%AD%E5%AE%9A)
- https://github.com/vuejs/vetur/blob/ad2490ac55838bda7d18acbf3eaa071ab3ea809d/docs/.vuepress/config.js#L5

### 相対パスによる画像

[Asset Handling | VuePress](https://v1.vuepress.vuejs.org/guide/assets.html)

既定で相対パスに対応している。なお、生成されたサイトでは `asset` フォルダー以下にランダムに生成された名前のファイルとして配置される。
また、Webpack のエイリアス機能を使ってより柔軟にベース フォルダを指定できる。詳細はドキュメントを参照のこと。

#### サンプル

```
{{< figure src="2019-12-28-hello-vuepress/mikyan.png" caption="みきゃん" >}}
```

{{< figure src="2019-12-28-hello-vuepress/mikyan.png" caption="みきゃん" >}}

### 数式

`vuepress-plugin-mathjax` でも良かったけど、[実装](https://github.com/vuepress/vuepress-plugin-mathjax/blob/master/src/markdown.js) を見る限り数式の判定がなんだか怪しい[^vuepress-plugin-mathjax-markdownjs]ので、`markdown-it-katex` の拡張で代用しました。

[^vuepress-plugin-mathjax-markdownjs]: 正規表現使うもんかと思ってた。

ただ、無印の (`@` によるスコープ指定をしない) `markdown-it-katex` は [更新が止まっていて version 0.5.0 くらいまでしか使えません](https://github.com/waylonflinn/markdown-it-katex/issues/23)。なので、`@iktakahiro/markdown-it-katex` を利用させてもらいました。

#### 構成例

```bash
$ yarn add @iktakahiro/markdown-it-katex --dev
```

```js
// .vuepress/config.js
    head: [
        ['link', {
            rel: 'stylesheet',
            href: 'https://cdn.jsdelivr.net/npm/katex@0.11.0/dist/katex.min.css'
        }]
    ],
    markdown: {
        extendMarkdown: md => {
            md.use(require('@iktakahiro/markdown-it-katex'), {
                throwOnError: false,
                errorColor: "#cc0000",
                macros: {
                    '\\Z': '\\mathbb{Z}',
                    '*': '\\times'
                }
            })
        }
    }
```

#### サンプル


```md
$\sin(x) = 2\pi$ という簡単な方程式でも、小学生には難しいです。
```

$\sin(x) = 2\pi$ という簡単な方程式でも、小学生には難しいです。

```md
機械学習とは、データセット $\mathcal{D} = \{ \mathbf{x}_n \in \mathcal{X}, y_n \in \mathcal{Y} \}_{n=1}^N$ が与えられた時に、入力と出力を対応付ける写像
$$
  f: \mathcal{X} \to \mathcal{Y}
$$
を学習すること。
```

機械学習とは、データセット $\mathcal{D} = \{ \mathbf{x}_n \in \mathcal{X}, y_n \in \mathcal{Y} \}_{n=1}^N$ が与えられた時に、入力と出力を対応付ける写像
$$
  f: \mathcal{X} \to \mathcal{Y}
$$
を学習すること。

```md
$$\frac {\partial^r} {\partial \omega^r} \left(\frac {y^{\omega}} {\omega}\right) 
= \left(\frac {y^{\omega}} {\omega}\right) \left\{(\log y)^r + \sum_{i=1}^r \frac {(-1)^i r \cdots (r-i+1) (\log y)^{r-i}} {\omega^i} \right\}$$
```

$$\frac {\partial^r} {\partial \omega^r} \left(\frac {y^{\omega}} {\omega}\right) 
= \left(\frac {y^{\omega}} {\omega}\right) \left\{(\log y)^r + \sum_{i=1}^r \frac {(-1)^i r \cdots (r-i+1) (\log y)^{r-i}} {\omega^i} \right\}$$

```md
$\Z$ を $\mathbb{Z}$ のエイリアスとして定義しました。また $a*b$ は $a \times b$ となるように乗算記号も手を入れています。
```

$\Z$ を $\mathbb{Z}$ のエイリアスとして定義しました。また $a*b$ は $a \times b$ となるように乗算記号も手を入れています。

```
$\unknown$ なコマンドは使わないこと。
```

$\unknown$ なコマンドは使わないこと。

#### 参考

- [VuePress で markdown-it-katex | memo](https://naranoshika.netlify.com/post/vuepress/markdown-it-katex.html#%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%81%A8%E8%A8%AD%E5%AE%9A)
- [iktakahiro/markdown-it-katex: Add Math to your Markdown with a KaTeX plugin for Markdown-it](https://github.com/iktakahiro/markdown-it-katex)

### ソースコード ハイライト

- [Markdown Extensions | VuePress](https://vuepress.vuejs.org/guide/markdown.html#syntax-highlighting-in-code-blocks)

既定だと行数が表示されるので、お好みで非表示に。

```js
  markdown: {
      lineNumbers: false,
```

### Emoji

- [Markdown Extensions | VuePress](https://vuepress.vuejs.org/guide/markdown.html#emoji)

```
:tada: :100: :thinking:
```

:tada: :100: :thinking:

### 目次

- [Markdown Extensions | VuePress](https://vuepress.vuejs.org/guide/markdown.html#emoji)

```
```



### 定義リスト

```bash
$ yarn add markdown-it-deflist --dev
```

```
パターン認識
:   パターン認識（パターンにんしき、英: Pattern recognition）は自然情報処理のひとつ。
画像・音声などの雑多な情報を含むデータの中から、一定の規則や意味を持つ対象を選別して取り出す処理である。

サポートベクターマシン *(support vetor machine; SVM)*
:   サポートベクターマシン（英: support vector machine, SVM）は、教師あり学習を用いるパターン認識モデルの一つである。
    分類や回帰へ適用できる。

    サポートベクターマシンは、現在知られている手法の中でも認識性能が優れた学習モデルの一つである。サポートベクターマシンが優れた認識性能を発揮することができる理由は、未学習データに対して高い識別性能を得るための工夫があるためである。
```

パターン認識
:   パターン認識（パターンにんしき、英: Pattern recognition）は自然情報処理のひとつ。
画像・音声などの雑多な情報を含むデータの中から、一定の規則や意味を持つ対象を選別して取り出す処理である。

サポートベクターマシン *(support vetor machine; SVM)*
:   サポートベクターマシン（英: support vector machine, SVM）は、教師あり学習を用いるパターン認識モデルの一つである。
    分類や回帰へ適用できる。

    サポートベクターマシンは、現在知られている手法の中でも認識性能が優れた学習モデルの一つである。サポートベクターマシンが優れた認識性能を発揮することができる理由は、未学習データに対して高い識別性能を得るための工夫があるためである。

## 新規ポスト


```md
---
title: {{ title }}
slug: hello-vuepress
date: 2019-12-28
category: {{ category }}
tags:
  - {{ tags }}
header-title: true
header-image:
  - /img/header/random-01.jpg
---

{{ overview }}

## <!--more-->

# {{ title }}


## はじめに
```

## デプロイ

### ブランチ構成

自分の場合、既に `openjny.github.io` レポジトリを次のように使っていました。

- `master` ブランチ: 静的ファイルの配置用
- `src` ブランチ: hexo の設定/記事ファイルの管理用

なので `src` はそのままにして、`vuepress` 用の孤児ブランチを作ることにしました。

```bash
$ cd vuepress-blog

$ git init
$ git checkout -b vuepress
$ git add -A
$ git commit -m ":tada: first commit!"

$ git remote add -t vuepress origin git@github.com:openjny/openjny.github.io.git
$ git push -u origin vuepress
```

これで今度からは `vuepress` ブランチを使えば良い。

```bash
$ git clone --branch vuepress git@github.com:OpenJNY/openjny.github.io.git blog
$ cd blog
```

## 継続的インテグレーション

[公式の方法](https://vuepress.vuejs.org/guide/deploy.html#github-pages) に従って、以下のようなスクリプトも書いてはみたものの、結局 Travis の `page` provider に頼った。

https://github.com/OpenJNY/openjny.github.io/blob/vuepress/.travis.yml

```sh
#!/usr/bin/env sh

# abort on errors
set -e

# build
yarn build

# navigate into the build output directory
cd "${VUEPRESS_DIR}/.vuepress/dist"

git init
git add -A
git commit -m "Publishing site on $(date "+%Y-%m-%d %H:%M:%S")"

# if you are deploying to https://<USERNAME>.github.io
git push -f --quiet "https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_USER}.github.io.git" master

cd -
```

## 今後の予定

自由に Vue ファイルを書いて機能を追加出来るので、javascript の勉強がてら書いてみたい。

- Google Analytics
- Tags/Category ページ
- コメント

### 参考サイト

- [VuePress で Google Anayltics と Search Console を設定する | memo](https://naranoshika.netlify.com/post/vuepress/google-analytics-and-search-console.html)
- [VuePressにblogの機能を追加していく | tomopictのblog](https://tomopict.netlify.com/posts/2019/05/03/_20190225.html#theme-%E3%82%92%E6%9B%B4%E6%96%B0%E3%81%97%E3%81%A6%E3%81%84%E3%81%8F)
- [Vssue](https://vssue.js.org/)
- [Theme Guide | vuepress-theme-meteorlxy](https://vuepress-theme-meteorlxy.meteorlxy.cn/posts/2019/02/27/theme-guide-en.html#posts-comments)
