import random
import pygame
from game.block import Block


class Debris:
    def __init__(self, x, y, width, height, color, vx, vy, rotation_speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        self.vx = vx
        self.vy = vy
        self.gravity = 0.45

        self.angle = 0
        self.rotation_speed = rotation_speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vy += self.gravity
        self.angle += self.rotation_speed

    def render(self, screen):
        surface = pygame.Surface(
            (max(1, int(self.width)), max(1, int(self.height))),
            pygame.SRCALPHA
        )
        surface.fill(self.color)

        rotated = pygame.transform.rotate(surface, self.angle)

        rect = rotated.get_rect(
            center=(
                self.x + self.width / 2,
                self.y + self.height / 2
            )
        )

        screen.blit(rotated, rect)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.block_height = 28
        self.base_width = 180

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 46)

        # Task 4: atmospheric background stages.
        self.sky_colors = [
            (45, 75, 120),    # Twilight blue
            (75, 45, 100),    # Dusk purple
            (18, 24, 55),     # Night
            (5, 7, 18)        # Very dark stratosphere
        ]

        # Task 4: generate stars once and reuse them.
        self.stars = []

        for _ in range(90):
            self.stars.append(
                (
                    random.randint(0, self.width - 1),
                    random.randint(0, self.height - 1),
                    random.randint(1, 2)
                )
            )

        self.reset()

    def get_color(self, index):
        palette = [
            (230, 75, 75),
            (240, 140, 45),
            (245, 210, 50),
            (60, 195, 110),
            (50, 150, 240),
            (165, 80, 225),
        ]
        return palette[index % len(palette)]

    def reset(self):
        self.score = 0
        self.game_over = False
        self.perfect_streak = 0
        self.perfect_popup_timer = 0
        self.debris = []

        base_x = (self.width - self.base_width) // 2
        base_y = self.height - 60

        base_block = Block(
            base_x,
            base_y,
            self.base_width,
            self.block_height,
            self.get_color(0),
            speed=0
        )

        self.stack = [base_block]

        self.spawn_active_block()

    def spawn_active_block(self):
        top_block = self.stack[-1]

        next_y = top_block.y - self.block_height - 4
        speed = min(10.0, 4.5 + (len(self.stack) * 0.35))
        color = self.get_color(len(self.stack))

        start_x = (
            25
            if random.choice([True, False])
            else self.width - 25 - top_block.width
        )

        self.active_block = Block(
            start_x,
            next_y,
            top_block.width,
            self.block_height,
            color,
            speed=speed
        )

    def drop_block(self):
        if self.game_over:
            return

        top_block = self.stack[-1]
        act = self.active_block

        left = max(act.x, top_block.x)
        right = min(
            act.x + act.width,
            top_block.x + top_block.width
        )
        overlap = right - left

        # Task 1:
        # A positive overlap means the block successfully lands.
        is_successful_drop = overlap > 0

        if is_successful_drop:
            # Task 2:
            # A perfect placement occurs when the horizontal
            # alignment error is 3 pixels or less.
            is_perfect = abs(act.x - top_block.x) <= 3

            if is_perfect:
                self.perfect_streak += 1
                self.perfect_popup_timer = 30

                act.x = top_block.x

                new_width = act.width
                new_x = top_block.x

                if self.perfect_streak >= 3:
                    new_width += 10
                    new_x = top_block.x - 5

                new_block = Block(
                    new_x,
                    act.y,
                    new_width,
                    self.block_height,
                    act.color,
                    speed=0
                )

                self.score += 3

            else:
                # Task 2:
                # Normal placement breaks the perfect streak.
                self.perfect_streak = 0

                # Task 3:
                # Create debris for the left overhang.
                if act.x < top_block.x:
                    debris_width = left - act.x

                    if debris_width > 0:
                        self.debris.append(
                            Debris(
                                act.x,
                                act.y,
                                debris_width,
                                self.block_height,
                                act.color,
                                vx=-2.0,
                                vy=-2.0,
                                rotation_speed=-6
                            )
                        )

                # Task 3:
                # Create debris for the right overhang.
                if act.x + act.width > top_block.x + top_block.width:
                    debris_x = right
                    debris_width = (
                        act.x + act.width
                    ) - right

                    if debris_width > 0:
                        self.debris.append(
                            Debris(
                                debris_x,
                                act.y,
                                debris_width,
                                self.block_height,
                                act.color,
                                vx=2.0,
                                vy=-2.0,
                                rotation_speed=6
                            )
                        )

                trimmed_width = max(10.0, overlap)

                new_block = Block(
                    left,
                    act.y,
                    trimmed_width,
                    self.block_height,
                    act.color,
                    speed=0
                )

                self.score += 1

            self.stack.append(new_block)

            if new_block.y < 180:
                shift_amount = self.block_height + 4

                for b in self.stack:
                    b.y += shift_amount

            self.spawn_active_block()

        else:
            # Task 1:
            # No overlap means the tower collapses.
            self.game_over = True

    def handle_event(self, event):
        if self.game_over:
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ) or (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.reset()

            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        ):
            self.drop_block()

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            self.drop_block()

    def update(self):
        if not self.game_over:
            self.active_block.update(self.width)

        # Task 2:
        # Countdown PERFECT popup.
        if self.perfect_popup_timer > 0:
            self.perfect_popup_timer -= 1

        # Task 3:
        # Update falling debris.
        for debris in self.debris:
            debris.update()

        # Task 3:
        # Remove debris once it falls off-screen.
        self.debris = [
            debris
            for debris in self.debris
            if debris.y < self.height + 100
        ]

    def interpolate_color(self, color_a, color_b, amount):
        amount = max(0.0, min(1.0, amount))

        return tuple(
            int(a + (b - a) * amount)
            for a, b in zip(color_a, color_b)
        )

    def get_sky_color(self):
        # Task 4:
        # Use the number of successfully placed blocks as
        # atmospheric progress rather than real-world time.
        tower_height = max(0, len(self.stack) - 1)

        stage_height = 15
        total_stages = len(self.sky_colors) - 1

        progress = tower_height / stage_height

        stage_index = min(
            int(progress),
            total_stages - 1
        )

        local_progress = progress - stage_index

        return self.interpolate_color(
            self.sky_colors[stage_index],
            self.sky_colors[stage_index + 1],
            local_progress
        )

    def render(self, screen):
        # Task 4:
        # Atmospheric sky background.
        sky_color = self.get_sky_color()
        screen.fill(sky_color)

        # Task 4:
        # Gradually introduce stars during the night stages.
        tower_height = max(0, len(self.stack) - 1)

        star_start = 18
        star_full = 30

        if tower_height > star_start:
            star_alpha = int(
                255 * (
                    (tower_height - star_start)
                    / (star_full - star_start)
                )
            )

            star_alpha = max(0, min(255, star_alpha))

            for x, y, size in self.stars:
                star_surface = pygame.Surface(
                    (size, size),
                    pygame.SRCALPHA
                )

                star_surface.fill(
                    (255, 255, 255, star_alpha)
                )

                screen.blit(
                    star_surface,
                    (x, y)
                )

        title_surf = self.font_title.render(
            "Skyscraper Stack",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2
                - title_surf.get_width() // 2,
                16
            )
        )

        score_surf = self.font_hud.render(
            f"Height: {self.score}",
            True,
            (255, 220, 80)
        )

        screen.blit(
            score_surf,
            (
                self.width // 2
                - score_surf.get_width() // 2,
                54
            )
        )

        # Existing tower rendering.
        for b in self.stack:
            b.render(screen)

        # Task 3:
        # Render falling debris.
        for debris in self.debris:
            debris.render(screen)

        # Existing active block rendering.
        if not self.game_over:
            self.active_block.render(screen)

        # Task 2:
        # PERFECT popup.
        if self.perfect_popup_timer > 0:
            perfect_surf = self.font_hud.render(
                "PERFECT!",
                True,
                (255, 215, 0)
            )

            screen.blit(
                perfect_surf,
                (
                    self.width // 2
                    - perfect_surf.get_width() // 2,
                    90
                )
            )

        if self.game_over:
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render(
                "TOWER COLLAPSED!",
                True,
                (240, 75, 75)
            )

            screen.blit(
                over_surf,
                (
                    self.width // 2
                    - over_surf.get_width() // 2,
                    self.height // 2 - 40
                )
            )

            final_surf = self.font_hud.render(
                f"Final Height: {self.score}",
                True,
                (255, 255, 255)
            )

            screen.blit(
                final_surf,
                (
                    self.width // 2
                    - final_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )

            restart_surf = self.font_hud.render(
                "Press [Space] or [R] to Play Again",
                True,
                (200, 200, 200)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2
                    - restart_surf.get_width() // 2,
                    self.height // 2 + 50
                )
            )