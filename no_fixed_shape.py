#!/usr/bin/env python3
"""NO FIXED SHAPE - a short text puzzle about attention and lucid dreaming."""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass, field


LINE_WIDTH = 76


def prose(text: str) -> str:
    """Wrap narrative paragraphs without flattening intentional blank lines."""
    return "\n\n".join(
        textwrap.fill(part.strip(), LINE_WIDTH) if part.strip() else ""
        for part in text.split("\n\n")
    )


def understand(raw_command: str) -> str:
    """Map natural player language to a canonical game intention."""
    text = re.sub(r"[^a-z0-9']+", " ", raw_command.lower()).strip()
    corrections = {
        "examime": "examine", "exmine": "examine", "inspectt": "inspect",
        "wal": "wall", "walll": "wall", "walpaper": "wallpaper",
        "cieling": "ceiling", "celing": "ceiling", "ligth": "light",
        "ligthbulb": "lightbulb", "dor": "door", "dooor": "door",
        "opne": "open", "trun": "turn", "arround": "around",
        "clibm": "climb", "jumpp": "jump", "eyse": "eyes",
    }
    text = " ".join(corrections.get(word, word) for word in text.split())
    words = set(text.split())

    if not text:
        return ""
    if text in {"help", "commands", "controls", "instructions", "?"}:
        return "help"
    if words & {"quit", "exit", "leave"} and "room" not in words:
        return "quit"
    if text in {"think", "hint", "consider", "ponder", "reflect", "im stuck", "stuck"}:
        return "think"
    if "what do i do" in text or "what should i do" in text or "help me" in text:
        return "think"

    if words & {"wake", "awaken"}:
        return "close eyes"
    if words & {"eyes", "eyelids"} and words & {"close", "shut", "cover"}:
        return "close eyes"
    if "stop looking" in text or "stop observing" in text or "let go" in text:
        return "close eyes"

    door_words = {"door", "doorway", "entrance", "exit", "threshold"}
    door_actions = {
        "open", "enter", "use", "push", "pull", "unlock", "cross", "through",
        "interact", "walk", "go", "step", "pass", "rush", "charge", "break",
        "smash", "kick", "hit", "ram",
    }
    if words & door_words and words & door_actions:
        return "open door"
    if text in {"go through", "walk through", "step through", "pass through", "open it", "use it"}:
        return "open door"
    if "it" in words and words & {"open", "enter", "push", "pull", "break", "smash", "kick", "through"}:
        return "open door"
    if text in {"look at it", "examine it", "inspect it", "check it", "turn toward it", "look toward it"}:
        return "inspect it"

    if "turn around" in text or "look behind" in text or "check behind" in text:
        return "turn around"
    if words & {"turn", "spin", "rotate"} and words & {"around", "back", "behind"}:
        return "turn around"

    if words & {"jump", "leap", "hop", "bounce"}:
        return "jump"
    if text in {"climb", "scale", "scramble up"}:
        return "climb wall"
    if words & {"climb", "scale", "scramble"} and words & {"wall", "walls", "wallpaper"}:
        return "climb wall"
    if words & {"fall", "drop", "trip", "collapse"}:
        return "fall"
    if "count" in words and words & {"finger", "fingers", "digits", "hand"}:
        return "count fingers"
    if words & {"pinch", "poke"} and words & {"self", "myself", "arm", "skin", "hand"}:
        return "pinch self"
    travel_words = {"walk", "run", "sprint", "cross", "traverse", "move", "travel", "go"}
    travel_targets = {"room", "across", "forward", "opposite", "side", "wall"}
    if words & travel_words and words & travel_targets:
        return "cross room"

    observe_words = {
        "look", "examine", "inspect", "check", "study", "observe", "watch",
        "investigate", "touch", "feel", "view", "stare", "analyze", "interact",
        "describe", "what", "notice",
    }
    if words & {"door", "doorway"} and words & observe_words:
        return "examine door"
    if words & {"wall", "walls", "wallpaper", "pattern", "fungus", "bacteria", "seam", "seams", "corner", "corners"}:
        if words & observe_words or len(words) <= 3:
            return "examine wall"
    if words & {"light", "lightbulb", "bulb", "lamp"}:
        if words & observe_words or len(words) <= 3:
            return "examine lightbulb"
    if "floor" in words or "ground" in words:
        if words & observe_words or len(words) <= 3:
            return "examine floor"
    if "ceiling" in words or "roof" in words:
        if words & observe_words or len(words) <= 3:
            return "examine ceiling"
    if words & {"hand", "hands", "finger", "fingers", "body", "self"}:
        if words & observe_words or len(words) <= 3:
            return "examine hand"

    if text in {"look", "l", "observe", "look around", "examine room", "inspect room"}:
        return "look"
    if "where am i" in text or "describe the room" in text or "my surroundings" in text:
        return "look"
    if text in {"examine", "inspect", "interact", "touch", "use"}:
        return "missing object"
    if text in {"move", "go", "walk", "run"}:
        return "missing movement"
    return "unknown"


