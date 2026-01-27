import pygame

import game
import draw
import save
import gui
import audio
from globals import Globals

from utils import *

class App:
    def run(self):
        self.slot = -1
        self.running = True

        dragging = False
        last_mouse_pos = Vec(0, 0)

        self.map = game.Map(self.slot)
        clock = pygame.time.Clock()

        self.menu = self.create_menu()
        self.bar = self.create_bar()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in [1, 2, 3]:
                        audio.play_sound(Globals.sound_click)
                        if event.button == 2:
                            dragging = True
                            last_mouse_pos = Vec(*event.pos)
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = Vec(*event.pos)
                    if event.button in [1, 2, 3]:
                        audio.play_sound(Globals.sound_unclick)
                        if event.button in [1, 3]:
                            if (not(mouse_pos.in_rect(Vec(0, 0), Vec(1000, 1000)))):
                                continue

                            if self.menu.click(mouse_pos, True) is not None:
                                continue
                            if self.bar.click(mouse_pos, True) is not None:
                                continue

                            global_pos = self.map.camera.reverse_transform(mouse_pos).floor()

                            if event.button == 1:
                                opened = self.map.open_cell(global_pos)
                                if (opened):
                                    audio.play_sound(Globals.sound_open)
                            else:
                                self.map.flag_cell(global_pos)

                        elif event.button == 2:
                            dragging = False

                elif event.type == pygame.MOUSEWHEEL:
                    if self.slot != -1:
                        self.map.camera.zoom = max(
                            8.0,
                            min(64.0, self.map.camera.zoom + event.y),
                        )

                elif event.type == pygame.QUIT:
                    self.map.save()
                    self.running = False

            current_mouse_pos = Vec(*pygame.mouse.get_pos())

            pointer = True
            menu_pointer = self.menu.click(current_mouse_pos, False)
            bar_pointer = self.bar.click(current_mouse_pos, False)

            if menu_pointer is not None:
                pointer = menu_pointer
            if bar_pointer is not None:
                pointer = bar_pointer

            pygame.mouse.set_cursor(
                pygame.SYSTEM_CURSOR_HAND if pointer else pygame.SYSTEM_CURSOR_ARROW
            )

            if dragging:
                delta = current_mouse_pos - last_mouse_pos

                self.map.camera.pos.x -= delta.x / self.map.camera.zoom
                self.map.camera.pos.y -= delta.y / self.map.camera.zoom

                last_mouse_pos = current_mouse_pos

            self.map.update()

            draw.clear_screen((101, 119, 128))
            self.map.draw()
            self.menu.draw()
            self.bar.draw()
            pygame.display.update()

            clock.tick(30)

    def start_slot(self, slot):
        self.slot = slot
        self.map = game.Map.load(slot, True)
        self.menu.active = False
        self.bar.active = True

    def delete_slot(self, slot):
        save.delete_save(slot)
        self.menu = self.create_menu()

    def toggle_dark_mode(self):
        Globals.dark_mode = not Globals.dark_mode
        self.menu = self.create_menu()

    def quit(self):
        self.running = False

    def back(self):
        self.map.save()
        self.slot = -1
        self.map = game.Map(self.slot)
        self.menu = self.create_menu()
        self.bar.active = False

    def create_menu(self):
        existing_slots = []

        for i in range(3):
            map = game.Map.load(i, False)
            if map is not None:
                existing_slots.append(i)

        def _renderer(menu, existing_slots):
            draw.draw_fade((0, 0, 0, 127))

            logo_sway = math.sin(pygame.time.get_ticks() * 0.002) * 8
            menu.draw_ui(Vec(99, 23 + logo_sway), Vec(0, 336), Vec(302, 102))
            menu.draw_ui(Vec(130, 138), Vec(0, 112), Vec(240, 224))

            for i in range(3):
                y = 150 + (i * 48)

                menu.draw_ui(Vec(142, y), Vec(12, 60), Vec(216, 40))

                if i in existing_slots:
                    menu.draw_ui(Vec(265, y + 7), Vec(240, 0), Vec(7, 27))
                    draw.draw_rect(
                        None,
                        Vec(249, y + 4),
                        Vec(2, 33),
                        (30, 39, 44) if Globals.dark_mode else (106, 124, 148),
                    )

        menu = gui.Menu(
            self,
            lambda menu, es=existing_slots: _renderer(menu, es),
            Vec(0, 0),
            Vec(500, 500),
        )

        for i in range(3):
            map = game.Map.load(i, False)
            exists = map is not None
            y = 154 + (i * 48)

            menu.add_button(
                gui.Button(
                    Vec(146, y),
                    Vec(0 if exists else 48, 0),
                    Vec(34, 34),
                    lambda slot=i: self.start_slot(slot),
                )
            )

            if exists:
                menu.add_button(
                    gui.Button(
                        Vec(322, y),
                        Vec(96, 0),
                        Vec(34, 34),
                        lambda slot=i: self.delete_slot(slot),
                    )
                )

                menu.add_label(
                    gui.Label(
                        Vec(194, y + 4),
                        f"SLOT {i + 1}",
                        (0, 0, 0) if Globals.dark_mode else (255, 255, 255),
                        Globals.font_big,
                    )
                )

                menu.add_label(
                    gui.Label(
                        Vec(200, y + 13),
                        map.get_formated_playtime(),
                        (30, 39, 44)
                        if Globals.dark_mode
                        else (106, 124, 148),
                        Globals.font_small,
                    )
                )

                menu.add_label(
                    gui.Label(
                        Vec(199, y + 22),
                        f"{map.get_score():08d}",
                        (30, 39, 44)
                        if Globals.dark_mode
                        else (106, 124, 148),
                        Globals.font_small,
                    )
                )

                menu.add_label(
                    gui.Label(
                        Vec(276, y + 2),
                        f"{map.flags_placed:08d}",
                        (0, 0, 0) if Globals.dark_mode else (255, 255, 255),
                        Globals.font_small,
                    )
                )

                menu.add_label(
                    gui.Label(
                        Vec(276, y + 12),
                        f"{map.cells_opened:08d}",
                        (0, 0, 0) if Globals.dark_mode else (255, 255, 255),
                        Globals.font_small,
                    )
                )

                menu.add_label(
                    gui.Label(
                        Vec(276, y + 22),
                        f"{map.bombs_exploded:08d}",
                        (0, 0, 0) if Globals.dark_mode else (255, 255, 255),
                        Globals.font_small,
                    )
                )
            else:
                menu.add_label(
                    gui.Label(
                        Vec(216, y + 13),
                        "NEW GAME",
                        (30, 39, 44) if Globals.dark_mode else (106, 124, 148),
                        Globals.font_big,
                    )
                )

        menu.add_button(gui.Button(Vec(146, 314), Vec(144, 0), Vec(34, 34), self.quit))
        menu.add_button(gui.Button(Vec(234, 314), Vec(240, 64), Vec(34, 34), lambda slot=-2: self.start_slot(slot)))
        menu.add_button(
            gui.Button(Vec(322, 314), Vec(192, 0), Vec(34, 34), self.toggle_dark_mode)
        )

        menu.add_label(
            gui.Label(
                Vec(132, 366),
                f"game by Violunae",
                (255, 255, 255),
                Globals.font_big,
            )
        )

        return menu

    def create_bar(self):
        def _renderer(bar):
            fg = (0, 0, 0) if Globals.dark_mode else (255, 255, 255)
            bg = (255, 255, 255) if Globals.dark_mode else (0, 0, 0)

            draw.draw_rect(None, Vec(0, 0), Vec(500, 11), bg)

            draw.draw_text(Vec(20, 2), "BACK", fg, Globals.font_big)
            draw.draw_text(
                Vec(58, 1),
                bar.app.map.get_formated_playtime(),
                fg,
                Globals.font_small,
            )
            draw.draw_text(
                Vec(235, 1),
                f"{bar.app.map.get_score():08d}",
                fg,
                Globals.font_small,
            )

            bar.draw_ui(Vec(359, 1), Vec(240, 30), Vec(9, 9))
            bar.draw_ui(Vec(360, 2), Vec(240, 0), Vec(7, 7))
            draw.draw_text(
                Vec(372, 1),
                f"{bar.app.map.flags_placed:08d}",
                fg,
                Globals.font_small,
            )

            bar.draw_ui(Vec(407, 1), Vec(240, 30), Vec(9, 9))
            bar.draw_ui(Vec(408, 2), Vec(240, 10), Vec(7, 7))
            draw.draw_text(
                Vec(419, 1),
                f"{bar.app.map.cells_opened:08d}",
                fg,
                Globals.font_small,
            )

            bar.draw_ui(Vec(455, 1), Vec(240, 30), Vec(9, 9))
            bar.draw_ui(Vec(456, 2), Vec(240, 20), Vec(7, 7))
            draw.draw_text(
                Vec(468, 1),
                f"{bar.app.map.bombs_exploded:08d}",
                fg,
                Globals.font_small,
            )

        bar = gui.Menu(self, _renderer, Vec(0, 0), Vec(500, 11), False)
        bar.add_button(gui.Button(Vec(1, 1), Vec(240, 48), Vec(18, 9), self.back))

        return bar