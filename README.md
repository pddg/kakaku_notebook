# これは？

ブログで作ったノートパソコンのデータの集計をするプログラム．[価格.com](http://kakaku.com/pc/note-pc/?lid=pc_hotcategory_pc02)から取得した情報を元に
各種の平均値を算出して棒グラフにする．

## 環境

macOS Sierra 10.12.3のPython3.5.2において以下のライブラリを導入して実行した．

* beautifulsoup4==4.5.3
* cycler==0.10.0
* lxml==3.7.2
* matplotlib==2.0.0
* numpy==1.12.0
* pandas==0.19.2
* pyparsing==2.1.10
* python-dateutil==2.6.0
* pytz==2016.10
* scipy==0.18.1
* seaborn==0.7.1
* selenium==3.0.2
* six==1.10.0
* SQLAlchemy==1.1.5

また，javascript実行のためにPhantomJSを用いる．

```sh
$ brew install phatomjs
```

パスが通っているか確認すること．

## ライセンス

MIT
