# openjny.github.io

## Markdown 表記

### テーマに関するもの: hugo-coder

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

## 移行

## スクリプト

新しい post を作成する:

```bash
uvx python ./scripts/new-post.py "slug-for-new-post"
```

zenn からの移行:

```bash
uvx python ./scripts/convert-from-zenn.sh old.md > new.md
```
