import multiprocessing
import time

def square(n):
    """計算平方值"""
    print(f"Processing {n} in process {multiprocessing.current_process().name}")
    time.sleep(1)  # 模擬較長的計算時間
    return n * n

if __name__ == "__main__":
    # 在 Jupyter Notebook 內的 multiprocessing 必須放在 __main__ 保護下
    with multiprocessing.Pool(processes=4) as pool:
        numbers = [1, 2, 3, 4, 5]
        results = pool.map(square, numbers)

    print("Squared results:", results)