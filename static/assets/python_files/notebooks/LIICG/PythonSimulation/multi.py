
from concurrent.futures import ProcessPoolExecutor, as_completed
from time import sleep, perf_counter
import asyncio

async def task(message):


    print(f"Started: {message}")
    sleep(2)
    print(message)
    asyncio.sleep(0.01)

async def main():
    # with ProcessPoolExecutor() as executor:
    #     futures = [executor.submit(task, *("Completed", "Completed1")) for _ in range(4)]
    
    # results = [f.result() for f in as_completed(futures)]

    await asyncio.wait([task(f"Completed_{_}") for _ in range(5)])

    # print(results)


if __name__ == '__main__':

    t0 = perf_counter()
    # main()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(f"Time taken: {perf_counter()-t0}s")