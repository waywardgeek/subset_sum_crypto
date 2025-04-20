# A (possibly) new crypto system I just made up.

Note: you should never use an unproven crypto scheme like this to protect
sensitive data.  Use standard crypto instead from trustworthy libraries like
OpenSSL.

#* Broken in 1981
It turns out this scheme is nearly the same as Merkle's original knapsack based
crypto, which was broken by Shamir in 1981.  Diffie, Hellman, and Merkle
shortly after the knapsack sysstem, invented the Diffie-Hellman system, which
should probably also include Merkle.  I'll leave this insuecure protocol
description here.

## Motivation
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
[2^384..2^385], and then computes 118 values `v_i`, for `i` in [0..117]:

```
    v_i = randrange(2^256) | (1 << (i + 266))
```

Remember that the << operator means shift the bits left.  `1 << i` is the value
`2^i`.

The format of v is 118 bits with only 1 bit set, followed by 10 0's, followed
by 256 random bits.  The upper 118 bits have only 1 bit set.  When any subset
of the array `v` are added together, the upper 118 bits encode which elements
of `v` were chosen, making the subset-sum problem trivial.  Just to make it
easier, note that all of these values added together are < `p`, so we can
compute the same sum mod `p`.  The 10 0 bits from position 256 to 265 ensure
that subset sums do not have the lower 256 bits impacting the upper 118 bits.

The main idea for this crypto system is for Alice to publish values based on
the array `v` as her public key, and for Bob to transmit to Alice a shared
118-bit shared secret encoded in a subset-sum.  Obviously, simply publishing
the array `v` is insecure, so we need to somehow obfuscate `v`'s values.

First, let's make the subset-sum problem more interesting, expanding the array
`v` from 118 elements to 512.  For `i` in [118..511], Alice computes:

```
    v_i = randrange(2^256)
```

These values have 0's for the leading 128 bits.  Note that a random subset-sum
of `v` encodes only which of the values where chosen in `v[0..117]`.  Also,
there are very many solutions to the subset-sum problem, more than 2^119 on
average when the target `T` is a random subset-sum of `v`.

To obscure the values of the array `v`, Alice picks a random 385-bit value
called `r` in [1..p-1], and computes a blinded array `b` for `i` in [0..511]:

```
    b_i = r*v_i mod p
```

For any `b_i` >= 2^384, Alice picks a new `v_i` randomly as before, until all
`b_i` < 2^384.  This prevents the `b` values from leaking information about
`p`.  The array `b` is Alice's public key, which is 24KiB.  The values `r`,
`p`, and array `v` are Alice's private key.

For Bob to send Alice a 118-bit shared secret, he encodes it by summing the
corresponding values in `b[0..117]`, and obfuscates the sum by picking randomly
elements from `b[118..511]`.  Bob sends the resulting sum `s` to Alice.

Alice then computes

    sharedSecret = (s/r mod p) >> 266

Note that the >> operator shifts right, dropping the lower bits.

## Security

As for the subset-sum problem, the best known general attacks where each
element has enough bits to make subset-sums usually unique run around `O(N/4)`,
where `N` is the number of elements in the set.  This algorithm makes it
strictly harder to find a correct subset of elements by shortening values,
giving the attacker less information.  This results in there being very many
solutions to the subset-sum problem.  There are only N*p possible sums, but
there are 2^N subsets.  This means that on average, each possible sum has
2^N/(N*p) collisions.  For N = 512, and p > 2^384, there are at least 2^119
solutions on average.  It is unlikely that using subset-sum will not help the
attacker, and the attacker is then left only with attacking the public key `b`
directly.

