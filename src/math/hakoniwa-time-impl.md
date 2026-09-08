# 現行実装に対応する1段時刻同期の安全性証明

本稿は、1つのコアと複数のアセットからなる**1段構成**について、実装の時刻更新規則からシミュレーション時刻差の上界を証明する。実装依存の解析（Informative）であり、[理想モデルの文書](hakoniwa-time.md)を変更・置換するものではない。多段構成、進行性、実時間性能は対象外とする。

結論は、以下に明記する前提の下で、任意のウォール時刻において

$$
\boxed{\max_i T_i(t) \le T_c(t) < \min_i T_i(t) + D_{\max} + \Delta T_c}
$$

が成立し、したがって任意のアセット対について

$$
\boxed{|T_i(t)-T_j(t)| < D_{\max}+\Delta T_c}
$$

が成立する、というものである。**厳密な結論は「未満」であり、「常にその幅だけずれる」「その値に必ず到達する」という意味ではない。** 非厳密な上界として $|T_i-T_j|\le D_{\max}+\Delta T_c$ と記載することも正しい。

## 1. 対象実装と位置付け

参照を再現可能にするため、調査時点（2026-09-08）のソースをコミットで固定する。

| 対象 | リポジトリと固定コミット | 対象箇所 |
|:--|:--|:--|
| コア | `toppers/hakoniwa-core-cpp` / `b8f6b38789934f716c675c4fc6f0708682fe6975` | `TheWorld::time_begins_to_move()` [S1] |
| アセット | `hakoniwalab/hakoniwa-core-pro` / `632fc885da2b81b2f6abf33c300fbedc74576f8b` | `hako_asset_impl_execute()` [S2] |
| 比較対象の理論 | `hakoniwalab/hakoniwa-design-docs` / `b3c0b611e449526aed7f22bb2950bbf62bb2083f` | `src/math/hakoniwa-time.md` [S3] |

アセット側の参照は、調査時の `main` を固定したものである。本稿はこの組み合わせから抽出した時刻更新則の証明であり、特定の配布バイナリの依存関係全体を検証したものではない。

理想モデルでは、コアが**次の時刻**で許容幅以内かを判定する。一方、対象実装では、コアが**現在の時刻差**で進行可否を判定してから $\Delta T_c$ を加算する。この差を取り込んだ上界を導くことが本稿の目的である。

## 2. 記号と前提

### 2.1. 記号

| 記号 | 意味・コードとの対応 |
|:--|:--|
| $t$ | ウォール時刻（実世界の時刻） |
| $n\ge1$ | 保証の対象とするアセット数 |
| $T_c(t)$ | コアの確定済みシミュレーション時刻。`world_time_usec_` |
| $T_i(t)$ | アセット $i$ の確定済みシミュレーション時刻。`current_usec` |
| $\Delta T_c>0$ | コアの1回のシミュレーション時刻増分。`delta_time_usec_` |
| $\Delta T_i>0$ | アセット $i$ の1回のシミュレーション時刻増分。`delta_usec` |
| $D_{\max}>0$ | コアの進行停止判定に使う設定閾値。`max_delay_time_usec_` |
| $\widetilde T_i$ | あるコア更新で参照する、アセット $i$ の通知・観測時刻 |
| $\widetilde T_{c,i}$ | あるアセット $i$ の更新で参照するコア時刻 |

大文字の $T,\Delta T,D_{\max}$ はシミュレーション時間単位である。$\Delta T_c$ はウォール時間での処理周期 $\Delta t_c$ ではない。本稿では、ウォール時間での周期を固定する必要はない。

ここでの $T_i$ はランタイムが管理する時刻カウンタであり、外部シミュレータが独自に保持する時計や、計算結果の物理的な精度を直接表すものではない。

### 2.2. 証明の前提

**A1：初期化と対象集合。** 1回のシミュレーション実行について $T_c(0)=T_i(0)=0$ とする。対象アセットの集合とパラメータは固定し、途中の時刻リセット、巻き戻り、参加・離脱、閾値変更を含めない。対象アセットはコアの判定用 `asset_times` に毎回含まれるものとする。対象外の外部プロセスには保証を拡張しない。

