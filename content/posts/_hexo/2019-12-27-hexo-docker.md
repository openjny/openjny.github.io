---
title: "Hexo 執筆のための Docker 環境"
slug: hexo-docker
date: 2019-12-27
categories:
  - その他
tags:
  - ブログ
  - SGG
  - Hexo
  - Docker
isCJKLanguage: true
---

hexo を使うための `nodejs, pandoc` 入りの Ubuntu 環境を作りました。

## <!--more-->

## Dockerfile

自分の馴染みの深い Ubuntu をベースに、hexo での作業環境を構築していきます。
要件としては次のような環境を目指します。

- Node.js (`npm`, `yarn`) が使える
- `pandoc` が使える
- `hexo-cli` が使える

基本 npm 使えりゃ hexo なんて動くんですが、なんでわざわざ Dockerfile を用意するかというと `pandoc` の存在です。hexo デフォルトの markdown レンダリング エンジンがあんまり気に入ってないので、`hexo-renderer-pandoc` を使っています。なので `pandoc` を用意する必要があり、環境毎に `pandoc` を用意するのが面倒で Dockerfile にまとめてしまいました。

できたのがこれ。

```dockerfile
ARG BASE_CONTAINER=ubuntu:18.04
FROM $BASE_CONTAINER
LABEL maintainer="OpenJNY <openjny@gmail.com>"

USER root

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git 
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*

# Install pandoc
# ref: https://github.com/jgm/pandoc/releases
ARG PANDOC_VERSION=2.9.1
ARG PANDOC_DEB=/tmp/pandoc.deb
RUN wget -O ${PANDOC_DEB} "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-amd64.deb" && \
    dpkg -i ${PANDOC_DEB} && \
    rm ${PANDOC_DEB}

# Install Node.js and yarn
# ref: https://github.com/nodesource/distributions/blob/master/README.md#deb
ARG NODEJS_VERSION=12
RUN curl -sL https://deb.nodesource.com/setup_${NODEJS_VERSION}.x | bash - && \
    apt-get install -y nodejs && \
    curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && \
    apt-get install yarn

# Install hexo-cli
RUN npm install -g hexo-cli

WORKDIR /blog
EXPOSE 4000
```

こんな感じで使ってください。

```bash
$ docker build . --tag hexo-ubuntu
$ docker run --rm -it -v $(pwd):/work -w /work -p 4000:4000 hexo-ubuntu /bin/bash
```
