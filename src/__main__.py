import warnings

from local_module import conductor

warnings.simplefilter("ignore")


def main():
    conductor.run()


if __name__ == "__main__":
    main()
