# A new crypto system I just made up.  Is it secure?  Quantum resistant?

Note: you should never use an unproven crypto scheme like this to protect
sensitive data.  Use standard crypto instead from trustworthy libraries like
OpenSSL instead.

That said, inventing new crypto is fun.  Here's my latest brain-fart.

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
`v` from 118 elements to 384.  For `i` in [118..383], Alice computes:

```
    v[i] = randrange(2^128) << 118
```

These values have 0's for both the leading 10 bits and the lower 118 bits.
Note that a random subset-sum of `v` encodes only which of the values where
chosen in `v[0..117]`.  Also, there are very many solutions to the subset-sum
problem, more than 2^120 when the target `T` is a random subset-sum of `v`.

To obscure the values of the array `v`, Alice picks a random 257-bit value
called `r` in [1..p-1], and computes a blinded array `b` for `i` in [0..383]:

```
    b[i] = r*v[i] mod p
```

For any `b[i]` > 2^256, Alice picks a new `v[i]` until all `b[i]` < 2^256.
This prevents the `b` values from leaking information about `p`.  The array `b`
is Alice's public key, which is 16KiB.  The values `r`, `p`, and array `v` are
Alice's private key.

For Bob to send Alice a 118-bit shared secret, he encodes it by summing the
corresponding values in `b[0..117]`, and obfuscates the sum by picking randomly
elements from `b[118..383]`.  Bob sends the resulting sum `s` to Alice.

Alice then computes

    sharedSecret = lower118Bits(s/r mod p)

This can be seen as valid noting that `s/r mod p = sum(v[i])`, where the `i`
values were selected by Bob to encode `sharedSecret`.  This sum is < `p`, so
the low 118 bits should represent Bob's secret key.

## Security

As for the subset-sum problem, the best known general attacks where each
element is more than 512 bits is around `O(n/4)`, where `n` is the number of
elements in the set.  This algorithm makes it strictly harder to find a correct
subset of elements by shortening values, giving the attacker less information.
This results in there being very many solutions to the subset-sum problem.
There are only N*p possible sums, but there are 2^N subsets.  This means that
on average, each possible sum has 2^N/N*p collisions.  For N = 384, and p >
2^128, there are at least 2^118 solutions on average.  Using subset-sum will
not help the attacker.

For any public key `b`, and any attacker-chosen `r'` and `p'` values, there exist
`v'` array values that satisfy `b[i] = r*v[i] mod p`, if we let the `v'` values
be any value in [1..p'-1].  Therefore, if v' had no constraints, the `b` array
would leak no information about `r` and `p`.  Any successful attack must
take advantage of the special structure of `v`.

If the attacker takes any 4 b[i] values where i > secretBits (118 in the
example), there is enouigh information to guess the v[i], k[i], r, and p values, where `k[i]` is the value needed to make:

```
    0 <=r*v[i] - k[i]*p < p
```

The four simulgtaneous equations can be written as:

```
    b[i1] = r*v[i1] - k[i1]*p
    b[i2] = r*v[i2] - k[i2]*p
    b[i3] = r*v[i3] - k[i3]*p
    b[i4] = r*v[i4] - k[i4]*p
```

The main assumption for the security of this system is that solving these
equations is hard for any subset of `b`.

The `k[i]` values are determined by the others, and are not random.  Each
equation introduces only 128 unknown bits, but gives us 256 bits of
const4raint.  There are a total of 1024 bits known on the left, and 1024
unknown bits on the right.  Any solution to these equations can be verified by
testing on one more.

No matter how many of these equations we try to solve simultaneously, there are
always two more unknown variables than equations.  Otherwise, these would form
Diophantine equations by adding these together.  Instead, if we think of the
unknowns as individual boolean variables, we have 1024 unknonw variables, and
1024 equations constraining them, if we write the equation for each bit of the
`b` values.

It is possible to eliminate both `r` and `v[i]` from the set of equations by
taking them mod 2^n, where n is the number of trailing 0's in `v` values, in
our example 118.

```
    b[i] = r*v[i] - k[i]*p
    b[i] mod 2^n = -k[i]*p mod 2^n
```

For every possible `p mod 2^n`, there is a possible `k[i] mod 2^n` s.t `b[i] =
k[i]*p mod 2^n`.  Therefore, the attacker does not learn anything about `p mod
2^n` from these equations alone.

## Quantum resistant?

If classically secure, is this scheme quantum resistant?  I am unfortunately
not skilled in this area.  However, the attacker will most likely need to solve
the above simultaneous equations to derive `r`, `p`, and `the v` values.  It
would take experts in quantum crytography to analyze the difficulty of this.

However, we do know that direct application of Grover's algorithm to equations
with 1024 unknown boolean variables is far too slow.  Is there anything like
Shor's algorithm that can work here?
