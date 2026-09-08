# 箱庭時刻同期の実装における時刻差の上界（1段構成）

## 1. 目的と結論

本稿は、1つのコアと複数のアセットからなる**1段構成**について、確認した実装の更新規則からシミュレーション時刻差の上界を証明する。[既存の理論文書](hakoniwa-time.md)を置き換えるものではなく、実装との差を明示する補足資料（Informative）である。多段構成および進行性の証明は対象としない。

コア側の実装は、次の時刻ではなく**現在の時刻差**が設定値 $D_{\max}$ 未満であることを確認してから、$\Delta T_c$ だけ進む。一方、アセット側は**次の時刻**が観測したコア時刻以下である場合だけ進む。

以下の前提の下で、任意のウォール時刻 $t$ において、

$$
\boxed{\quad 0 \le T_c(t)-T_i(t)<D_{\max}+\Delta T_c \quad (\forall i) \quad} \tag{I.1}
$$

が成立する。したがって、任意のアセットのペアについて、

$$
\boxed{\quad |T_i(t)-T_j(t)|<D_{\max}+\Delta T_c \quad (\forall i,j) \quad} \tag{I.2}
$$

が成立する。論文で保守的な閉じた上界として $|T_i-T_j|\le D_{\max}+\Delta T_c$ と記述することもできるが、実装の厳密な不等号から得られる結果は **「未満」** である。

ここで $D_{\max}$ は**実装の停止判定に用いる閾値**であり、それ自体が任意の刻み幅に対して保証される時刻差の上界ではない。実効的な保証幅を $B_{\mathrm{impl}}=D_{\max}+\Delta T_c$ と区別する。超過量はコアの1ステップ幅未満であり、ステップ数に応じて累積しない。

## 2. 対象ソースと既存理論との差

### 2.1. 参照版

可変な `main` ではなく、次のコミットに固定して参照する。確認日は2026年9月8日である。

