from random import randrange
import sympy

def getRandomPrime(minVal, maxVal):
    num = randrange(minVal, maxVal)
    while not sympy.isprime(num):
        num += 1
    return num

minRange = 1 << 384
maxRange = 1 << 385
p = getRandomPrime(minRange, maxRange)
r = randrange(1 << 384)
print("p =", p)
print("r =", r)

def findVAndB(i):
    while True:
        if i < 118:
            v = randrange(1 << 256) | (1 << (i + 266))
        else:
            v = randrange(1 << 256)
        b = r*v % p
        if b < (1 << 384):
            return (v, b)

v = []
b = []
for i in range(512):
    pair = findVAndB(i)
    v.append(pair[0])
    b.append(pair[1])

bobSecret = randrange(1 << 118)
print("Bob's secret =", bobSecret)
s = 0
for i in range(118):
    if (bobSecret >> i) & 1 == 1:
        s += b[i]
for i in range(118, 384):
    if randrange(2) == 1:
        s += b[i]
print("Bob returns", s)

# This computes the modular inverse of r mod p.
rInv = pow(r, -1, p)
print("rInv =", rInv)
aliceSecret = (((s % p) * rInv) % p) >> 266
print("aliceSecret =", aliceSecret)
if aliceSecret == bobSecret:
      print("Passed")
else:
      print("Failed")
