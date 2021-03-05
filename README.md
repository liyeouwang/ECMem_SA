The first four lines contain four integers $I$, $J$, $K$, and $T_{max}$, indicating the number of vehicles, the number of servers, the number of services, and the upper bound of time (all time $\in [0, T_{max})$).

The next $J$ lines represents $T_{j, k}$. Each of these lines contains $K$ non-negative integers.

The next $J$ lines represents $C_{j, k}$. Each of these lines contains $K$ non-negative integers.

The following $J$ groups of $J$ lines represents $T^{\vee}{j,j',k}$ (i.e. there are $J \times J$ lines). Each of these lines contains $K$ non-negative integers. The $k$-th integer in the $j'$-th line of the $j$-th group indicates the transmission time of $\sigma_k$ from $\epsilon_j$ to $\epsilon{j'}$.

The next $I$ lines represents $D_{i, k}$. Each of these lines contains $K$ integers. The $k$-th integer of the $i$-th line is a non-negative integer if $\nu_i$ DOES demand $\sigma_k$, otherwise it will be -1.

The next $I$ lines represents $F_{i,k}$. Each of these lines contains $K$ non-negative integers.

The following $I$ groups of $J$ lines represents $R_{i, j, t}$ (i.e. there are $I \times J$ lines). Each of these lines contains $T_{max}$ integers that is either $0$ or $1$. The $t$-th integer of in the $j$-th line of the $i$-th group indicates if $\nu_i$ is in the communication of $\epsilon_j$ at time $t$.

The next line represents $M_{k}$. It contains $K$ non-negative integers.

The next line represents $\overline{M}_{j}$. It contains $J$ non-negative integers.