**A2：時刻更新の直列性。** コアの時刻は単一の更新主体が管理し、各アセットの時刻もそれぞれ単一の更新主体が管理する。時刻の変更は第3節の規則に従い、1回の増分は $0$ または所定の正の $\Delta T$ である。更新処理への再入や、コールバックからの無制御な時刻変更を含めない。

**A3：正しい過去値の観測。** 読み取る値は同じ実行内で実際に存在した時刻であり、通知遅延や通信遅延によって古くてもよい。各更新の確定直前の真のカウンタに対し、

$$
0\le\widetilde T_i\le T_i,\qquad
0\le\widetilde T_{c,i}\le T_c
$$

を満たす。全アセットを同一瞬間に観測する必要も、観測の遅延上限を設定する必要もない。過去の実行の値、未来値、破損値は含めない。

観測列そのものが単調に最新値へ更新されることまでは要求しない。同じ実行内の有効な古い値を再び読んでも、その値が更新確定直前の真のカウンタ以下であればよい。

**A4：数値と共有状態の健全性。** 時刻値を途中で壊れた値として読み取らず、加減算・符号反転・比較にオーバーフロー等がないものとする。各時刻の確定済み更新を事象列として扱えることを前提とする。C++メモリモデル、共有メモリの読み書きの原子性、全プラットフォームでの実装健全性そのものを、本稿の比較式の証明から導いたとはしない。

**A5：ウォール時刻との対応。** 有限のウォール時間区間内に無限回の更新が集中しないものとし、カウンタは更新の確定時に値が変わり、それ以外では一定とする。更新順序や処理速度の一致、公平なスケジューリング、必ず更新が完了することは、安全性の前提としない。

判定から代入までの処理全体が瞬時に終わる必要はない。自己の時刻に別の書き手がなく、途中で他の時刻が進んでも単調増加するため、A3の過去値条件を用いて扱える。

## 3. コードから得られる更新規則

以下では、ある更新の直前の値を $T_c,T_i$、直後の値を $T_c^+,T_i^+$ と書く。観測値はその更新で実際に参照した値を表す。

### 3.1. コア：現在の差が閾値未満なら進む

コアの停止条件は次のとおりである [S1]。

```cpp
HakoTimeType diff = asset_time - this->world_time_usec_;
if (diff <= -this->max_delay_time_usec_) {
    canStep = false;
    break;
}
```

`canStep` が真の場合にだけ `world_time_usec_ += delta_time_usec_` を行う。したがって更新則は

$$
T_c^+=
\begin{cases}
T_c+\Delta T_c & \text{if } T_c-\widetilde T_i<D_{\max}\quad(\forall i),\\
T_c & \text{otherwise}.
\end{cases}
\tag{1}
$$

である。**等号 $T_c-\widetilde T_i=D_{\max}$ では停止する。判定は次時刻ではない。**

### 3.2. アセット：次の時刻が観測コア時刻以下なら進む

アセットは、`next_time = current_usec + delta_usec` に対し、`next_time > world_time` なら停止する。進行時はコールバックの後に `current_usec = next_time` と確定する [S2]。時刻の進行条件は

$$
T_i^+=
\begin{cases}
T_i+\Delta T_i & \text{if }T_i+\Delta T_i\le\widetilde T_{c,i},\\
T_i & \text{otherwise}.
\end{cases}
\tag{2}
$$

である。**次時刻がコア時刻と等しい場合は進行できる。** 実際には実行状態やPDUに関する条件でも停止するが、それらが時刻を変更せず進行を抑制する限り、以下の安全性証明に影響しない。

### 3.3. 理想モデルとの差

$g=T_c-\min_i\widetilde T_i$ とすると、同じ観測値に対するコアの進行条件は次のように比較できる。理想モデル [S3] では観測値を最新値とみなす。

