def get_nth_fibonacci_number(n):
    matrix = __matrix_fib_number(n)
    return matrix[0][0]+matrix[0][1]

def __c(mt1,mt2,il,ic):
    return mt1[il][0]*mt2[0][ic] + mt1[il][1]*mt2[ic][1]

def __matrix2x2_multiplication(matrix_one, matrix_two):
    c00 = __c(matrix_one,matrix_two,0,0)
    c01 = __c(matrix_one,matrix_two,0,1)
    c10 = __c(matrix_one,matrix_two,1,0)
    c11 = __c(matrix_one,matrix_two,1,1)
    return [ [ c00 , c01 ] , [ c10 , c11 ] ]

def __matrix_fib_number(n):
    if n == 1 : return [[0,1],[1,1]]
    next_n = int(n/2)
    result = __matrix_fib_number(next_n)
    result = __matrix2x2_multiplication(result,result)
    if n % 2 == 1:
        result = __matrix2x2_multiplication(result,__matrix_fib_number(1))
    return result
