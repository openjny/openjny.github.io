---
applyTo: "content/**/*.md"
---

# Theme Instructions

## Notice block

```
{{< notice TYPE "title" >}}
Content of the notice block.
{{< /notice >}}
```

TYPE: `note`, `tip`, `example`, `question`, `info`, `warning`, `error`

## Figure

```
{{< figure src="path/to/image.png" caption="Caption for the image" >}}
{{< figure src="path/to/image.png" caption="Caption for the image" width=200 >}}
```

## Reference

```
[Link text]({{< ref "path-to-another.md" >}})
```
