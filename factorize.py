import logging
import time
import multiprocessing

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def factorize_sync(*numbers):
    start_time = time.time()
    factors = []
    for num in numbers:
        num_factors = []
        sqrt_num = int(num ** 0.5)
        for i in range(1, sqrt_num + 1):
            if num % i == 0:
                num_factors.append(i)
                if i != num // i:
                    num_factors.append(num // i)
        factors.append(sorted(num_factors))
    end_time = time.time()
    execution_time = end_time - start_time
    logger.debug("factorize_sync execution time: %s seconds", execution_time)
    return factors

def factorize_single(num):
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)
    return factors

def factorize_parallel(*numbers):
    start_time = time.time()
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(factorize_single, numbers)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.debug("factorize_parallel execution time: %s seconds", execution_time)
    return results

if __name__ == '__main__':

    a, b, c, d  = factorize_sync(128, 255, 99999, 10651060)
    a, b, c, d  = factorize_parallel(128, 255, 99999, 10651060)

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]