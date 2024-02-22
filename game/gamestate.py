class GameState():
    def __init__(self, player_id=None, state = 0, already_done_moves=None, next_gamestate= None, interruption=False) -> None:
        self.player_id = player_id
        self.state = state
        # Moves such that can be described as "You can do it anytime x times."
        self.already_done_moves = already_done_moves if already_done_moves is not None else []
        # For gamestate where just from the state is unclear whats next,
        # like reaction decisions, for example reaveal or not as blackmailer
        self.next_gamestate = next_gamestate

        # Next is an interrupting decision if true, like blackmail reveal, magistrate, or graveyard
        self.interruption = interruption

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, GameState):
            return self.state == __value.state and self.player_id == __value.player_id
        return False