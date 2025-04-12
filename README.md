# A new crypto system I just made up.  Is it secure?  Quantum resistant?

Note: you should never use an unproven crypto scheme like this to protect
sensitive data.  Use standard crypto instead from trustworthy libraries like
OpenSSL instead.

Alice starts by picking random secret 256-bit prime `p` in the range
[2^256..2^257], and then computes 118 values `v[i]`, for `i` in [0..117]:

```
    v[i] = (randrange(2^128) << 118) | (1 << i)
```

Remember that the << operator means shift the bits left.  `1 << i` is the value
`2^i`.

The upper 138 bits start with 10 leading 0's, followed by 128 random bits.  The
lower 118 bits have only the `i`th bit set.  When any subset of the array `v`
are added together, the lower 118 bits encode which elements of `v` were
chosen, making the subset-sum problem trivial.  Just to make it easier, note
that all of these values added together are < `p`, so we can compute the same
sum mod `p`.

The main idea for this crypto system is for Alice to publish values based on
the array `v` as her public key, and for Bob to transmit to Alice a shared
118-bit key encoded in a subset-sum.  Obviously, simply publishing the array
`v` is insecure, so we need to somehow obfuscate `v`'s values.

First, let's make the subset-sum problem more interesting, expanding the array
`v` from 118 elements to 512.  For `i` in [118..511], Alice computes:

```
    v[i] = randrange(2^128) << 118
```

These values have 0's for both the leading 10 bits and the lower 118 bits.
Note that a random subset-sum of `v` encodes only which of the values where
chosen in `v[0..117]`.  Also, there are very many solutions to the subset-sum
problem, around 2^256 when the target `T` is a random subset-sum of `v`.

To obscure the values of the array `v`, Alice picks a random 257-bit value
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

    sharedSecret = lower118Bits(s/r mod p)

This can be seen as valid noting that `s/r mod p = sum(v[i])`, where the `i`
values were selected by Bob to encode `sharedSecret`.  This sum is < `p`, so
the low 118 bits should represent Bob's secret key.

## Security

For any public key `b`, and any chosen `r` and `p` values, there exist `v`
array values that satisfy `b[i] = r*v[i] mod p`, if we let the `v` values be
any value in [0..p-1].  Therefore, if v had no constraints, the `b` array would
leak no information about `r` and `p`.

However, v has significant structure.  It is, for example possible to eliminate both `r` and `v[i]` from the set of equations with some tricks:

```
    r*v[i] mod p = (r/(2^118))*(2^118*v[i] mod p
```

What this dues is let us define `r' = r/(2^118)`, and `v'[i] = v[i]/2^118.
Note that the upper 118 bits of v'[i] are 0 when i > 118.  For i in [116..511]:

```
    b[i] = r'*v'[i] mod p = r'*v'[i] + k[i]*p
    b[i] mod 2^118 = r'*v'[i] + k[i]*p mod 2^118
    b[i] mod 2^118 = k[i]*p mod 2^118
```

Here, `k[i]\*p` is a negative value that reduces `r'\*v'[i] + k[i]\*p` to be in
the range [0..p-1].  For every possible `p mod 2^118`, there is a possible
`k[i] mod 2^118` s.t `b[i] = k[i]\*p mod 2^118`.  Therefore, the attacker does
not directly learn anything about the lower 118 bits of `p`.

Are there more sophisticated attacks that leak some or all of `p`?  Maybe.

If classically secure, is this scheme quantum resistant?  I am unfortunately
not skilled in this area, but I will hypothesize that it might be.  Someone
else would need to determine this.  However, direct attacks on the subset-sum
problem look unlikely, even for quantum computers.  There are very many
solutions to the subset-sum, around 2^256, so having many valid solutions does
not lead to guessing the shared secret efficiently.  A more likely successful
quantum algorithm would derive `r` and `p` directly from the `b[i]` values.

My likely flawed intuition for this problem being quantum resistant is that
without knowing `p`, so the attacker doesn't even know what the group members
are, complicating attacks.  However, a good mathematician can probably break
this scheme.

As for the subset-sum problem, the best known general attacks where each
element is more than 512 bits is around `O(n/4)`, where `n` is the number of
elements in the set.  This algorithm makes it strictly harder to find a correct
subset of elements by shortening values, giving the attacker less information.

Any successful attack will rely on the chosen structure of the `v` values.  For
i > 128, we have:

```
    b[i] = r*<10 0's><128 random bits><118 0s> mod p
or:
    b[i] = r*<10 0's><128 random bits><118 0s> + k*p
```

Would a lattice-based attack break this?  If not, what about quantum algorithms?
I suspect this is where the weakness in the algorithm lies.
