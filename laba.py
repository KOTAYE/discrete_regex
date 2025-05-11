'''laba'''
from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """
    State class for the FSM
    Each state can have multiple next states, which are checked when a character is processed.
    """
    @abstractmethod
    def __init__(self) -> None:
        """
        Initializes the state with an empty list of next states.
        This list will be populated with the next states that can be reached from this state.
        """
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether the occurred character is handled by the current state
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        """
        Checks the next state based on the current character.
        If the character is handled by the current state, it returns the next state.
        """
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    """
    Class for the start state of the FSM.
    This state is the entry point for the FSM and does not handle any characters itself.
    """
    def __init__(self):
        """
        Initializes the start state with an empty list of next states.
        The start state does not handle any characters itself, so the list is empty.
        """
        self.next_states = []

    def check_self(self, char):
        """
        Checks if the current character is handled by the start state.
        The start state does not handle any characters, so it always returns False.
        """
        return True


class TerminationState(State):
    """
    Class for the termination state of the FSM.
    This state is reached when the input string has been fully processed and is accepted by the FSM.
    """
    def __init__(self):
        """
        Initializes the termination state with an empty list of next states.
        The termination state does not handle any characters itself, so the list is empty.
        """
        self.next_states = []

    def check_self(self, char: str):
        """
        Checks if the current character is handled by the termination state.
        The termination state does not handle any characters, so it always returns False.
        """
        return False


class DotState(State):
    """
    State for '.' character (any character accepted)
    """
    def __init__(self):
        """
        initializes the dot state with an empty list of next states.
        The dot state can transition to any other state, so the list is empty initially.
        """
        self.next_states = []

    def check_self(self, char: str):
        """
        Checks if the current character is handled by the dot state.
        The dot state accepts any character, so it always returns True.
        """
        return True


class AsciiState(State):
    """
    State for alphabet letters or numbers
    """
    def __init__(self, symbol: str) -> None:
        """
        Initializes the AsciiState with a specific character.
        The character is stored in the curr_sym attribute.
        """
        self.next_states = []
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        """
        Checks if the current character matches the stored character.
        If it matches, it returns True; otherwise, it returns False.
        """
        return curr_char == self.curr_sym


class StarState(State):
    """
    Class for '*' character (zero or more occurrences of the previous state)
    This state can transition to the previous state or itself, allowing for zero 
    or more occurrences.
    """
    def __init__(self, checking_state: State):
        """
        Initializes the StarState with a specific checking state.
        The checking state is the state that is being repeated zero or more times.
        """
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        """
        Checks if the current character is handled by the checking state.
        The star state allows for zero or more occurrences of the checking state,
        so it returns True if the checking state accepts the character.
        If the checking state does not accept the character, it returns False.
        """
        return self.checking_state.check_self(char)


class PlusState(State):
    """
    Class for '+' character (one or more occurrences of the previous state)
    This state can transition to the previous state or itself, allowing for one or more occurrences.
    """
    def __init__(self, checking_state: State):
        """
        Initializes the PlusState with a specific checking state.
        The checking state is the state that is being repeated one or more times.
        """
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        """
        Checks if the current character is handled by the checking state.
        The plus state requires at least one occurrence of the checking state,
        so it returns True if the checking state accepts the character.
        If the checking state does not accept the character, it returns False.
        """
        return self.checking_state.check_self(char)


class RegexFSM:
    """
    Finite State Machine for regex pattern matching.
    This class compiles a regex pattern into a finite state machine (FSM) and provides
    a method to check if an input string matches the pattern.
    """
    def __init__(self, regex_expr: str) -> None:
        """
        Initializes the FSM with a regex pattern.
        The regex pattern is processed to create states and transitions based on the
        characters in the pattern.
        """
        self.start_state = StartState()
        self.terminal_state = TerminationState()
        self.states = [self.start_state]

        prev_state = self.start_state
        tmp_next_state = None

        i = 0
        while i < len(regex_expr):
            char = regex_expr[i]

            if char == '*':
                if tmp_next_state is None:
                    raise ValueError("* cannot be the first character")
                star_state = StarState(tmp_next_state)
                prev_state.next_states[-1] = star_state
                star_state.next_states.append(tmp_next_state)
                star_state.next_states.append(star_state)
                tmp_next_state = star_state
                self.states.append(star_state)
                i += 1
                continue

            elif char == '+':
                if tmp_next_state is None:
                    raise ValueError("+ cannot be the first character")
                plus_state = PlusState(tmp_next_state)
                prev_state.next_states[-1] = plus_state
                plus_state.next_states.append(tmp_next_state)
                tmp_next_state.next_states.append(tmp_next_state)
                self.states.append(plus_state)
                i += 1
                continue

            new_state = self.__init_next_state(char)
            if tmp_next_state:
                tmp_next_state.next_states.append(new_state)
            else:
                prev_state.next_states.append(new_state)
            tmp_next_state = new_state
            self.states.append(new_state)
            i += 1

        if tmp_next_state:
            tmp_next_state.next_states.append(self.terminal_state)
        else:
            self.start_state.next_states.append(self.terminal_state)

    def __init_next_state(self, token: str) -> State:
        """
        Initializes the next state based on the token.
        If the token is a dot (.), it creates a DotState.
        """
        if token == ".":
            return DotState()
        if token.isascii():
            return AsciiState(token)
        raise ValueError(f"Unsupported token: {token}")

    def check_string(self, input_string: str) -> bool:
        """
        Check if input string matches the regex pattern
        """
        current_positions = [(self.start_state, 0)]
        string_len = len(input_string)

        while current_positions:
            state, pos = current_positions.pop(0)

            if pos == string_len:
                if self.terminal_state in state.next_states:
                    return True

                for next_state in state.next_states:
                    if isinstance(next_state, StarState) and self.terminal_state \
in next_state.next_states:
                        return True
                continue

            char = input_string[pos]

            for next_state in state.next_states:
                if next_state.check_self(char):
                    current_positions.append((next_state, pos + 1))

                if isinstance(next_state, StarState):
                    for s in next_state.next_states:
                        if s != next_state:
                            current_positions.append((s, pos))

        return False



if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
