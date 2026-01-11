def caching_fibonacci():
    cache = {}

    def fibonacci(n):
        if not isinstance(n, int):
            raise TypeError("n must be an integer")

        if n <= 0:
            return 0
        if n == 1:
            return 1

        if n in cache:
            return cache[n]

        cache[n] = fibonacci(n - 1) + fibonacci(n - 2)
        return cache[n]

    return fibonacci

fib = caching_fibonacci()

print(f"F(10) = {fib(10)}")
print(f"F(11) = {fib(11)}")
print(f"F(12) = {fib(12)}")
print(f"F(13) = {fib(13)}")
print(f"F(14) = {fib(14)}")
print(f"F(15) = {fib(15)}")
print(f"F(16) = {fib(16)}")
print(f"F(17) = {fib(17)}")
print(f"F(18) = {fib(18)}")
print(f"F(19) = {fib(19)}")
print(f"F(20) = {fib(20)}")
print(f"F(50) = {fib(50)}")

