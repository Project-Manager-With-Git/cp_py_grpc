import sys
from typing import Sequence
from .serv import Serv


def main(argv: Sequence[str]) -> None:
    serv_node = Serv(name="echo_serv")
    serv_node(argv)


if __name__ == "__main__":
    main(sys.argv[1:])