@dataclass
class PuzzleState:
    room_number: int = 1
    examinations: int = 0
    wallpaper_checks: int = 0
    surfaces_examined: set[str] = field(default_factory=set)
    door_felt: bool = False
    door_disappeared: bool = False
    environment_understood: bool = False
    lucid: bool = False
    door_visible: bool = False
    crossed_first_door: bool = False
    escaped: bool = False


class NoFixedShape:
    """Command-driven state machine for the puzzle."""

    WALL_STAGES = (
        "The wallpaper has a faint organic pattern. It looks less printed than grown.",
        "The pattern pulses like bacteria or fungus moving beneath a thin surface. "
        "Its rhythm is uncomfortably close to a heartbeat.",
        "The pattern is different now. Shapes that repeated before have changed size, "
        "split apart, and rejoined in the wrong places.",
        "The seams at the room's corners are fading. The walls soften into one another, "
        "as if the room is forgetting where one wall ends and the next begins.",
        "The corners melt away. What used to be four walls has become one continuous "
        "surface wrapped around the room.",
    )

    def __init__(self) -> None:
        self.state = PuzzleState()

    def introduction(self) -> str:
        return prose(
            "NO FIXED SHAPE\n\n"
            "You wake up in your own mind.\n\n"
            "Four unbroken, wallpapered walls surround you. There are no doors or windows. A single "
            "lightbulb hangs from the ceiling, illuminating the entire room even though "
            "its light should not be able to reach that far.\n\n"
            "You need to get out.\n\n"
            "Type HELP to see the available commands."
        )

    def process(self, raw: str) -> tuple[str, bool]:
        command = understand(raw)
        if command == "inspect it":
            command = "examine door" if self.state.door_felt or self.state.door_visible else "missing object"
        if not command:
            return "You remain still. The wallpaper continues to pulse.", True

        if command in {"quit", "exit"}:
            return "You leave the puzzle unfinished.", False
        if command in {"help", "commands", "?"}:
            return self.help_text(), True
        if command in {"think", "hint", "consider"}:
            return self.hint(), True
        if command in {"look", "look around", "examine room", "inspect room"}:
            return self.look(), True
        if command in {"turn", "turn around", "look behind", "look for door"}:
            return self.turn_around(), True
        if command in {"open door", "open", "enter door", "go through door"}:
            return self.open_door(), True
        if command in {"close eyes", "close my eyes", "wake", "wake up"}:
            return self.close_eyes()

        physical = self.physical_action(command)
        if physical is not None:
            return physical, True

        target = self.examination_target(command)
        if target is not None:
            return self.examine(target), True

        if command == "missing object":
            return "What do you want to examine or interact with?", True
        if command == "missing movement":
            return "How or where do you want to move?", True

        return (
            "The game could not understand that intention. Use a basic verb such as "
            "LOOK, EXAMINE, INTERACT, MOVE, or THINK.",
            True,
        )

    def help_text(self) -> str:
        return prose(
            "COMMANDS\n\n"
            "LOOK                        Observe your surroundings.\n"
            "EXAMINE <SOMETHING>         Study something you notice.\n"
            "INTERACT WITH <SOMETHING>   Attempt an interaction.\n"
            "MOVE <SOMEWHERE OR SOMEHOW> Describe how you want to move.\n"
            "THINK                       Consider what you have discovered.\n"
            "QUIT                        End the game.\n\n"
            "You may type short commands or complete sentences."
        )

    def look(self) -> str:
        state = self.state
        if state.lucid and state.door_visible:
            return prose(
                "The room is stationary only because you expect it to be. The single "
                "lightbulb still hangs above you. A door is clearly visible in one wall. "
                "It has no lock, handle, or doorknob, but it no longer disappears when "
                "you look directly at it."
            )
        if state.crossed_first_door:
            return prose(
                f"ROOM {state.room_number} looks almost the same as the first: four walls, "
                "one lightbulb, and no visible exit. The wallpaper pattern is slightly "
                "different. The door you used is gone without a seam or mark to prove it "
                "was ever there."
            )
        if state.door_felt:
            return prose(
                "You know something solid is behind you because you just backed into it. "
                "The four walls in front of you still appear unbroken."
            )
        return prose(
            "Four walls, a floor, a ceiling, and one hanging lightbulb. There are no "
            "doors or windows. The bulb never changes, but the distance between it and "
            "the room no longer feels reliable."
        )

    def examination_target(self, command: str) -> str | None:
        for prefix in ("examine ", "inspect ", "look at ", "check "):
            if command.startswith(prefix):
                target = command[len(prefix):].strip()
                aliases = {
                    "a wall": "wall",
                    "another wall": "wall",
                    "walls": "wall",
                    "pattern": "wallpaper",
                    "the wallpaper": "wallpaper",
                    "the ceiling": "ceiling",
                    "the floor": "floor",
                    "ground": "floor",
                    "bulb": "lightbulb",
                    "light": "lightbulb",
                    "the lightbulb": "lightbulb",
                    "my hand": "hand",
                    "hands": "hand",
                    "fingers": "hand",
                    "the door": "door",
                }
                return aliases.get(target, target)
        return None

    def examine(self, target: str) -> str:
        if target not in {"wall", "wallpaper", "ceiling", "floor", "lightbulb", "hand", "door"}:
            return f"There is nothing clearly identifiable as {target!r}."

        if target == "door":
            return self.examine_door()

        state = self.state
        state.examinations += 1
        state.surfaces_examined.add(target)

        door_event = ""
        if state.examinations == 2 and not state.lucid and not state.door_disappeared:
            state.door_felt = True
            door_event = (
                "\n\nWhile concentrating on it, you step backward and bump into something "
                "flat and solid. It feels exactly like a door standing behind you."
            )

        if target in {"wall", "wallpaper"}:
            state.wallpaper_checks += 1
            index = min(state.wallpaper_checks, len(self.WALL_STAGES) - 1)
            description = self.WALL_STAGES[index]
            if state.wallpaper_checks >= 2:
                scale = (
                    " The room's volume changes while you watch. The wall moves farther "
                    "away, but the lightbulb remains the same size and in the same place. "
                    "Its light stretches across the new distance as if normal physics do "
                    "not apply."
                )
            else:
                scale = ""
            result = description + scale
        elif target == "lightbulb":
            result = (
                "The lightbulb does not change or disappear. The room expands and becomes "
                "smaller around it, yet its light always reaches every surface. It is the "
                "only stable point in the space."
            )
        elif target == "ceiling":
            result = (
                "The ceiling rises while the lightbulb remains hanging in the same place. "
                "The room gains volume without becoming darker. Along the upper corners, "
                "the seams are beginning to fade."
            )
        elif target == "floor":
            result = (
                "The floor stretches away from you. The room should now be larger, but the "
                "light still covers all of it evenly. The wall seams soften at the edges of "
                "your vision."
            )
        else:
            result = (
                "Your hand looks almost correct, but your fingers shift when you stop "
                "focusing on them. A careful reality check may reveal more."
            )

        if state.wallpaper_checks >= 2 and state.examinations >= 3:
            state.environment_understood = True

        if state.crossed_first_door and state.lucid and state.examinations >= 2:
            state.door_visible = True
            result += (
                "\n\nA new door settles into one wall. Because you are lucid, it remains "
                "stationary when you look at it."
            )

        return prose(result + door_event)

    def examine_door(self) -> str:
        state = self.state
        if state.lucid and state.door_visible:
            return prose(
                "The door is stationary and can immediately be recognized. It has no "
                "lock, handle, or doorknob because it was never physically locked. It "
                "seems to be waiting for a decision rather than a physical key."
            )
        if state.door_felt:
            state.door_felt = False
            state.door_disappeared = True
            return prose(
                "You turn toward the solid surface you bumped into. It disappears before "
                "you can see it. There is only a seamless wall where the door should be."
            )
        return "There is no door that you can directly examine."

    def turn_around(self) -> str:
        state = self.state
        if state.lucid and state.door_visible:
            return "You turn around. The door remains stationary and fully visible."
        if state.door_felt:
            state.door_felt = False
            state.door_disappeared = True
            return prose(
                "You turn around to look at the door. It is gone. A blank, seamless wall "
                "stands where the solid surface touched your back."
            )
        return "You turn around. The room rearranges itself, but no door remains in view."

    def physical_action(self, command: str) -> str | None:
        actions = {
            "cross room": (
                "You walk toward the opposite wall. It moves away at the same rate, so you "
                "are travelling without getting any closer. You are running in place inside "
                "your own mind."
            ),
            "traverse room": (
                "You cross the room, but distance stretches beneath each step. The wall is "
                "never closer even though you continue moving."
            ),
            "walk across room": (
                "You walk toward the opposite wall. It moves away at the same rate, leaving "
                "you in the center no matter how far you travel."
            ),
            "jump": (
                "You jump. The floor drops away instead of your body rising. For a moment, "
                "the lightbulb hangs beside you rather than above you."
            ),
            "fall": (
                "You intentionally let yourself fall forward. The floor bends away before "
                "you reach it, then places you upright again. Within this space, the test "
                "causes no injury."
            ),
            "fall down": (
                "You intentionally let yourself fall. The floor refuses the impact and "
                "returns you to your feet."
            ),
            "climb wall": (
                "You climb the wall. Its orientation changes beneath your hands until the "
                "wall becomes the floor and the old floor stands vertically behind you."
            ),
            "climb the wall": (
                "You climb the wall. It rotates into a floor beneath you without the "
                "lightbulb changing position."
            ),
            "count fingers": (
                "You count your fingers. The number changes before you finish, as if your "
                "mind is trying to remember what a hand is supposed to look like."
            ),
            "count my fingers": (
                "You count your fingers. The number changes before you finish."
            ),
            "pinch self": (
                "You pinch your arm gently. The pressure arrives late, as if the sensation "
                "had to be invented after the action. You do not wake."
            ),
            "pinch myself": (
                "You pinch your arm gently. The sensation does not behave normally."
            ),
        }
        result = actions.get(command)
        if result is None:
            return None

        if self.state.environment_understood and not self.state.lucid:
            self.state.lucid = True
            self.state.door_visible = True
            result += (
                "\n\nThe room is not real. It does not abide by any logical understanding "
                "of physics. It is almost as if it were trying to remember what a room is "
                "supposed to look like.\n\n"
                "The realization makes you fully lucid. The space stops changing without "
                "your permission. A stationary door can now be clearly recognized in one wall."
            )
        elif not self.state.environment_understood and not self.state.lucid:
            result += (
                "\n\nThe experience is wrong, but you do not yet understand the rule controlling it."
            )
        return prose(result)

    def open_door(self) -> str:
        state = self.state
        if not state.lucid:
            if state.door_felt:
                state.door_felt = False
                state.door_disappeared = True
                return prose(
                    "You reach for the door behind you. The moment you try to treat it as "
                    "a normal object, it disappears. Your hand touches a blank wall."
                )
            return "There is no stable door to open."
        if not state.door_visible:
            return "This room currently has four empty walls and no visible door."

        state.room_number += 1
        state.crossed_first_door = True
        state.door_visible = False
        state.door_felt = False
        state.examinations = 0
        state.wallpaper_checks = 0
        state.surfaces_examined.clear()
        return prose(
            "There was never a lock or doorknob. You decide that the door opens, and it "
            "does. You pass through.\n\n"
            f"ROOM {state.room_number} is waiting on the other side. It is almost the same "
            "as the previous room, but the wallpaper has reconstructed itself into a "
            "slightly different pattern.\n\n"
            "When you look back, the old door is no longer there. The previous room has "
            "been erased or merged into this one without any sign it ever existed. You are "
            "back in an empty room with four walls again."
        )

    def close_eyes(self) -> tuple[str, bool]:
        state = self.state
        if state.lucid and state.crossed_first_door:
            state.escaped = True
            return prose(
                "The door was never the actual exit. Every room was the same thought "
                "rebuilding itself around you. You were only running in place.\n\n"
                "You close your eyes and stop giving the space a shape. The walls, the "
                "pulsing wallpaper, and the impossible light disappear.\n\n"
                "You wake up.\n\nEND: LUCID AWAKENING"
            ), False
        if state.lucid:
            return prose(
                "You close your eyes, but uncertainty keeps the first room intact. When "
                "you open them, the stationary door is still waiting."
            ), True
        return prose(
            "You close your eyes and try to wake up. When you open them, the room is still "
            "there, but its proportions have changed again."
        ), True

    def hint(self) -> str:
        state = self.state
        if state.door_felt and not state.lucid:
            return "You bumped into something solid. What happens if you try to look at it?"
        if state.crossed_first_door and not state.door_visible:
            return prose(
                "You went through the door, but you are still inside the same thought. The "
                "real exit may require you to stop observing the room entirely."
            )
        if state.wallpaper_checks < 2:
            return "The wallpaper may not look the same the next time you examine it."
        if not state.environment_understood:
            return prose(
                "Compare the changing walls, floor, or ceiling with the one object that "
                "never changes: the lightbulb."
            )
        if not state.lucid:
            return prose(
                "If the room does not obey normal physics, test what happens when you move "
                "through it, jump, fall, or climb."
            )
        if state.door_visible:
            return "The door has no lock or handle because it was never physically locked."
        return "The room is waiting for you to decide what is real."


