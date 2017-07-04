"""This module implements the player object (sprite) for Py-Climber"""

from tilemap import Tilemap
from animation import Animation
from animated_sprite import AnimatedSprite


class Player(AnimatedSprite):
    """Player object"""

    def __init__(self, settings, screen, images, tile_map):
        """Initialize the player sprite"""
        # Calls AnimatedSprite, which in turn will call pygame.Sprite __init_()
        super().__init__(settings, screen, images)

        # Override the initial position
        self.rect.bottom = tile_map.player_bounds_rect.bottom
        self.rect.left = self.screen.get_rect().width / 2

        # Set the transparent margins
        self.margin_left = self.settings.player_sprite_horz_margin
        self.margin_right = self.settings.player_sprite_horz_margin
        self.margin_top = self.settings.player_sprite_top_margin

        # set the optional collision check callback
        self.collision_check = self.collided

        # These are specific to the player object
        self.air_jumps = 0
        self.max_air_jumps = settings.player_max_air_jumps

        # Add the animations for the player
        self.animations[self.settings.anim_name_idle_left] = Animation([0, 1, 2, 3, 2, 1], 5)
        self.animations[self.settings.anim_name_idle_right] = Animation([5, 6, 7, 8, 7, 6], 5)
        self.animations[self.settings.anim_name_walk_left] = Animation([0, 10, 11, 10], 2)
        self.animations[self.settings.anim_name_walk_right] = Animation([5, 12, 13, 12], 2)
        self.animations[self.settings.anim_name_jump_up_left] = Animation([15], 5)
        self.animations[self.settings.anim_name_jump_down_left] = Animation([16], 5)
        self.animations[self.settings.anim_name_jump_up_right] = Animation([17], 5)
        self.animations[self.settings.anim_name_jump_down_right] = Animation([18], 5)
        self.current_animation = self.settings.anim_name_idle_left
        self.facing_left = True

    def update_current_animation(self):
        """Set the correct animation based on state"""
        # IDLE
        if self.dx == 0 and self.dy == 0:
            if self.facing_left:
                self.set_current_animation(self.settings.anim_name_idle_left)
            else:
                self.set_current_animation(self.settings.anim_name_idle_right)
        # WALKING
        elif self.dy == 0:
            if self.dx < 0:
                self.set_current_animation(self.settings.anim_name_walk_left)
            else:
                self.set_current_animation(self.settings.anim_name_walk_right)
        # JUMPING
        else:
            if self.dy < 0:
                if self.facing_left:
                    self.set_current_animation(self.settings.anim_name_jump_up_left)
                else:
                    self.set_current_animation(self.settings.anim_name_jump_up_right)
            else:
                if self.facing_left:
                    self.set_current_animation(self.settings.anim_name_jump_down_left)
                else:
                    self.set_current_animation(self.settings.anim_name_jump_down_right)

    def collided(self, player, block):
        """This callback is used to modify the basic collision check for the player sprite"""
        player_rect = player.rect.copy()
        # shrink the player rect based on the margins
        player_rect.height -= player.settings.player_sprite_top_margin
        player_rect.width -= (player.settings.player_sprite_horz_margin * 2)
        player_rect.midbottom = player.rect.midbottom
        # Now do a standard check with the adjusted Rect
        return player_rect.colliderect(block.rect)

    def update(self, tile_map):
        """Updates the player sprite's position"""

        # AnimatedSprite handles most of this
        super().update(tile_map)
        if self.dy == 0:
            self.air_jumps = 0

        self.finish_update()

    def handle_collision(self, collision_list, group):
        """Given a list of sprites that collide with the player, alter state such as position, velocity, etc"""
        # Even though this is a list, the first item should be all we need for now
        if collision_list:
            block = collision_list[0]

            # is this a side-collision?
            side_collision = self.rect.right > block.rect.right  or self.rect.left < block.rect.left

            # Falling is the default case, so check it first
            if self.dy > 0:
                self.falling = False
                self.falling_frames = 1
                self.air_jumps = 0
                self.dy = 0
                self.rect.bottom = block.rect.top
            # If the player is jumping, check for a lower hit
            elif self.dy < 0:
                if self.rect.bottom > block.rect.bottom:
                    self.dy = 0
                    self.rect.top = block.rect.bottom - self.settings.player_sprite_top_margin
                    # remove blocks struck from the bottom
                    group.remove(collision_list)
            # Now check the left
            elif self.dx > 0:
                if side_collision:
                    self.dx = 0
                    self.rect.right = block.rect.left + self.settings.player_sprite_horz_margin
            elif self.dx < 0:
                if side_collision:
                    self.dx = 0
                    self.rect.left = block.rect.right - self.settings.player_sprite_horz_margin