For any public key `b`, and any attacker-chosen `r'` and `p'` values, there exist
`v'` array values that satisfy `b_i = r*v_i mod p`, if we let the `v'` values
be any value in [1..p'-1].  Therefore, if v' had no constraints, the `b` array
would leak no information about `r` and `p`.  Any successful attack must take
advantage of the special structure of `v`.  So, for example, no solver for
Diophantine equations can help the attacker here, as there are 2 more unknowns
than equations, as each equation introduces a new `v_i` unknown, and all
include the unknown `r` and `p` values.

However, for the example parameters, the attacker can solve for `r` and `p`
using any 6 `equations for b_i`.  There is enough information to guess the
`v_i`, `r`, and `p` values, when `k_i` is the value needed to make:

```
    0 <= b_i = r*v_i - k_i*p < p
```

The 6 simultaneous equations needed to attack our systems with our example
parameters can be written as:

```
    b_i1 = r*v_i1 mod p
    b_i2 = r*v_i2 mod p
    b_i3 = r*v_i3 mod p
    b_i4 = r*v_i4 mod p
    b_i5 = r*v_i5 mod p
    b_i6 = r*v_i6 mod p
```

Each equation introduces 384 Boolean constraints if we consider the `b` values
as 384 Boolean equations.  Each `v` value introduces 256 unknown Boolean
values.  r has 385 unknown bits, and p has 383, since we know the leading and
trailing bits of p are 1.  6 equations gives us 2 more Boolean constraints than
we have unknown Boolean variables.

The security of this scheme is based on the assumption that solving these
equations is hard for any subset of equations for `b`, when the only public
values are the `b` values, and both  `r` and `p` are secret.

It is easy to see that for randomly chosen `v` values in [1..p-1], the scheme
has information theoretic security, meaning the attacker cannot learn `r` or
`p` regardless of their computational power.  There is always a value of `v_i`
which satisfies the equation for `b_i`, regardless of the values of `r` and
prime `p`.

To actually transmit information from Bob to Alice, Alice must pick `v`
non-randomly, and the attacker must take advantage of how Alice picked `v` to
have any chance of attacking Alice's public key.

No matter how many of these equations we try to solve simultaneously, there are
always two more unknown variables than equations.  Otherwise, these would form
a Diophantine system of equations.  Instead, if we think of the unknowns as
individual Boolean variables, in our example, we have 385 unknown variables for
`r`, 383 for `p`, and 6\*256 for `v`.  The constraints have 6*384 bits.  so a
solution may be unique, and if not, solutions can be tested against the other
equations for `b`.

It is possible to eliminate `r` and `v_i` from the set of equations by taking
them mod 2^n, where n is the number of leading 0's in `v` values, in our
example 128.

```
    v' = v*2^n, where n == 128 in our example.
    r' = r/2^n mod p
```

Then we can find:

```
    b_i = r'*v'_i - k_i*p < p
    b_i = -k_i*p mod 2^n
```

For every possible `p mod 2^n`, there is a possible `k_i mod 2^n` s.t `b_i =
k_i*p mod 2^n`.  Therefore, the attacker does not learn anything about `p` or
`k` directly from these equations alone.

Gemini 2.5 gave the following insight.  For any `i, j > 118`, `v_i` and `v_j`
are small, only 256 bits.  We have:

```
    b_i = r*v_i - k_i*p
    b_j = r*v_j - k_j*p
```
Now multiply the first by `v_j` and the second by `v_i`:

```
    b_i*v_j = r*v_i*v_j - k_i*p*v_j
    b_j*v_i = r*v_j*v_i - k_j*p*v_i
```

Subtracting gives:


```
    b_i*v_j - b_j*v_i = p*(k_j*v_i - k_i*v_j)
```

Which means the left side is 0 mod p.  For 6 values of `b_i`, we get 36
equations of the form:

```
    b_i*v_j - b_j*v_i = 0 mod p
```

Does his help mount a latice-based attack that can reveal `p`?

This is where my math skills fail me.

Just as a sanity check, I verified that the `b` values output by this scheme
pass the dieharder tests.  "Passing" nowadays means getting roughly the
expected number o "weak" results, and it fell in between the results of two
runs on the output of /dev/urandom.  It would be concerning if the public keys
did not pass basic tests for randomness.

### Quantum resistant?

If classically secure, is this scheme quantum resistant?  I am unfortunately
not skilled in this area.  However, the attacker will most likely need to solve
the above simultaneous equations to derive `r`, `p`, and `the v` values.  It
would take experts in quantum cryptography to analyze the difficulty of this.

However, we do know that direct application of Grover's algorithm to find `r`,
`p`, and `v_i` values would be too slow.

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

So, there is a non-negligible chance this scheme is new, probably because I
propose a new untested problem as the basis for security.  We usually prefer
famous problems that have been studied for centuries.

Because the keys are so large, there is no reason to investigate this scheme
further, other than for the possibility that it may be quantum-resistant.
