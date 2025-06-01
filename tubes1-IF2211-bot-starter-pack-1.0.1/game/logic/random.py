from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

class MyBot(BaseLogic):
    def __init__(self):
        super().__init__()
        self.last_position = None
        self.stuck_count = 0
        self.base_position = None

    def next_move(self, board_bot: GameObject, board: Board) -> tuple[int, int]:
        def manhattan_distance(pos1: Position, pos2: Position) -> int:
            return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

        def move_to_target(current: Position, target: Position) -> tuple[int, int]:
            if current.x == target.x and current.y == target.y:
                return (0, 0)

            # Teleporter handling
            teleporters = [obj.position for obj in board.game_objects if obj.type == "TeleportGameObject"]
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

            # Prioritizing longer distance axis first
            x_dist = abs(current.x - target.x)
            y_dist = abs(current.y - target.y)

            if x_dist > y_dist and dx != 0:
                return (dx, 0)
            elif dy != 0:
                return (0, dy)
            elif dx != 0:
                return (dx, 0)

            return (0, 0)

        def calculate_effective_distance(start: Position, end: Position) -> int:
            teleporters = [obj.position for obj in board.game_objects if obj.type == "TeleportGameObject"]
            if len(teleporters) != 2:
                return manhattan_distance(start, end)

            tele1, tele2 = teleporters
            options = [
                manhattan_distance(start, end),
                manhattan_distance(start, tele1) + manhattan_distance(tele2, end),
                manhattan_distance(start, tele2) + manhattan_distance(tele1, end)
            ]
            return min(options)

        def find_closest_diamond(from_pos: Position) -> tuple[Position | None, int]:
            closest = None
            min_distance = float('inf')
            for obj in board.game_objects:
                if obj.type == "DiamondGameObject":
                    dist = manhattan_distance(from_pos, obj.position)
                    if dist < min_distance:
                        min_distance = dist
                        closest = obj.position
            return closest, min_distance

        def find_most_diamonds_teleport() -> tuple[Position | None, int]:
            # Cari teleport yang dekat dengan banyak diamond
            teleporters = [obj.position for obj in board.game_objects if obj.type == "TeleportGameObject"]
            if len(teleporters) != 2:
                return None, 0

            counts = []
            for tele in teleporters:
                count = sum(1 for obj in board.game_objects if obj.type == "DiamondGameObject" and manhattan_distance(tele, obj.position) <= 5)
                counts.append((tele, count))
            counts.sort(key=lambda x: x[1], reverse=True)
            if counts and counts[0][1] > 0:
                return counts[0][0], counts[0][1]
            return None, 0

        def find_closest_red_box(from_pos: Position) -> tuple[Position | None, int]:
            closest = None
            min_distance = float('inf')
            for obj in board.game_objects:
                if obj.type == "RedBoxGameObject":
                    dist = manhattan_distance(from_pos, obj.position)
                    if dist < min_distance:
                        min_distance = dist
                        closest = obj.position
            return closest, min_distance

        def check_if_stuck(current_pos: Position) -> bool:
            if self.last_position and self.last_position.x == current_pos.x and self.last_position.y == current_pos.y:
                self.stuck_count += 1
            else:
                self.stuck_count = 0
            self.last_position = current_pos
            return self.stuck_count > 2

        def handle_stuck(current_pos: Position) -> tuple[int, int]:
            # Coba gerakan random ke arah yang valid untuk keluar stuck
            moves = [(1,0), (-1,0), (0,1), (0,-1)]
            for dx, dy in moves:
                nx, ny = current_pos.x + dx, current_pos.y + dy
                if 0 <= nx < board.width and 0 <= ny < board.height:
                    return (dx, dy)
            return (0, 0)

        # Mulai logic utama
        current_pos = board_bot.position
        props = board_bot.properties
        self.base_position = props.base

        # Cek stuck
        if check_if_stuck(current_pos):
            return handle_stuck(current_pos)

        # Jika inventory penuh, kembali ke base
        if props.diamonds == 5:
            return move_to_target(current_pos, self.base_position)

        # Cari diamond terdekat
        closest_diamond, dist_diamond = find_closest_diamond(current_pos)

        # Cari teleport dengan banyak diamond dekatnya
        best_teleport, count_teleport = find_most_diamonds_teleport()

        # Cari kotak merah terdekat
        closest_red_box, dist_red_box = find_closest_red_box(current_pos)

        # Logika prioritas:
        # 1. Jika membawa diamond dan base lebih dekat, kembali base
        dist_base = calculate_effective_distance(current_pos, self.base_position)
        if props.diamonds > 0 and dist_base < dist_diamond:
            return move_to_target(current_pos, self.base_position)

        # 2. Jika ada diamond dekat, kejar diamond
        if closest_diamond:
            return move_to_target(current_pos, closest_diamond)

        # 3. Jika tidak ada diamond, cek kotak merah dan teleport
        if closest_red_box and best_teleport:
            if dist_red_box < manhattan_distance(current_pos, best_teleport):
                return move_to_target(current_pos, closest_red_box)
            else:
                return move_to_target(current_pos, best_teleport)
        elif closest_red_box:
            return move_to_target(current_pos, closest_red_box)
        elif best_teleport:
            return move_to_target(current_pos, best_teleport)

        # 4. Jika tidak ada apa2, kembali ke base
        return move_to_target(current_pos, self.base_position)
