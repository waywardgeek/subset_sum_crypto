# A (possibly) new crypto system I just made up.

Note: you should never use an unproven crypto scheme like this to protect
sensitive data.  Use standard crypto instead from trustworthy libraries like
OpenSSL.

That said, inventing new crypto is fun.  This scheme is inspired from [Merkle
Puzzles](https://en.wikipedia.org/wiki/Merkle%27s_Puzzles).  If we want to
increase the security of the scheme to exponential advantage rather than
quadratic, then maybe Bob can pick a random subset of puzzles, rather than just
one, and only Alice can figure out which puzzles Bob chose.  The simplest way
to combine Bob's subset of chosen puzzles is just to add them.  It turns out
that determining Bob's chosen subset from the sum is hard, and in some cases
NP-complete, making this a good candidate for a public key cryptography scheme.
From there, I just used the most obvious way for Alice to determine Bob's
subset: encode 1 unique bit in each value so that I can read off the subset
from the binary representation of the sum.  To make it hard for Eve to see this
binary representation, I just blinded them with a random secret `r` and a random
secret prime modulus `p`.

## The Scheme

Alice starts by picking random secret 257-bit prime `p` in the range
[2^256..2^257], and then computes 118 values `v[i]`, for `i` in [0..117]:

```
    v[i] = (randrange(2^128) << 118) | (1 << i)
```

Remember that the << operator means shift the bits left.  `1 << i` is the value
`2^i`.  These values, if added together trivially expose which values were
added.  The chosen values are encoded in the lower bits.

The upper 138 bits start with 10 leading 0's, followed by 128 random bits.  The
lower 118 bits have only the `i`th bit set.  When any subset of the array `v`
are added together, the lower 118 bits encode which elements of `v` were
chosen, making the subset-sum problem trivial.  Just to make it easier, note
that all of these values added together are < `p`, so we can compute the same
sum mod `p`.

The main idea for this crypto system is for Alice to publish values based on
the array `v` as her public key, and for Bob to transmit to Alice a shared
118-bit shared secret encoded in a subset-sum.  Obviously, simply publishing
the array `v` is insecure, so we need to somehow obfuscate `v`'s values.

First, let's make the subset-sum problem more interesting, expanding the array
`v` from 118 elements to 384.  For `i` in [118..383], Alice computes:

```
    v[i] = randrange(2^128) << 118
```

These values have 0's for both the leading 10 bits and the lower 118 bits.
Note that a random subset-sum of `v` encodes only which of the values where
chosen in `v[0..117]`.  Also, there are very many solutions to the subset-sum
problem, more than 2^119 on average when the target `T` is a random subset-sum
of `v`.

To obscure the values of the array `v`, Alice picks a random 257-bit value
called `r` in [1..p-1], and computes a blinded array `b` for `i` in [0..383]:

```
    b[i] = r*v[i] mod p
```

For any `b[i]` > 2^256, Alice picks a new `v[i]` until all `b[i]` < 2^256.
This prevents the `b` values from leaking information about `p`.  The array `b`
is Alice's public key, which is 12KiB.  The values `r`, `p`, and array `v` are
Alice's private key.

For Bob to send Alice a 118-bit shared secret, he encodes it by summing the
corresponding values in `b[0..117]`, and obfuscates the sum by picking randomly
elements from `b[118..383]`.  Bob sends the resulting sum `s` to Alice.

Alice then computes

    sharedSecret = lower118Bits(s/r mod p)

## Security

As for the subset-sum problem, the best known general attacks where each
element has enough bits to make subset-sums usually unique run around `O(N/4)`,
where `N` is the number of elements in the set.  This algorithm makes it
strictly harder to find a correct subset of elements by shortening values,
giving the attacker less information.  This results in there being very many
solutions to the subset-sum problem.  There are only N*p possible sums, but
there are 2^N subsets.  This means that on average, each possible sum has
e^N/N*p collisions.  For N = 384, and p > 2^256, there are at least 2^119
solutions on average.  It is unlikely that using subset-sum will not help the
attacker, and the attacker is then left only with attacking the public key `b`
directly.

For any public key `b`, and any attacker-chosen `r'` and `p'` values, there exist
`v'` array values that satisfy `b[i] = r*v[i] mod p`, if we let the `v'` values
be any value in [1..p'-1].  Therefore, if v' had no constraints, the `b` array
would leak no information about `r` and `p`.  Any successful attack must take
advantage of the special structure of `v`.  So, for example, no solver for
Diophantine equations can help the attacker here, as there are 2 more unknowns
than equations, as each equation introduces a new `v[i]` unknown, and all
include the unknown `r` and `p` values.

However, for the example parameters, the attacker can solve for `r` and `p`
using any 4 `equations for b[i]`.  There is enough information to guess the
`v[i]`, `r`, and `p` values, when `k[i]` is the value needed to make:

```
    0 <= b[i] = r*v[i] - k[i]*p < p
```

The four simultaneous equations needed to attack our systems with our example
parameters can be written as:

```
    b[i1] = r*v[i1] - k[i1]*p < p
    b[i2] = r*v[i2] - k[i2]*p < p
    b[i3] = r*v[i3] - k[i3]*p < p
    b[i4] = r*v[i4] - k[i4]*p < p
```

The security of this scheme is based on the assumption that solving these
equations is hard for any subset of equations for `b`, when the only known
values are the `b` values.

Just how hard is this?  If, for example, it is only as hard as DLP, then then
we would need p to be 2047 bits, making this scheme too slow to be of any use.

The `k[i]` values are determined by the others, and are not random.  Each
equation introduces only 128 unknown bits, but gives us 256 bits of
constraint.  There are a total of 1024 bits known on the left, and 1024
unknown bits on the right.  Any solution to these equations can be verified by
testing on one more.

No matter how many of these equations we try to solve simultaneously, there are
always two more unknown variables than equations.  Otherwise, these would form
Diophantine equations by adding these together.  Instead, if we think of the
unknowns as individual Boolean variables, we have 1024 unknown variables, and
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

### Quantum resistant?

If classically secure, is this scheme quantum resistant?  I am unfortunately
not skilled in this area.  However, the attacker will most likely need to solve
the above simultaneous equations to derive `r`, `p`, and `the v` values.  It
would take experts in quantum cryptography to analyze the difficulty of this.

However, we do know that direct application of Grover's algorithm to equations
with 1024 unknown Boolean variables is far too slow.  Is there anything like
Shor's algorithm that can work here?

## Conclusion

Cryptography is hard.  In general, if you invent a public key algorithm, then:

1) It is not new: you've just re-invented something old.
2) It is also insecure.

I have not yet found this algorithm published anywhere.  Most likely this is
because it was too easy to break, and no one wound up with their name attached
to it.  That said, can you break it?  I have failed so far, making this
algorithm "Secure against Bill".  That's all I know for now.

Googling for subset-sum cryptography yields hundreds of papers, some which
claim to prove security of their public-key schemes based on the hardness of
subset-sum.  My guess is most likely Ralph Merkle invented and broke this
scheme in the 1980s.  However, most of the papers in this area:

1)  Use known prime fields, where `p` is public.
2) Rely on the hardness of the subset-sum problem.
3) Work in work in "low density" versions of the subset-sum problem where Bob's
   sum has a unique solution.

So, there is a non-negligible chance this scheme is new, mostly because I
propose a new untested problem for the security of the scheme that is simply
too hard for me to break, rather than relying on well-known hard problems that
have been studied for centuries, like subset-sum.
