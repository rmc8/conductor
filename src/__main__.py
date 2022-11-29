import shutil
import asyncio
import warnings

from local_module import conductor, util

warnings.simplefilter("ignore")


async def main():
    try:
        util.mkdir("./output/")
        util.mkdir("./dict/")
        util.mkdir("./log/")
        await conductor.run()
    finally:
        shutil.rmtree("./output/")


if __name__ == "__main__":
    asyncio.run(main())
