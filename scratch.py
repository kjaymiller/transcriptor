def fizz_buzz(n: int):
    n_value = ''

    if not n % 3:
        n_value += 'Fizz'

    if not n % 5:
        n_value += 'Buzz'

    if not n_value:
        n_value = n

    return n_value


for n in range(100):
    print(fizz_buzz(n))
