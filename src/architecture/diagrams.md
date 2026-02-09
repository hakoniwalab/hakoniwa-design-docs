# 図版一覧

(Informative)

本章は、今後維持する図版の一覧とプレースホルダを示す。

## 予定する図版
- スタック（層）図
- Data Plane / Control Plane フロー図
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