| モデル | コアの進行条件 |
|:--|:--|
| 理想モデルの次時刻判定 | $g+\Delta T_c\le D_{\max}$ |
| 対象実装の現在時刻判定 | $g<D_{\max}$ |

両者が異なるのは $D_{\max}-\Delta T_c<g<D_{\max}$ の領域であり、実装はこの領域でも1ステップ進む。現在差がちょうど $D_{\max}$ の場合は、どちらも停止する。したがって「等号だけが逆」なのではなく、**比較対象と境界条件の組み合わせ**が異なる。

## 4. 定理：コアと各アセットの時刻差上界

**定理1。** A1〜A5の下で式(1)、(2)に従う1段構成では、すべての対象アセット $i$ とすべての実行中のウォール時刻 $t$ について

$$
\boxed{0\le T_c(t)-T_i(t)<D_{\max}+\Delta T_c}
\tag{3}
$$

が成立する。

### 証明

コアおよび全アセットの確定済み時刻更新をまとめた事象列に対し、数学的帰納法を用いる。更新の順番は任意でよく、各更新が参照した値はA3に従う。

**初期状態。** A1より $T_c-T_i=0$。$D_{\max}+\Delta T_c>0$ なので式(3)は成立する。

以下では、ある更新の直前に、すべての $i$ について式(3)が成立していると仮定する。

**場合1：コアが進行する。** 式(1)の成功条件とA3より、すべての $i$ について

$$
T_c-\widetilde T_i<D_{\max},\qquad \widetilde T_i\le T_i.
$$

したがって、コア更新直後の差は

$$
\begin{aligned}
T_c^+-T_i
&=(T_c-\widetilde T_i)+\Delta T_c+(\widetilde T_i-T_i)\\
&\le(T_c-\widetilde T_i)+\Delta T_c\\
&<D_{\max}+\Delta T_c.
\end{aligned}
\tag{4}
$$

また帰納法の仮定と $\Delta T_c>0$ より、$T_c^+=T_c+\Delta T_c\ge T_i$。よって式(3)の両側が保存される。

**場合2：あるアセット $k$ が進行する。** 式(2)の成功条件とA3より

$$
T_k^+=T_k+\Delta T_k\le\widetilde T_{c,k}\le T_c.
\tag{5}
$$

したがって更新後もコアを追い越さない。一方、$\Delta T_k>0$ より

$$
T_c-T_k^+=T_c-T_k-\Delta T_k
\le T_c-T_k<D_{\max}+\Delta T_c.
\tag{6}
$$

他のアセットの差は変わらない。よって式(3)が保存される。

**場合3：待機、進行条件不成立、通知・観測だけの処理。** 確定済みの $T_c,T_i$ が変わらないので式(3)は保存される。観測値の変更は、次の時刻更新でA3を満たしていればよい。

以上で、任意の更新回数後に式(3)が成立する。A5より更新間では各カウンタが一定なので、更新時だけでなく任意のウォール時刻でも成立する。証明終。

## 5. 系：アセット集合の幅と任意のアセット対

**系1。** 定理1より

$$
\boxed{\max_i T_i\le T_c<\min_i T_i+D_{\max}+\Delta T_c}
\tag{7}
$$

が成立する。したがって、全アセットの時刻分布の幅は

$$
0\le\max_i T_i-\min_i T_i
\le T_c-\min_i T_i
<D_{\max}+\Delta T_c.
\tag{8}
$$

任意の $i,j$ に対して $|T_i-T_j|\le\max_k T_k-\min_k T_k$ なので

$$
\boxed{|T_i-T_j|<D_{\max}+\Delta T_c\quad(\forall i,j)}.
\tag{9}
$$

これは同一ウォール時刻での確定済みカウンタ間の保証である。異なるウォール時刻に取得したログ値をそのまま比較する主張ではない。

すべてのアセットがコアの後方にあるため、三角不等式だけから得られる粗い上界 $2(D_{\max}+\Delta T_c)$ ではなく、式(9)の幅で抑えられる。

### 5.1. なぜ追加項は $\Delta T_c$ だけなのか

