# 図版一覧

(Informative)

本章は、今後維持する図版の一覧とプレースホルダを示す。

## 予定する図版
- スタック（層）図
- Data Plane / Control Plane フロー図
- Epoch / Owner 遷移（概念シーケンス）図
- ランタイムトポロジ図

## スタック（層）図（プレースホルダ）
```mermaid
flowchart TB
  L0[Hardware / OS]
  L1[Hakoniwa Assets]
  L2[Data Plane: EU + Endpoint]
  L3[Control Plane: Conductor + Registry + Remote API]
  L4[Declarative Design: Schema + Generator + Validation]

  L0 --> L1 --> L2 --> L3 --> L4
```

キャプション: 概念構造を示すスタック図であり、配置や実行環境の具体を表すものではない。Registry は構成情報の保持ロールであり、意味論の権威ではない。

## Data Plane / Control Plane フロー図（プレースホルダ）
```mermaid
flowchart LR
  subgraph DataPlane[Data Plane]
    EU[Execution Units]
    EP[Endpoint]
    EU --> EP
  end

  subgraph ControlPlane[Control Plane]
    COND[Conductor]
    REG[Registry]
    API[Remote API]
    API --> COND --> REG
  end

  EP <--> BRG[Bridge]
  BRG <--> COND
```

キャプション: 概念的な平面分離と境界横断を示す図であり、配置やネットワーク構成の具体を表すものではない。Registry は構成情報の保持ロールであり、意味論の権威ではない。

## Epoch / Owner 遷移図（プレースホルダ）
```mermaid
sequenceDiagram
  participant A as Asset A (Owner: Epoch N)
  participant B as Asset B (Owner: Epoch N+1)
  participant BRG as Bridge / Endpoint
  participant COND as Conductor

  Note over A,BRG: Epoch N における Data Plane 実行
  A ->> BRG: PDU送信 (Epoch N)
  BRG -->> A: Epoch N として配信

  Note over COND: Control Plane による遷移確定
  COND ->> BRG: Epoch N の Commit Point 確定
  COND ->> B: Epoch N+1 の Owner 割当
  BRG -->> B: Epoch N+1 の配信を有効化

  Note over B,BRG: Epoch N+1 における Data Plane 実行
  B ->> BRG: PDU送信 (Epoch N+1)
  BRG -->> B: Epoch N+1 として配信
```

キャプション: Conductor が Commit Point を確定し、次の Epoch の Owner を割り当てる流れを示す概念図。配置やプロトコル仕様を表すものではない。
