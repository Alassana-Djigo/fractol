def escape_iterations(z0: complex, c: complex, max_iter: int = 100) -> int:
    """
    Aplica repetidamente z = z*z + c, partindo de z0.
    Devolve quantos passos levou ate abs(z) ultrapassar 2
    (ou max_iter, se nunca ultrapassou)
    """
    z = z0
    for i in range(max_iter):
        z = z * z + c
        if abs(z) >= 2:
            return i + 1
    return max_iter
