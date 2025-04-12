from random import randrange
import sympy

def get_random_prime(min_val, max_val):
  while True:
    num = randrange(min_val, max_val)
    if sympy.isprime(num):
      return num

min_range = 1 << 256
max_range = 1 << 257
p = get_random_prime(min_range, max_range)
r = randrange(1 << 256)
print(f"p = {p}")
print(f"r = {r}")

def findVAndB(i):
    if i < 128:
        v = (randrange(1 << 118) << 128) | (1 << i)
    else:
        v = randrange(1 << 118) << 128
    b = r*v % p
    if b < (1 << 256):
        return (v, b)
    return findVAndB(i)

v = []
b = []
for i in range(512):
    pair = findVAndB(i)
    v.append(pair[0])
    b.append(pair[1])

bobSecret = randrange(1 << 128)
print("Bob's secret =", bobSecret)
s = 0
for i in range(128):
    if (bobSecret >> i) & 1 == 1:
        s += b[i]
for i in range(128, 512):
    if randrange(2) == 1:
        s += b[i]
print("Bob returns", s)

rInv = pow(r, -1, p)
print("rInv =", rInv)
aliceSecret = ((1 << 128) - 1) & (((s % p) * rInv) % p)
print("aliceSecret =", aliceSecret)
if aliceSecret == bobSecret:
      print("Passed")
else:
      print("Failed")