コアだけが「現在の差」を判定してから進むため、その1回分の増分が上界に加わる。アセットは「次の時刻」でコアを追い越さないことを確認しているため、別途 $\Delta T_i$ を足す必要はない。$\Delta T_i$ が大きすぎて進行できなくても、安全性自体は成立する。

また、コアが進むたびに式(4)で上界を再確認するため、超過量が更新回数とともに累積することはない。アセット数 $n$ に比例する項も必要ない。

### 5.2. 通知・観測遅延があっても追加の遅延項が不要な理由

式(4)、(5)はすでに過去値を使っている。コアが古いアセット時刻を読むと遅れを大きく見積もり、アセットが古いコア時刻を読むと進行可能範囲を小さく見積もる。そのため、A3を満たす遅延は安全側に働く。

対象のアセット実装では `notify_simtime(current_usec)` が `hako_asset_impl_execute()` の冒頭にあり、`current_usec = next_time` より前に実行される [S2]。したがって、コアの通知値とアセットの現在値を常に等しいと仮定するのではなく、両者を区別する必要がある。コア側でも取得した `asset_times` を使って更新し、その結果を公開している [S4]。

A3の下では遅延の上限がなくても式(9)は保たれる。ただし、**停止し続けても安全性は成立するため、これは進行性や性能の保証ではない。**

## 6. 境界の意味と到達例

### 6.1. 整数時間での上界

$D_{\max},\Delta T_c,T_c,T_i$ がすべて共通の時間単位 $q>0$ の整数倍なら、式(3)、(9)はさらに

$$
T_c-T_i\le D_{\max}+\Delta T_c-q,
\qquad
|T_i-T_j|\le D_{\max}+\Delta T_c-q
\tag{10}
$$

と書ける。差も上界も $q$ の整数倍であることによる。

コアの `HakoTimeType` はマイクロ秒単位の `int64_t` と定義されている [S5]。全対象の時刻とパラメータを整数マイクロ秒で扱う場合、$q=1\,\mu\mathrm{s}$ を使える。これは表現可能な時間単位による補足であり、主定理に整数型や刻みの整列を要求するものではない。

### 6.2. $D_{\max}$ を超えるアセット間差は実際に到達可能

次の整数マイクロ秒の構成を考える。

$$
D_{\max}=100,\quad\Delta T_c=10,\quad
\Delta T_1=1,\quad\Delta T_2=10.
$$

観測遅延なしで、初期状態から次の実行順序を選ぶ。有限区間でアセット1の実行を遅らせるだけであり、不正な時刻通知を使わない。

| 処理後の状態 | $T_c$ | $T_1$ | $T_2$ | 説明 |
|:--|--:|--:|--:|:--|
| 初期化 | 0 | 0 | 0 | すべて一致 |
| コアが1回進行 | 10 | 0 | 0 | 現在差 $0<100$ |
| 両アセットが1回ずつ進行 | 10 | 1 | 10 | 両方の次時刻がコア以下 |
| コアだけが順に進行 | 100 | 1 | 10 | この区間の全コア更新が許可される |
| コアがさらに1回進行 | 110 | 1 | 10 | 判定時の最大差 $100-1=99<100$ |
| アセット2がコアに追いつく | 110 | 1 | 110 | アセット2は10刻みで追いつける |

通知が更新前に行われる対象実装でも、この確定時刻列は実現できる。アセット1は時刻1を次回の `hako_asset_impl_execute()` の冒頭で通知した後、次の時刻確定まで一時停止させればよい。アセット2も時刻10を通知した後に待機し、その後コアへ追いつく。永久停止や未来時刻の通知は必要ない。

最後の状態では

$$
|T_2-T_1|=109>100=D_{\max},
$$

かつ

$$
109=D_{\max}+\Delta T_c-1<110=D_{\max}+\Delta T_c.
$$

したがって、現行実装に対して無条件に $|T_i-T_j|\le D_{\max}$ と記載することはできない。式(10)の整数時間上界に達する構成も存在する。ただし、すべてのパラメータ構成でこの上界に達するという主張ではない。