def play() -> int:
    game = NoFixedShape()
    print("=" * LINE_WIDTH)
    print(game.introduction())
    print("=" * LINE_WIDTH)
    running = True
    while running:
        try:
            command = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\n\nThe room fades from view.")
            return 0
        response, running = game.process(command)
        print("\n" + response)
    return 0


def self_test() -> int:
    game = NoFixedShape()

    game.process("examine wall")
    response, _ = game.process("examine ceiling")
    assert game.state.door_felt and "bump" in response.lower()
    response, _ = game.process("turn around")
    assert game.state.door_disappeared and "gone" in response.lower()

    game.process("examine wallpaper")
    assert game.state.environment_understood
    response, _ = game.process("cross room")
    assert game.state.lucid and game.state.door_visible and "fully lucid" in response

    response, _ = game.process("open door")
    assert game.state.room_number == 2 and game.state.crossed_first_door
    assert not game.state.door_visible and "old door is no longer there" in response

    response, running = game.process("close eyes")
    assert game.state.escaped and not running and "LUCID AWAKENING" in response

    loop = NoFixedShape()
    loop.process("examine wall")
    loop.process("examine wallpaper")
    loop.process("examine floor")
    loop.process("jump")
    loop.process("open door")
    loop.process("examine wall")
    response, _ = loop.process("examine ceiling")
    assert loop.state.door_visible and "new door" in response.lower()
    loop.process("open door")
    assert loop.state.room_number == 3

    print("SELF-TEST PASSED: discovery, disappearing door, lucidity, room loop, and waking verified.")
    return 0


def arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play NO FIXED SHAPE.")
    parser.add_argument("--self-test", action="store_true", help="verify puzzle state transitions")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = arguments(sys.argv[1:])
    raise SystemExit(self_test() if args.self_test else play())
