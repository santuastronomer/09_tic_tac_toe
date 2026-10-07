"""
GameEngine: owns the board, turn state, round-end logic,
scoreboard, first-player selection, and reset controls.
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        # Task 2: persistent scoreboard
        self.scores = {
            'X': 0,
            'O': 0,
            'draws': 0
        }

        # Task 4: X or O starts the round
        self.starting_player = 'X'

        self.reset_round()

    def reset_round(self):
        """Start a new round while preserving the scoreboard."""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.starting_player
        self.round_over = False
        self.winner = None

        # If O is selected to start, the computer moves first.
        if self.current_player == COMPUTER_SYMBOL:
            self._maybe_take_computer_turn()

    def reset_match(self):
        """Reset the board and the entire scoreboard."""
        self.scores = {
            'X': 0,
            'O': 0,
            'draws': 0
        }

        self.reset_round()

    def select_first_player(self, player):
        """Select X or O as the player who starts the round."""
        if player not in ('X', 'O'):
            return

        self.starting_player = player
        self.reset_round()

    def handle_click(self, pos):
        if self.round_over:
            return

        # Human always plays X.
        # If O starts, the computer makes its move automatically.
        if self.current_player != HUMAN_SYMBOL:
            return

        cell = board_pos_to_cell(pos)

        if cell is None:
            return

        row, col = cell

        # Task 3: prevent overwriting an occupied cell.
        if self.board[row][col] is not None:
            return

        self.board[row][col] = self.current_player

        self.check_round_end()

        if self.round_over:
            return

        self.current_player = COMPUTER_SYMBOL
        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return

        move = choose_move(self.board)

        if move is None:
            return

        row, col = move

        # Safety check: never overwrite an occupied cell.
        if self.board[row][col] is not None:
            return

        self.board[row][col] = COMPUTER_SYMBOL

        self.check_round_end()

        if self.round_over:
            return

        self.current_player = HUMAN_SYMBOL

    def handle_keydown(self, key):
        import pygame

        # X starts the next round
        if key == pygame.K_x:
            self.select_first_player('X')

        # O starts the next round
        elif key == pygame.K_o:
            self.select_first_player('O')

        # Round Restart - keeps scoreboard
        elif key == pygame.K_r:
            self.reset_round()

        # Match Reset - clears scoreboard
        elif key == pygame.K_m:
            self.reset_match()

    def check_round_end(self):
        # Task 1: check winner BEFORE board-full check.
        winner = check_winner(self.board)

        if winner:
            self.round_over = True
            self.winner = winner

            # Task 2: update scoreboard exactly once.
            self.scores[winner] += 1
            return

        if is_board_full(self.board):
            self.round_over = True
            self.winner = None

            # Task 2: update draw score exactly once.
            self.scores['draws'] += 1

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_board(surface, self.board)

        # Current turn
        if self.current_player == HUMAN_SYMBOL:
            turn_label = "Your turn (X)"
        else:
            turn_label = "Computer's turn (O)"

        renderer.draw_text(
            surface,
            font,
            turn_label,
            (10, 20)
        )

        # Scoreboard
        scoreboard = (
            f"X Wins: {self.scores['X']}    "
            f"O Wins: {self.scores['O']}    "
            f"Draws: {self.scores['draws']}"
        )

        renderer.draw_text(
            surface,
            font,
            scoreboard,
            (10, 50)
        )

        # Controls
        controls = "X: X starts | O: O starts | R: Restart | M: Match Reset"

        renderer.draw_text(
            surface,
            font,
            controls,
            (10, 75)
        )

        # Round result
        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"

            renderer.draw_banner(
                surface,
                font,
                text
            )
