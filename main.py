import sys
from typing import Dict, Type

from challenges import Challenge


def _handle_pick(pick: str, mapping: Dict[int, Type[Challenge]]) -> int:
    maybe_err_msg = f"invalid_pick: {pick}"
    try:
        pick = int(pick)
    except ValueError:
        print(maybe_err_msg)
        sys.exit(-1)

    if pick not in mapping.keys():
        print(maybe_err_msg)
        sys.exit(-1)

    return pick


def prompt_challenge_selector() -> Type[Challenge]:
    mapping = {i: c for i, c in enumerate(Challenge.__subclasses__())}
    print("pick a challenge:")
    for idx, challenge in mapping.items():
        print(f"{idx: >3}: {challenge.__name__}")

    pick = input("> ")
    pick = _handle_pick(pick, mapping)

    return mapping[pick]


if __name__ == "__main__":
    picked_challenge = prompt_challenge_selector()
    picked_challenge().run()
