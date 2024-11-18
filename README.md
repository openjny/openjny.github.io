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

### スクリプト

- [ ]: 画像のダウンロードとリンクの自動修正

```bash
# zenn からの移行
./scripts/convert-from-zenn.sh /tmp/old.md
```