| 対象 | 固定参照 |
| :--- | :--- |
| コアの更新規則 | [`hako_time.cpp`](https://github.com/toppers/hakoniwa-core-cpp/blob/b8f6b38789934f716c675c4fc6f0708682fe6975/src/hako/core/simulation/time/hako_time.cpp)、`TheWorld::time_begins_to_move()` |
| アセットの更新規則 | [`hako_asset_impl.cpp`](https://github.com/hakoniwalab/hakoniwa-core-pro/blob/632fc885da2b81b2f6abf33c300fbedc74576f8b/sources/assets/callback/src/hako_asset_impl.cpp#L513-L560)、`hako_asset_impl_execute()` |
| コアの時刻型 | [`hako_types.hpp`](https://github.com/toppers/hakoniwa-core-cpp/blob/b8f6b38789934f716c675c4fc6f0708682fe6975/src/include/types/hako_types.hpp#L11-L14)、マイクロ秒単位の `int64_t` |
| 比較する理論 | [`hakoniwa-time.md`](https://github.com/hakoniwalab/hakoniwa-design-docs/blob/b3c0b611e449526aed7f22bb2950bbf62bb2083f/src/math/hakoniwa-time.md) のアセット・コア更新規則 |

これは上記2つの更新規則を組み合わせたモデルの証明である。個々の評価実験で使ったバイナリ・依存コミットがこの組合せに一致することまで、参照だけで保証するものではない。論文の評価対象については、実際のビルド構成と対応付ける必要がある。

### 2.2. コア側

時刻に関係する判定と更新は、次のコードである。

```cpp
HakoTimeType diff = asset_time - this->world_time_usec_;
if (diff <= -this->max_delay_time_usec_)
{
    canStep = false;
    break;
}
// 全アセットについて判定した後
if (canStep) {
    this->world_time_usec_ += this->delta_time_usec_;
}
```

`diff <= -max_delay` は、そのアセットに対する現在の遅れが $D_{\max}$ **以上なら停止する**ことを意味する。従って進行条件は「すべてのアセットに対する現在の差が $D_{\max}$ **未満**」である。

### 2.3. アセット側

```cpp
hako_time_t next_time =
    hako_asset_instance.current_usec + hako_asset_instance.delta_usec;
if (next_time > world_time) {
    return false;
}
// コールバックを実行した後
hako_asset_instance.current_usec = next_time;
```

`next_time == world_time` なら進めるため、時刻についての進行条件は $T_i+\Delta T_i\le\widehat T_{c,i}$ である。コールバック呼出し前の時刻を $T_i$、`current_usec = next_time` で確定した時刻を $T_i+\Delta T_i$ と対応付ける。

この関数では、`notify_simtime(..., current_usec)` は関数冒頭にあり、`current_usec` の更新より前に実行される。従って、**アセット内部の完了時刻と、コアが読める通知値を同一視しない**。本稿は後述の観測値を導入してこの差を扱う。

### 2.4. 判定条件の比較

最新値が読める場合の現在差を $g=T_c-\min_iT_i$ と置く。

| 更新対象 | 既存理論の時刻進行条件 | 今回の実装の時刻進行条件 |
| :--- | :--- | :--- |
| アセット $i$ | $T_i+\Delta T_i\le T_c$ | 同じ。ただし参照値は観測したコア時刻 |
| コア | $g+\Delta T_c\le D_{\max}$ | $g<D_{\max}$ |

差が現れるのは $D_{\max}-\Delta T_c<g<D_{\max}$ の領域である。現在差がちょうど $D_{\max}$ なら両者とも停止するため、単に等号だけを入れ替えた差ではない。

## 3. モデルと前提

### 3.1. 記号

| 記号 | 意味 |
| :--- | :--- |
| $t$ | ウォール時刻（実世界の時刻） |
| $T_c(t)$ | コアが保持する、確定したシミュレーション時刻 |
| $T_i(t)$ | アセット $i$ の `current_usec` に対応する、確定したシミュレーション時刻 |
| $\Delta T_c>0$ | コアの1回のシミュレーション時刻増分 |
| $\Delta T_i>0$ | アセット $i$ の1回のシミュレーション時刻増分 |
| $D_{\max}>0$ | コアの現在差に対する停止判定閾値 |
| $\widehat T_i$ | あるコア更新の判定に使われるアセット $i$ の通知・観測時刻 |
| $\widehat T_{c,i}$ | あるアセット $i$ の更新判定に使われるコアの観測時刻 |

$D_{\max},\Delta T_c,\Delta T_i$ はすべて**シミュレーション時間**の量である。ウォール時間の実行間隔 $\Delta t_c,\Delta t_i$ や通信時間とは異なる。本稿の安全性証明では、一定のウォール時間間隔を仮定しない。

### 3.2. 前提条件

1. **固定された1段構成**：コアは1つ、同期対象のアセット集合は $\{1,\ldots,n\}$、$n\ge1$ とする。コアは進行前に、この集合の全アセットを判定する。外部利用などによりこの集合に入っていないアセットは保証対象外である。
2. **同一の実行区間**：$T_c(0)=T_i(0)=0$ とし、その区間内で巻き戻し、リセット、時刻の強制代入、アセットの追加・除去を行わない。リセットをまたぐ場合は、初期条件を再び満たす区間ごとに議論する。
3. **更新の直列化と単調性**：各コンポーネント自身の時刻更新は直列に実行し、増分を一度だけ確定する。コールバックなどが同じ時刻を別経路から変更しない。確定時刻は増加または停留のみであり、有限ウォール時間中の更新回数は有限とする。
4. **保守的な観測**：判定で読む値は同じ実行区間の有効な過去または現在の確定値である。未来時刻の通知、未完了ステップの完了通知、破損値、読み取り途中の値の混成は認めない。読み取りや通知の遅延、アセットごとに異なる観測時刻は認める。
5. **数値・設定の健全性**：$D_{\max}$ と各増分は固定の正値であり、加減算・比較で整数オーバーフローや数値誤りが生じない。共通の時間単位を使用する。
6. **対象の意味**：保証するのは上記ソフトウェアの確定した論理時刻である。シミュレータ内部の未報告の積分サブステップやPDUの内容に、同じ保証が自動的に及ぶとは仮定しない。

アセット間の相互通信、同時の全アセット時刻スナップショット、同一の刻み幅、ウォールクロックの一致、公平なスケジューリングは、この安全性証明の前提ではない。ただし、進行性や実時間性能を保証するには別の前提が必要になる。

### 3.3. 観測遅延の扱い

更新の確定時における実際の時刻に対して、その判定に用いた値は、単調性により

$$
\widehat T_i\le T_i,\qquad \widehat T_{c,i}\le T_c \tag{I.3}
$$

を満たす。各値が異なる時刻に読み取られていても、この不等式は各アセットについて個別に成り立つ。

特に、観測列自体が常に最新値へ単調に更新されることまでは要求しない。有効な古い値を再び読む場合でも、その値が現在の確定値以下であればよい。観測誤差の大きさや通信遅延の上限を式(I.1)に加算する必要はない。

## 4. 実装の更新規則

確定した時刻の更新をイベントとして並べる。異なるコンポーネントの実行は任意に交錯してよい。判定から確定までの間に相手が進んでも、式(I.3)の向きは変わらない。自分自身の更新は直列化されるため、その間に別の自分の更新が割り込むことはない。

### アセットの更新

$$
T_i^+=
\begin{cases}
T_i+\Delta T_i & \text{if }T_i+\Delta T_i\le\widehat T_{c,i},\\
T_i & \text{otherwise}.
\end{cases} \tag{I.4}
$$

### コアの更新

$$
T_c^+=
\begin{cases}
T_c+\Delta T_c & \text{if }T_c-\widehat T_i<D_{\max}\quad\text{for all }i,\\
T_c & \text{otherwise}.
\end{cases} \tag{I.5}
$$

状態確認やPDU同期モードなどの追加条件によって、時刻条件を満たしていても更新しないことがある。それらはこのモデルでは停留として扱う。時刻条件を迂回して進む別経路は対象としない。

## 5. 安全性の証明

**定理（実装の1段時刻差上界）**：第3節の前提と式(I.4)、(I.5)の更新規則の下で、式(I.1)がすべての $t\ge0$ について成立する。

**証明**：$B=D_{\max}+\Delta T_c$ と置き、不変条件

$$
\mathcal I:\quad 0\le T_c-T_i<B\quad(\forall i) \tag{I.6}
$$

を、確定時刻更新のイベント数に関する帰納法で示す。

### 5.1. 初期状態

すべての時刻がゼロなので $T_c-T_i=0$ であり、$B>0$ より $\mathcal I$ は成立する。

### 5.2. コアが進む場合

進行条件から、すべての $i$ について

$$
T_c-\widehat T_i<D_{\max}.
$$

観測値は現在のアセット時刻以下なので、更新後の差は

$$
\begin{aligned}
T_c^+-T_i
&=T_c+\Delta T_c-T_i\\
&\le T_c+\Delta T_c-\widehat T_i\\
&<D_{\max}+\Delta T_c=B.
\end{aligned} \tag{I.7}
$$

また、帰納法の仮定から $T_i\le T_c$ であり、コアは正の増分だけ進むため $T_i\le T_c^+$ である。従って上下の不等式がともに維持される。

### 5.3. アセット $i$ が進む場合

進行条件と式(I.3)から、

$$
T_i^+=T_i+\Delta T_i\le\widehat T_{c,i}\le T_c. \tag{I.8}
$$

従って更新後も $0\le T_c-T_i^+$ である。一方、$T_i^+\ge T_i$ なので、

$$
T_c-T_i^+\le T_c-T_i<B. \tag{I.9}
$$

他のアセットの時刻はこのイベントでは変わらないため、それらの不等式も維持される。

### 5.4. 停留・通知・読み取りの場合

いずれの確定時刻も変わらなければ、$\mathcal I$ は維持される。通知値が変わるだけの場合も同様である。通知の有効性は次回の更新で式(I.3)として使用する。

以上より、すべての更新後に $\mathcal I$ が成立する。確定時刻はイベント間で一定であるため、任意のウォール時刻でも成立する。同じウォール時刻に複数の更新を位置付ける場合も、上記の前提を満たす確定順序で扱える。よって式(I.1)が証明された。□

### 5.5. アセット間の差

式(I.1)を全アセットについてまとめると、

$$
\max_iT_i\le T_c<\min_iT_i+B. \tag{I.10}
$$

従って、アセット全体の時刻幅 $W(t)$ は

$$
\begin{aligned}
W(t)&=\max_iT_i(t)-\min_iT_i(t)\\
&\le T_c(t)-\min_iT_i(t)\\
&<B=D_{\max}+\Delta T_c.
\end{aligned} \tag{I.11}
$$

任意のペアについて $|T_i-T_j|\le W(t)$ であるため、式(I.2)が得られる。すべてのアセットがコアの**後方**にあるので、三角不等式から得られる粗い $2B$ ではなく、$B$ で抑えられる。

この証明では、コアが進むたびに現在の通知値から式(I.7)を立て直す。前回の上界にステップ幅を繰り返し足す議論ではない。従って、$D_{\max}$ を超える余裕は $\Delta T_c$ 未満にとどまり、長時間実行による累積ドリフトにはならない。

## 6. 境界・具体例・整数時間での補強

### 6.1. $D_{\max}$ を超える到達可能な例

時間単位を $\mu\mathrm{s}$ とし、$D_{\max}=100$、$\Delta T_c=10$、遅いアセットSの増分を $1$、速いアセットFの増分を $10$ とする。更新順序を次のように選ぶ。

| 段階 | 操作 | $T_c$ | $T_S$ | $T_F$ |
| :--- | :--- | ---: | ---: | ---: |
| 0 | 初期状態 | 0 | 0 | 0 |
| 1 | アセットを待機させたまま、コアが10回進む | 100 | 0 | 0 |
| 2 | Fを100まで進め、Sを1だけ進める | 100 | 1 | 100 |
| 3 | 上記時刻の通知後、コアが1回進む | 110 | 1 | 100 |
| 4 | Fが110まで進む | 110 | 1 | 110 |

段階1の各更新前の差は $0,10,\ldots,90$ なので、すべて許可される。段階3では現在の最遅差が $100-1=99<100$ のため、コアは110へ進める。段階4ではFの次時刻がコア時刻に一致するため、アセット側の判定も許可する。

この間、Sは完了時刻1を通知した後、次の時刻確定まで一時停止させる。例えば、次の `hako_asset_impl_execute()` の冒頭で通知し、その後のコールバック完了前に待機する実行順序でよい。永久停止を仮定する必要はない。

最終的に

$$
T_F-T_S=110-1=109>100=D_{\max}
$$

となる。従って、任意の刻み幅と更新順序に対して $D_{\max}$ 以内とする主張は、現在の更新規則では一般に成立しない。一方、$109<110=D_{\max}+\Delta T_c$ であり、証明した上界と一致する。

### 6.2. 整数時間の場合

時刻、$D_{\max}$、増分のすべてが共通量子 $q>0$ の整数倍なら、式(I.1)、(I.2)の右辺も $q$ の整数倍である。従って、

$$
T_c-T_i\le D_{\max}+\Delta T_c-q,\qquad
|T_i-T_j|\le D_{\max}+\Delta T_c-q. \tag{I.12}
$$

参照したコアの時刻型はマイクロ秒単位の `int64_t` である。全時刻と設定値を同じ整数マイクロ秒で扱う場合は $q=1\,\mu\mathrm{s}$ とできる。上の到達例は、この整数上界 $100+10-1=109$ に達する。

量子化しないモデルでも、$D_{\max}=\Delta T_c=a>0$、アセット増分を $\varepsilon$ と $a$（$0<\varepsilon<a$）とすれば、同様に $(T_c,T_S,T_F)=(2a,\varepsilon,2a)$ へ到達できる。幅は $2a-\varepsilon$ であり、$\varepsilon\to0^+$ により $D_{\max}+\Delta T_c$ に任意に近づく。従って、刻み幅について追加条件を置かずに補正項を一律に取り除くことはできない。

### 6.3. 刻みがそろう特殊ケース

初期時刻がゼロで、すべての $\Delta T_i$ と $D_{\max}$ が $\Delta T_c$ の整数倍なら、コア時刻と有効なアセット通知値も $\Delta T_c$ の整数倍となる。このとき、

$$
T_c-\widehat T_i<D_{\max}
\quad\Longleftrightarrow\quad
T_c-\widehat T_i\le D_{\max}-\Delta T_c.
$$

従ってコアの次時刻は $\widehat T_i+D_{\max}$ を超えず、この特殊ケースでは $|T_i-T_j|\le D_{\max}$ まで強められる。これは十分条件であり、一般の場合の式(I.2)と混同しない。刻みのそろった実験だけでは、両更新規則の違いが表れないことがある。

## 7. 保証範囲と論文への適用

**本稿が保証するもの**は、前提を満たす確定論理時刻の安全性である。観測遅延が有効な過去値を返す限り、その遅延は進行判定を保守的にするため、上界は変わらない。極端に古い観測によって停止し続けても、安全性とは矛盾しない。

**本稿が保証しないもの**は、デッドロック回避、一定速度での進行、実時間締切、通信時間の上限、数値積分誤差、物理モデルの妥当性、PDUのデータ年齢・因果関係・スナップショット整合性である。登録対象外のアセット、リセット混在、未来の完了時刻を通知する実装経路にも、そのまま適用できない。参照したC++プログラム全体のメモリ安全性・並行実行の正しさを機械検証したという主張でもない。

ICRA向けには、設定閾値 $D_{\max}$ と保証幅 $B_{\mathrm{impl}}$ を分け、**実装差分を含めても時刻幅は一様に有界であり、追加項はコアの1ステップだけである**と記述できる。ただし、評価実験が同じ更新規則と前提を満たすことは、ビルド構成・同期参加アセット・計測対象時刻と対応付けて確認する。実測で $D_{\max}$ を超えなかったことだけを、任意条件での $D_{\max}$ 上界の証明とはしない。

### 英文記述案（定理と証明の要約）

**Implementation-aware clock-skew bound for a single-level configuration.**
Consider one core and a fixed set of synchronized assets. Let $T_c$ and $T_i$ denote their committed simulation times, respectively. The implementation advances the core by $\Delta T_c$ if $T_c-\widehat T_i<D_{\max}$ for every asset, whereas asset $i$ advances only if $T_i+\Delta T_i\le\widehat T_{c,i}$. Here $D_{\max}$ is the configured stopping threshold, not necessarily the maximum realized skew. Assume zero initial times, monotone clocks, serialized updates within each component, no arithmetic overflow or rollback, and observations of valid committed times from the same execution epoch. Observations may be stale: $\widehat T_i\le T_i$ and $\widehat T_{c,i}\le T_c$.

Under these assumptions, for every wall-clock time $t$,

$$
0\le T_c(t)-T_i(t)<D_{\max}+\Delta T_c,
\qquad
\max_iT_i(t)-\min_iT_i(t)<D_{\max}+\Delta T_c.
$$

*Proof.* The invariant holds initially. On a core update, $T_c^+-T_i\le T_c+\Delta T_c-\widehat T_i<D_{\max}+\Delta T_c$, and increasing the core time preserves $T_i\le T_c$. On an asset update, $T_i^+\le\widehat T_{c,i}\le T_c$, while increasing $T_i$ can only decrease its lag behind the core. Stuttering and observation updates leave committed times unchanged. Induction over committed updates establishes the invariant. Since all asset times lie at or behind the core, their spread is at most $T_c-\min_iT_i$, which yields the pairwise bound. Thus the current-time guard introduces less than one core time step of additional skew, without accumulation over the execution. This is a safety result; liveness and physical simulation accuracy are not claimed.

## 8. 再現用のモデルチェック

補助スクリプト [`experiment/check_time_impl_bound.py`](experiment/check_time_impl_bound.py) は、上記の不等式を直接モデル化し、境界条件、整数上界への到達例、古い観測値の保守性、および小規模な到達状態の網羅探索を検査する。

```sh
python3 src/math/experiment/check_time_impl_bound.py
```

網羅探索は、1または2アセット、$D_{\max}=1,\ldots,6$、$\Delta T_c=1,\ldots,4$、各 $\Delta T_i=1,\ldots,4$、コア時刻24以下の範囲で、進行可能な全コンポーネントの更新順序を探索する。

新しい観測値を使うモデルでは、古い観測値の場合に可能な更新も許可される。古い値は更新を禁止する方向にしか働かず、停留は確定時刻の状態を変えないため、この探索は遅延による停留も許した確定時刻列を包含する。ただし、これは数式モデルの有限範囲の補助検査であり、C++実装の実行試験や任意パラメータに対する証明の代替ではない。一般的な保証は第5節の帰納的証明による。
