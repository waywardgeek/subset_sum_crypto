# A (possibly) new crypto system I just made up.

Note: you should never use an unproven crypto scheme like this to protect
sensitive data.  Use standard crypto instead from trustworthy libraries like
OpenSSL.

## Broken in 1981
It turns out this scheme is nearly the same as Merkle's original knapsack based
crypto, which was broken by Shamir in 1981.  Diffie, Hellman, and Merkle
shortly after the knapsack sysstem, invented the Diffie-Hellman system, which
should probably also include Merkle.  I'll leave this insuecure protocol
description here.

Even variants I also came up with, such as the multiply-iterated Merkle-Hellman
system have been broken.

As usual, when you come up with a "new" public key crypto scheme, it is:

1) Actually very old.
2) Already broken.

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

I'm sure this is how Merkle came up with almost the exact same scheme in the
late 1970s...

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
