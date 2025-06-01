from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

class MyBot(BaseLogic):
    def __init__(self):
        super().__init__()
        self.last_position = None
        self.back_to_base = False
        self.target_diamond = None
        self.stuck_count = 0
        self.base_position = None
        self.teleporters = []
        self.visited_positions = set()

    def next_move(self, board_bot: GameObject, board: Board) -> tuple[int, int]:
        # Helper function: Manhattan distance
        def manhattan_distance(pos1: Position, pos2: Position) -> int:
            return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

        # Helper function: Move to target
        def move_to_target(current: Position, target: Position) -> tuple[int, int]:
            if current.x == target.x and current.y == target.y:
                return (0, 0)

            # Handle teleporter
            if len(teleporters) == 2:
                tele1, tele2 = teleporters
                if current.x == tele1.x and current.y == tele1.y:
                    target = tele2
                elif current.x == tele2.x and current.y == tele2.y:
                    target = tele1

            dx = 0
            dy = 0
            
            if current.x < target.x:
                dx = 1
            elif current.x > target.x:
                dx = -1
                
            if current.y < target.y:
                dy = 1
            elif current.y > target.y:
                dy = -1

            x_dist = abs(current.x - target.x)
            y_dist = abs(current.y - target.y)
            
            if x_dist > y_dist and dx != 0:
                return (dx, 0)
            elif dy != 0:
                return (0, dy)
            elif dx != 0:
                return (dx, 0)
            
            return (0, 0)

        # Helper function: Calculate effective distance
        def calculate_effective_distance(start: Position, end: Position) -> int:
            if len(teleporters) != 2:
                return manhattan_distance(start, end)

            tele1, tele2 = teleporters
            options = [
                manhattan_distance(start, end),
                manhattan_distance(start, tele1) + manhattan_distance(tele2, end),
                manhattan_distance(start, tele2) + manhattan_distance(tele1, end)
            ]
            return min(options)

        # Helper function: Find closest diamond
        def find_closest_diamond(from_pos: Position) -> tuple[Position, float]:
            closest = None
            min_distance = float('inf')

            for obj in board.game_objects:
                if obj.type == "DiamondGameObject":
                    distance = manhattan_distance(from_pos, obj.position)
                    if distance < min_distance:
                        min_distance = distance
                        closest = obj.position

            return closest, min_distance

        # Helper function: Check if stuck
        def check_if_stuck(current_pos: Position) -> bool:
            nonlocal last_position, stuck_count
            if last_position and last_position.x == current_pos.x and last_position.y == current_pos.y:
                stuck_count += 1
            else:
                stuck_count = 0
            last_position = current_pos
            return stuck_count > 2

        # Helper function: Handle stuck situation
        def handle_stuck_situation(current_pos: Position) -> tuple[int, int]:
            nonlocal back_to_base, stuck_count
            back_to_base = True
            stuck_count = 0
            return move_to_target(current_pos, base_position)

        # Main logic
        current_pos = board_bot.position
        props = board_bot.properties
        base_position = props.base
        last_position = self.last_position
        stuck_count = self.stuck_count
        back_to_base = self.back_to_base
        teleporters = [obj.position for obj in board.game_objects if obj.type == "TeleportGameObject"]
        self.visited_positions.add((current_pos.x, current_pos.y))

        # Check if stuck
        if check_if_stuck(current_pos):
            return handle_stuck_situation(current_pos)

        # Jika inventory penuh, langsung kembali ke base
        if props.diamonds == 5:
            return move_to_target(current_pos, base_position)

        # Hitung jarak ke base
        base_distance = calculate_effective_distance(current_pos, base_position)

        # Cari diamond terdekat
        closest_diamond, closest_diamond_distance = find_closest_diamond(current_pos)

        # Jika sedang membawa diamond dan base lebih dekat, utamakan kembali ke base
        if props.diamonds > 0 and base_distance < closest_diamond_distance:
            return move_to_target(current_pos, base_position)

        # Jika ada diamond yang bisa diambil
        if closest_diamond:
            # Cek apakah melalui teleporter lebih efisien
            if len(teleporters) == 2:
                tele1, tele2 = teleporters
                
                via_tele1 = (manhattan_distance(current_pos, tele1) + 
                            manhattan_distance(tele2, closest_diamond))
                
                via_tele2 = (manhattan_distance(current_pos, tele2) + 
                            manhattan_distance(tele1, closest_diamond))
                
                if via_tele1 < closest_diamond_distance and via_tele1 < via_tele2:
                    return move_to_target(current_pos, tele1)
                elif via_tele2 < closest_diamond_distance:
                    return move_to_target(current_pos, tele2)

            return move_to_target(current_pos, closest_diamond)

        # Default: kembali ke base
        return move_to_target(current_pos, base_position)