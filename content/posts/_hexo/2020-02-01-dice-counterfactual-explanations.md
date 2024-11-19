---
title: "DiCE: 反実仮想サンプルによる機械学習モデル解釈"
slug: dice-counterfactual-explanations
date: 2020-02-01
categories:
  - Machine Learning
tags:
  - Explainable AI
  - Counterfactual Machine Learning
isCJKLanguage: true
---

[Open-source library provides explanation for machine learning through diverse counterfactuals](https://www.microsoft.com/en-us/research/blog/open-source-library-provides-explanation-for-machine-learning-through-diverse-counterfactuals/) を読んだのでそのまとめです。

## <!--more-->

## はじめに

この記事を一言で要約すると、反実仮想的な説明に基づく機械学習モデル解釈手法に対する Microsoft Research の取り組みと、その成果 (アルゴリズム) を実装した Python ライブラリ **DiCE** の紹介記事です。

{{< figure src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/127839/eb79aae3-b36e-38d4-ad1c-ef8e9aa81f40.png" caption="image.png" >}}

## 記事の要約

* 昨今のブラックボックス機械学習モデルの解釈手法 (e.g. LIME) は、予測の理由にのみ注意が向けられており、**反実仮想 (counterfactuals)** を考慮できていない
    * 例えば、銀行からローンが借りれなかった人が「なぜ借りれなかったか？」や「あなたのどういう特性を見て貸与しなかったか」は言える
    * しかし「これからどういう状態になれば借りれるのか？」という未来の意思決定に直接関わる情報を言及できない
* そこで、**反実仮想的な説明 (counterfactual explanation)**[^cf] を出力するアルゴリズムが必要
    * あるサンプルの反実仮想的な説明 = 狙った出力結果となる、似たようなサンプル (代替案)
    * 反実仮想的説明は、サンプルの perturbation[^perturbation] であることから**敵対的サンプル (adversarial examples)** に近い概念のものだが、意思決定/現実世界の制約のために、特徴の部分集合を変更してはいけない要請 (e.g. 年齢は変わらない) が存在する点が大きく異なる
    * ref: [Counterfactual Explanations without Opening the Black Box: Automated Decisions and the GDPR](https://arxiv.org/abs/1711.00399)
* Microsoft Research はこの問題に対し、**有益な反実仮想サンプルを列挙するフレームワーク**を提案 [(ACM FAT 2020)](https://www.microsoft.com/en-us/research/publication/explaining-machine-learning-classifiers-through-diverse-counterfactual-examples/)
    * まずはじめに、反実仮想を考えても良い特徴の値を変えつつ、それと同時に元サンプルとの近さも保つような**同時最適化問題を定式化**し、これにより大量の仮想サンプルを生成する (両者のトレードオフを調整する機能も提供)
    * さらに、反実仮想サンプルの**有益性**を図る指標も開発
        * 良い反実仮想サンプル = そのサンプルで学習させた単純な機械学習モデル (e.g. k-NN) によって、局所的に元の機械学習モデルを近似できる
* 課題
    * 応用のドメインに応じて反実仮想サンプル生成を調節する方法を考えないといけない
    * 特に**特徴量間の因果関係**を陽に扱う手法が重要
        * そうでなければ、例えば「年を取らずに学歴を積め👊」みたいなサンプルが出力されてしまう
        * NeurIPS 2019 の Workshop  "Do the right thing": machine learning and causal inference for improved decision making [[link]](http://tripods.cis.cornell.edu/neurips19_causalml/) で、今後のための問題を提起
* 実装に関して
    * [DiCE (Diverse Counterfactual Explanations)](https://github.com/microsoft/DiCE) という名前の Python パッケージで実装を公開
    * 現在はモデルとして Tensorflow しか入力出来ないが、将来的に PyTorch/sckit-learn も扱えるように動いている[^models]
    * 将来的に [InterpretML](https://github.com/interpretml/interpret-community) や Azure AutoML と統合される予定

## DiCE

GitHub: https://github.com/microsoft/DiCE

### インストール

DiCE のインストールは pip で `setup.py` を実行する方法しか今 (2020-02-01) の所ありません。

```bash
git clone https://github.com/microsoft/DiCE.git dice
cd dice
pip install .
```

注意点として TensorFlow 1.13 で開発を行っているようで、まだ 2.x には対応していません。

### チュートリアル

https://github.com/microsoft/DiCE/tree/master/notebooks

公式で 3 つのチュートリアル (jupyter notebook) が公開されています。
それぞれの notebook へのリンク、colab で開くリンク、簡単な説明を記しておきます。

- [DiCE_getting_started.ipynb](https://github.com/microsoft/DiCE/blob/master/notebooks/DiCE_getting_started.ipynb) [[colab](https://colab.research.google.com/github/microsoft/DiCE/blob/master/notebooks/DiCE_getting_started.ipynb)]:
    - DiCE の API 利用方法の簡単な レクチャー
- [DiCE_with_advanced_options.ipynb](https://github.com/microsoft/DiCE/blob/master/notebooks/DiCE_with_advanced_options.ipynb) [[colab](https://colab.research.google.com/github/microsoft/DiCE/blob/master/notebooks/DiCE_with_advanced_options.ipynb)]:
    - feasibility を考慮した perturbation (特徴量の変化量についての重み付け)
- [DiCE_with_private_data.ipynb](https://github.com/microsoft/DiCE/blob/master/notebooks/DiCE_with_private_data.ipynb) [[colab](https://colab.research.google.com/github/microsoft/DiCE/blob/master/notebooks/DiCE_with_private_data.ipynb)]: 
    - 訓練データがなく学習済みモデルしか存在しない場合の反実仮想サンプル生成

colab で開く際は、最初に以下の 2 つのセルを実行してください。

```
%tensorflow_version 1.x
```
```
!git clone https://github.com/microsoft/DiCE.git dice && cd dice && pip install .
```

### Roadmap

https://microsoft.github.io/DiCE/includeme.html#roadmap

今後の開発ロードマップとして、PyTorch や scikit-learn モデルへの対応や、新たな反実仮想サンプル生成アルゴリズムの実装、因果関係を考慮した手法の組み込み等がドキュメントに記されています。

> We are working on adding the following features to DiCE:
>
> - Support for PyTorch and scikit-learn models
> - Support for using DiCE for debugging machine learning models
> - Support for other algorithms for generating counterfactual explanations
> - Incorporating causal constraints when generating counterfactual explanations

## 所感

機械学習モデルの解釈手法も成熟してきつつあり、[原先生](https://www.slideshare.net/SatoshiHara3) の [Lasso 解列挙手法 [AAAI 2017]](https://www.aaai.org/ocs/index.php/AAAI/AAAI17/paper/viewFile/14304/14364) のような、解釈した先の意識決定を意識するフェーズに来ているのかなと思いました。
そのような方法の一つとして、反実仮想的な説明/反実仮想サンプルの着想は非常に理にかなっており、今後も発展が期待されます。
ただ、ライブラリ実装がまだ豊富ではなさそうなので、その辺りの進展が望まれるところですね。

## 参考文献

- [Open-source library provides explanation for machine learning through diverse counterfactuals - Microsoft Research](https://www.microsoft.com/en-us/research/blog/open-source-library-provides-explanation-for-machine-learning-through-diverse-counterfactuals/)
- [[1711.00399] Counterfactual Explanations without Opening the Black Box: Automated Decisions and the GDPR](https://arxiv.org/abs/1711.00399)
- [Explaining Machine Learning Classifiers through Diverse Counterfactual Examples - Microsoft Research](https://www.microsoft.com/en-us/research/publication/explaining-machine-learning-classifiers-through-diverse-counterfactual-examples/)
- [microsoft/DiCE: Generate Diverse Counterfactual Explanations for any machine learning model.](https://github.com/microsoft/dice)
- [NeurIPS19 CausalML | Cornell TRIPODS Center for Data Science for Improved Decision Making](http://tripods.cis.cornell.edu/neurips19_causalml/)
- [colabでLIMEとSP-LIMEを動かす。 - Qiita](https://qiita.com/irisu-inwl/items/a4d44efa81935884c725)
- [機械学習モデルの判断根拠の説明](https://www.slideshare.net/SatoshiHara3/ss-126157179)

[^cf]: 独自の訳です
[^perturbation]: 一部/あるいはすべての特徴量の値を微妙に変化させること
[^models]: Documentation の [Roadmap](https://microsoft.github.io/DiCE/includeme.html#roadmap) を参照