量子化しないモデルでも、$D_{\max}=\Delta T_c=a>0$、アセット増分を $\varepsilon$ と $a$（$0<\varepsilon<a$）とすれば、同様に $(T_c,T_1,T_2)=(2a,\varepsilon,2a)$ へ到達できる。幅は $2a-\varepsilon$ であり、$\varepsilon\to0^+$ により $D_{\max}+\Delta T_c$ に任意に近づく。したがって、刻み幅について追加条件を置かずに補正項を一律に取り除くことはできない。

### 6.3. 刻みがそろう場合には、より強い $D_{\max}$ 上界も成立する

追加条件として、すべての $\Delta T_i$ と $D_{\max}$ が $\Delta T_c$ の正の整数倍であるとする。初期時刻ゼロと正しい過去値観測により、$g=T_c-\min_i\widetilde T_i$ も $\Delta T_c$ の整数倍となる。このとき

$$
g<D_{\max}
\iff g\le D_{\max}-\Delta T_c
\iff g+\Delta T_c\le D_{\max}.
$$

したがってコアの判定が理想モデルの次時刻判定と等価になり、同様の帰納法で $|T_i-T_j|\le D_{\max}$ を示せる。

これは**追加条件の下での改善**であり、主定理に必要な条件ではない。$D_{\max}$ が $\Delta T_c$ の整数倍というだけでは十分でないことは、第6.2節の例からも分かる。

## 7. ICRA向けに明確にすべき保証範囲

論文等での主張は、例えば次のように区別する。

> 固定された1段構成において、単調増加する論理時刻と同一実行内の正しい過去値観測を前提とする。コアは現在の最大時刻差が設定閾値 $D_{\max}$ 未満のときに $\Delta T_c$ だけ進み、アセットは次の時刻が観測コア時刻以下のときに進む。この実装では、任意の時点の任意のアセット対の論理時刻差は $D_{\max}+\Delta T_c$ 未満である。

本稿の $D_{\max}$ は**設定上の停止閾値**であり、一般構成における保証上界そのものではない。理想モデルの $D_{\max}$ 上界と実装の上界を同一視せず、実装上の安全な上界として $B_{\mathrm{impl}}=D_{\max}+\Delta T_c$ を別に定義できる。

本証明からは、デッドロック回避、実時間に対する遅れ、通信の到達期限、物理シミュレーションの数値精度、PDUの因果順序、多段構成の上界は結論しない。また、実験の時刻が外部シミュレータ自身の時計やPDUタイムスタンプである場合は、それと $T_i$ の対応を別途確認する必要がある。

コアの `get_asset_times()` は登録済みエントリの時刻を順次読み出す [S6]。全体の同時スナップショットを要求しないことと、各読み取りが健全であることは別の条件であり、後者はA3、A4に残る。実装全体を形式検証済みと表現しない。

### 7.1. 英文記述案（定理と証明の要約）

**Implementation-aware clock-skew bound for a single-level configuration.**
Consider one core and a fixed, nonempty set of synchronized assets. Let $T_c$ and $T_i$ denote their committed simulation times, respectively. The implementation advances the core by a fixed $\Delta T_c>0$ only if $T_c-\widetilde T_i<D_{\max}$ for every asset, whereas asset $i$ advances by a fixed $\Delta T_i>0$ only if $T_i+\Delta T_i\le\widetilde T_{c,i}$. Here $D_{\max}>0$ is the configured stopping threshold, not necessarily the maximum realized skew. Under assumptions A1–A5, all clocks start at zero, each component serializes its own updates, reads and arithmetic are sound, and no rollback, membership change, or parameter change occurs. Observations are valid committed times from the same execution and may be stale: $\widetilde T_i\le T_i$ and $\widetilde T_{c,i}\le T_c$ at update commitment. Only finitely many committed updates occur in a finite wall-clock interval.

For every wall-clock time $t$ in the execution,

$$
0\le T_c(t)-T_i(t)<D_{\max}+\Delta T_c,
\qquad
\max_iT_i(t)-\min_iT_i(t)<D_{\max}+\Delta T_c.
$$

