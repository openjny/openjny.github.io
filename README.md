# openjny.github.io

## ローカル環環のセットアップ

1. Hugo のインストール
2. リポジトリのクローン

```bash
git clone --recursive github.com:openjny/openjny.github.io.git
gh repo clone openjny/openjny.github.io -- --recursive
```

3. テーマのサブモジュールを更新

```bash
cd openjny.github.io
git submodule update --init --recursive
```

## テーマ特化のマークダウン表記

```bash
# note, tip, example, question, info, warning, error

{{< notice note >}}
# notice
{{< /notice >}}

# figure
{{< figure src="./path.png" caption="caption" width=200 >}}

# ref
[link]({{< ref "path-to-another.md" >}})
```

## スクリプト

新しい post を作成する:

```bash
uvx python ./scripts/new-post.py "slug-for-new-post"
```

zenn からの移行:

```bash
uvx python ./scripts/convert-from-zenn.sh old.md > new.md
```
