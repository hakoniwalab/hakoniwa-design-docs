# 用語集

## 設計用語（Normative）
- 箱庭アセット（Hakoniwa Asset）: OSプロセスとして実行される単位。一つまたは複数の Execution Unit（EU）を内部に保持する。
- Execution Unit（EU）: 分散環境において同一の論理モデルを表す実行主体。EU は論理的存在であり、複数アセット上に実体を持ちうる。
- Owner / Non-Owner: EU に対して状態更新および PDU 書き込み責任を持つ主体／持たない主体。
- Epoch: EU に対する実行責任（Owner）が一意に定まっている実行権限の世代番号。
- Commit Point: Conductor による状態遷移に基づき、Epoch の更新が全体で合意され、当該 Epoch の実行結果と実行責任が意味論的に確定する境界点。
- Runtime Delegation（RD）: 実行中に EU の Owner を安全に切り替えるための機構。
- Conductor（箱庭コンダクタ）: EU に対する実行責任の状態遷移を管理し、Epoch の更新および Commit Point の成立を制御する主体。Conductor は数値計算を行わず、実行戦略や解法を決定しない。
- Data Plane: シミュレーション実行に必要な実データ（PDU等）の伝達・更新・時間進行を担う領域。
- Control Plane: 実行責任の移譲・世代管理・因果境界の確定・ポリシー適用を担う領域。
- Endpoint: データ伝達の境界。単なるメッセージAPIではなく、因果境界と配信・寿命セマンティクスを定義する。
- Bridge: Data Plane と Control Plane の境界整合を担保する中継ロール。
- Registry: システム全体の構成・定義情報を保持するロール。責任や因果の意味論は保持しない。
- Remote API: 制御操作や外部統合のためのAPI面。
- 有界ドリフト（Bounded Drift）: 時刻ズレが定義された上限（d_max または 2·d_max）に収まるという同期原理。

## 一般エンジニア向け用語（Informative）
- 論理時間（Logical Time）: シミュレーションモデル上で定義される時間軸。
- 実時間（Wall-clock Time）: 現実世界の経過時間。
- ΔT: 数値計算や通信における更新ステップ幅。
- d_max（最大許容遅延時間）: 分散実行においてシステム設計時に設定される最大通信遅延の上限。
- PDU（Protocol Data Unit）: シミュレーション構成要素間の通信に用いられるデータ単位。
- FMI（Functional Mock-up Interface）: 数値モデル（FMU）の交換・結合を目的としたインターフェース規格。
- FMI-CS（FMI for Co-Simulation）: FMIにおけるCo-Simulation向けプロファイル。
- FMU（Functional Mock-up Unit）: FMIで用いられるパッケージ化モデル。
- MA（Master Algorithm）: FMIのCo-Simulationで実行順序・ステップ制御・遅延処理を統括するアルゴリズム。
- HLA（High Level Architecture）: 分散イベント／論理時間シミュレーションの枠組み。
- RTI（Runtime Infrastructure）: HLAで論理時間進行と因果順序を管理するコンポーネント。
- HILS（Hardware-in-the-Loop Simulation）: 実機を含むリアルタイム制約下のシミュレーション。
