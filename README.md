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
broken if an attacker finds `r` and `p`.  Without knowing `r` and `p`, can
the attacker guess the lower bits of a subset-sum of the `v` values?  The
hypothesis for this crypto system is that this problem is hard.

For Bob to send Alice a 128-bit shared secret, he encodes it by summing the
corresponding values in `b[0..127]`, and obfuscates the sum by picking randomly
elements from `b[128..511]`.  Bob sends the resulting sum `s` to Alice.

Alice then computes

    sharedSecret = lower128Bits(s/r mod p)

This can be seen as valid noting that `s/r mod p = sum(v[i])`, where the `i`
values were selected by Bob to encode `sharedSecret`.  This sum is < `p`, so
the low 128 bits should represent Bob's secret key.

## Security

Is this scheme quantum resistant?  I am unfortunately not skilled in this area,
but I will hypothesize that it might be.  Someone else would need to determine
this.

With very many solutions to the subset-sum problem, even a quantum computing
solution to subset-sum does not break the scheme directly.  The attacker would
need to find not just a subset with the correct sum, but one that also includes
the correct set of `b[0..127]`.  A successful attack is more likely to derive
`r` and `p` directly from the `b` array, without relying on Bob's subset sum.
The linear nature of the equations for the `b` array values may result in
efficient quantum attacks, or even efficient classical computing attacks.

My intuition for this problem being hard is that without knowing `p`, the
attacker does not know the group, and linear analysis won't work on an unknown
group.

As for the subset-sum problem, the best known general attacks where each
element is more than 512 bits is around `O(n/4)`, where `n` is the number of
elements in the set.  This algorithm makes it strictly harder to find a correct
subset of elements by shortening values, giving the attacker less information.
