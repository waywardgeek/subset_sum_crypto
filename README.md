Alice picks 128 values, for i in [0..127]:

    v[i] = (randRange(2^118) << 128) | (1 << i)

That is 118 random upper bits, but only one unique bit set in the lower bits.
Alice also picks

    v[128 .. 512] = randRange(2^118) << 128

where all 128 lower bits are 0.  All the values of v added together are still < p.

Alice then picks random 256-bit r and prime p in the range of 2^256 to 2^257,
and cmoputes

    b[i] = r\*v[i] mod p

For any b[i] > 2^256, Alice picks a new b[i] until all b[i] < 2^256.  The set
of b[i] is Alice's public key, which is 16KiB.  The values r, v[i], and p are
Alice's secret key.

Note that Bob knows that b[0] to b[127] represent bits of the shared key.  Bob
picks a random 128-bit key, and sums the corresponding b[i] together where i <
128.  Bob then further obfuscates the sumb by adding a random subset of the
remaining b[128..512].  Bob sends the resulting sum s to Alice.

Alice then computes

    key = lower128Bits((s mod p) / r mod p)

This can be seen as valid noting that s/r mod p = sum(v[i]), where i was
selected by Bob.  This sum < p, so the low 128 bits shoulud represent Bob's
secret key.

Subset-sum problem can be solved in ~O(2^(n/4)), where n is the number of
integers being summed.  However, we have ~2^256 solutions, so maybe one can be
found quickly.  However, only 1 in 2^128 solutions is valid, in that it gives
Bob's secret key.

The other attack is to try to compute p and r from the 512 values.  Brute force
guessing p clearly won't be fast enough.

Trying to guess r from the 512 values without knowing p:

    b[0] = r\*v[0] + k[0]p -- 2 256-bit unknowns and 1 128-bit unknown (k can be dreived)
    b[1] = r\*v[1] + k[1]p -- An additional 128 bit unknown.
    ...

Hypothesis: finding r and p from these 512 equations is hard.  Intuition is
that without knowing p, this is a group of unknown order, and the attacker
loses the ability to find modular inverses.

Quantum resistance, assuming BQP != NP: The subsest-sum problem is NP-hard, so
unless a special version of a quantum algorithm can be found to solve this
specific case, I think the best we can do is Grover's algorithm.  With Grovers
algorithm, we want to find r and p that simultaneouisly solves a few of the
B[i] = r\*v[i] mod p constraints.  Both r and p are 256 bits long, so Grovers
algorithm would take 2^256 time.

There is a year-old paper that claims BQP == NP, which would be a tremendous
result if true.  In that case, there is no such thing as post-quantum crypto.
However, it hasn't been talked about much, most likely meaning it is wrong.
