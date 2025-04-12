# A new crypto system I just made up.  Is it secure?  Quantum resistant?

Alice starts by picking random secret 256-bit prime `p` in the range
[2^256..2^257], and then computes 128 values `v[i]`, for `i` in [0..127]:

```
    v[i] = (randrange(2^118) << 128) | (1 << i)
```

Remember that the << operator means shift the bits left.  `1 << i` is the value
`2^i`.

The upper 128 bits start with 10 leading 0's, followed by 118 random bits.  The
lower 128 bits have only the `i`th bit set.  When any subset of the array `v`
are added together, the lower 128 bits encode which elements of `v` were
chosen, making the subset-sum problem trivial.  Just to make it easier, note
that all of these values added together are < `p`, so we can compute the same
sum mod `p`.

The main idea for this crypto system is for Alice to publish values based on
the array `v` as her public key, and for Bob to transmit to Alice a shared
128-bit key encoded in a subset-sum.  Obviously, simply publishing the array
`v` is insecure, so we need to somehow obfuscate `v`'s values.

First, let's make the subset-sum problem more interesting, expanding the array
`v` from 128 elements to 512.  For `i` in [128..511], Alice computes:

```
    v[i] = randrange(2^118) << 128
```

These values have 0's for both the leading 10 bits and the lower 128 bits.
Note that a random subset-sum of `v` encodes only which of the values where
chosen in `v[0..127]`.  Also, there are very many solutions to the subset-sum
problem, around 2^256 when the target `T` is a random subset-sum of `v`.

To obscure the values of the array `v`, Alice picks a random 256-bit value
called `r` in [1..p-1], and computes a blinded array `b` for `i` in [0..511]:

```
    b[i] = r*v[i] mod p
```

For any `b[i]` > 2^256, Alice picks a new `v[i]` until all `b[i]` < 2^256.
This prevents the `b` values from leaking information about `p`.  The array `b`
is Alice's public key, which is 16KiB.  The values `r`, `p`, and array `v` are
Alice's private key.

Is this blinding cryptographically secure?  This crypto system is completely
broken if an attacker finds ``r`` and ``p`.  Without knowing `r` and `p`, can
the attacker guess the lower bits of a subset-sum of the `v` values?  The
hypothesis for this crypto system is that this problem is hard.

For Bob to send Alice a 128-bit shared secret, he encodes it by summing the
corresponding values in `b[0..127]`, and obfuscates the sum by picking randomly
elements from `b[128..511]`.  Bob sends the resulting sum `s` to Alice.

Alice then computes

    sharedSecret = lower128Bits(s/r mod p)

This can be seen as valid noting that `s/r mod p = sum(v[i])`, where the `i`
values were selected by Bob to encode `sharedSecret`.  This sum is < `p`, so
the low 128 bits shoulud represent Bob's secret key.

Is this scheme quantum resistant?  I am unfortunately not skilled in this area,
but I will hypothesize that it might be.  Someone else would need to determine
this.

However, assuming BQP != NP: The subsest-sum problem is NP-hard, so unless a
special version of a quantum algorithm can be found to solve this specific
case, I think the best we can do is Grover's algorithm.  With Grovers
algorithm, we want to find r and p that simultaneouisly solves a few of the
`b[i] = r*v[i] mod p` constraints.  Both `r` and `p` are at least 256 bits
long, so Grovers algorithm would take 2^256 time.
