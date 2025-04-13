from random import randrange
import sympy

def getRandomPrime(minVal, maxVal):
  while True:
    num = randrange(minVal, maxVal)
    if sympy.isprime(num):
      return num

minRange = 1 << 256
maxRange = 1 << 257
p = getRandomPrime(minRange, maxRange)
r = randrange(1 << 256)
print("p =", p)
print("r =", r)

def findVAndB(i):
    while True:
        if i < 118:
            v = (randrange(1 << 128) << 118) | (1 << i)
        else:
            v = randrange(1 << 128) << 118
        b = r*v % p
        if b < (1 << 256):
            return (v, b)

v = []
b = []
for i in range(384):
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
aliceSecret = ((1 << 118) - 1) & (((s % p) * rInv) % p)
print("aliceSecret =", aliceSecret)
if aliceSecret == bobSecret:
      print("Passed")
else:
      print("Failed")