*Proof.* The invariant holds initially. On a core update, $T_c^+-T_i\le T_c+\Delta T_c-\widetilde T_i<D_{\max}+\Delta T_c$, and increasing the core time preserves $T_i\le T_c$. On an asset update, $T_i^+\le\widetilde T_{c,i}\le T_c$, while increasing $T_i$ can only decrease its lag behind the core. Stuttering and observation updates leave committed times unchanged. Induction over committed updates establishes the invariant, which also holds between updates. Since all asset times lie at or behind the core, their spread is at most $T_c-\min_iT_i$. Every pairwise difference is bounded by this spread. Thus the current-time guard introduces less than one core time step of additional skew, without accumulation over the execution. This is a safety result; liveness, physical simulation accuracy, and correctness of the complete shared-memory implementation are not claimed.

## 8. 再現可能な補助検証

[verify_time_impl.py](experiment/verify_time_impl.py) は標準ライブラリだけを使う抽象モデルの検査であり、リポジトリルートから次で実行できる。

```bash
python3 src/math/experiment/verify_time_impl.py
```

比較演算の境界、正しい古い観測値による待機、第6.2節の初期状態からの到達例を確認する。さらに2アセットについて、$D_{\max},\Delta T_c\in\{1,\ldots,8\}$、$\Delta T_1,\Delta T_2\in\{1,\ldots,4\}$ の1,024構成を探索する。

探索状態は $g_i=T_c-T_i$ とし、コア更新ではすべての $g_i$ に $\Delta T_c$ を加え、アセット $i$ の更新では $g_i$ から $\Delta T_i$ を引く。判定がこの差だけに依存するため、共通の絶対時刻を取り除いても遷移を表せる。ステップ回数による打ち切りや、上界を超えた状態の除外は行わず、到達する各状態で不変条件を検査する。

この探索では最新値観測を使うが、正しい過去値を用いて許可される更新は、同じ真の状態で最新値を使った場合にも許可される。古い観測による追加の待機は時刻を変更しない。一般の遅延観測を含む保証自体は第4節の数学的証明による。

確認結果：1,024構成、合計51,485相対状態、96,685進行遷移で検査成功。これらは構成ごとの件数の合計である。**有限のパラメータ検査は一般定理の代わりではなく、C++バイナリの実行試験、共有メモリの検証、進行性の証明でもない。**

## 9. 固定参照ソース

- [S1] [コアの時刻更新：hako_time.cpp](https://github.com/toppers/hakoniwa-core-cpp/blob/b8f6b38789934f716c675c4fc6f0708682fe6975/src/hako/core/simulation/time/hako_time.cpp)
- [S2] [アセットの通知・進行判定・時刻確定：hako_asset_impl.cpp](https://github.com/hakoniwalab/hakoniwa-core-pro/blob/632fc885da2b81b2f6abf33c300fbedc74576f8b/sources/assets/callback/src/hako_asset_impl.cpp)
- [S3] [比較対象の理論：hakoniwa-time.md](https://github.com/hakoniwalab/hakoniwa-design-docs/blob/b3c0b611e449526aed7f22bb2950bbf62bb2083f/src/math/hakoniwa-time.md)
- [S4] [コアの時刻取得・更新・公開：hako_master_impl.cpp](https://github.com/toppers/hakoniwa-core-cpp/blob/b8f6b38789934f716c675c4fc6f0708682fe6975/src/hako/hako_master_impl.cpp)
- [S5] [コアの時刻型と時間単位：hako_types.hpp](https://github.com/toppers/hakoniwa-core-cpp/blob/b8f6b38789934f716c675c4fc6f0708682fe6975/src/include/types/hako_types.hpp)
- [S6] [登録済みアセット時刻の読み取り：hako_master_data.hpp](https://github.com/toppers/hakoniwa-core-cpp/blob/b8f6b38789934f716c675c4fc6f0708682fe6975/src/hako/data/hako_master_data.hpp)
