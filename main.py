import pygame
import random

clock = pygame.time.Clock()
fps = 14  # Больший фпс требует более плавных анимаций, с большим кол-вом кадров

pygame.init()
# Разрешение, пока что очень неадаптивное
bottom_panel = 340
screen_width = 1250
screen_height = 720 + bottom_panel
# Экран
screen = pygame.display.set_mode((screen_width, screen_height))  # , flags=pygame.NOFRAME) для безрамочного режима
pygame.display.set_caption("SlayThePoor")  # Названия пока нет
# Состояние экрана, который надо отображать в данный момент
menu_state = "main"
map_state = "not_main"
battle_state = "not_main"
camp_state = "not_main"
# Переменные для боя
current_fighter = 1  # Текущий боец, порядок хода
total_fighters = 4  # Количество бойцов в игре, включая игрока
action_cooldown = 0  # Набирает порог времени для свершения действий
action_wait_time = 10  # Порог времени, после которого происходят действия; Не допускает прерывания/наслоения анимаций
potion_effect = 16  # Количество ОЗ, которое восстанавливает одно зелье
# Прочие переменные
unblock = 0  # Разблокирует уровень по индексу в списке
choice = 0  # Выбор сценария выбранного на карте
route_choice = 0  # Выбор маршрута(верхнего/нижнего) выбранного на карте
clicked = False  # Фиксирование нажатия мыши
game_over = 0  # Статус конца игры; 1:Победа, 2:Поражение
special_mark = 0  # Идёт ли бой с боссом?
play_error_sound = True  # против заедающих звуков
# Иконки
icon = pygame.image.load("images/icons/GameIcon.png")  # Для игры
pygame.display.set_icon(icon)
cursor_icon = pygame.image.load("images/icons/sword.png")  # Курсор при наведении на врага
cursor_icon = pygame.transform.scale(cursor_icon, (cursor_icon.get_width() * 0.08, cursor_icon.get_height() * 0.08))
potion_button = pygame.image.load("images/icons/potion.png")  # Зелье лечения
restart_button = pygame.image.load("images/icons/restart.png")  # Кольцевая стрелка
next_button = pygame.image.load("images/icons/next.png")
next_button2 = pygame.image.load("images/icons/next.png")    # Стрелка Далее
enemy_button = pygame.image.load("images/icons/enemy.png")  # Иконка лёгкого боя
elite_button = pygame.image.load("images/icons/elite.png")  # Иконка сложного боя
boss_button = pygame.image.load("images/icons/boss.png")  # Иконка боя с боссом
camp_button = pygame.image.load("images/icons/camp.png")
win_plus = pygame.image.load("images/icons/win+.png")
win_plus = pygame.transform.scale(win_plus, (256, 256))
dmg_button = pygame.image.load("images/icons/dmg.png")
heal_button = pygame.image.load("images/icons/heal.png")
exit_button = pygame.image.load("images/icons/exit.png")
unuse = pygame.image.load("images/icons/unuse.png")  # Иконка запрета иконки 0_0
unuse = pygame.transform.scale(unuse, (60, 60))
# Экраны
win_screen = pygame.image.load("images/icons/win.png")  # Победный
win_screen = pygame.transform.scale(win_screen, (win_screen.get_width()*1.2, win_screen.get_height()*1.2))
lose_screen = pygame.image.load("images/icons/lost.png")  # Проигрышный
stage1IMG = pygame.image.load('images/screens/stage1.png')  # Уровень 1
stage1IMG = pygame.transform.scale(stage1IMG, (stage1IMG.get_width() * 1.25, stage1IMG.get_height() * 1.25))
panelIMG = pygame.image.load('images/screens/panel.png')  # Панель действий
panelIMG = pygame.transform.scale(panelIMG, (stage1IMG.get_width(), bottom_panel))
menuIMG = pygame.image.load('images/screens/menu.png')  # Меню
mapIMG = pygame.image.load('images/screens/map.png')  # Карта уровней
endIMG = pygame.image.load('images/screens/end.jpg')
endIMG = pygame.transform.scale(endIMG, (1250, 1050))
campIMG = pygame.image.load('images/screens/camp.png')
campIMG = pygame.transform.scale(campIMG, (1250, 1050))
# Звуки
click_sfx = pygame.mixer.Sound("sounds/click.mp3")
atck_sfx = pygame.mixer.Sound("sounds/atck.mp3")
death_sfx = pygame.mixer.Sound("sounds/death.mp3")
dmpUP_sfx = pygame.mixer.Sound("sounds/dmgUP.mp3")
heal_sfx = pygame.mixer.Sound("sounds/heal.mp3")
hit_sfx = pygame.mixer.Sound("sounds/hit.mp3")
battle_end_sfx = pygame.mixer.Sound("sounds/battle_end.mp3")
background_sfx = pygame.mixer.Sound("sounds/background.mp3")
final_sfx = pygame.mixer.Sound("sounds/final.mp3")
# Шрифты
game_font = pygame.font.Font("Fonts/FFFFORWA.TTF", 17)  # Пока только этот
# Цвета
red = (255, 0, 0)
green = (0, 255, 0)
white = (250, 251, 252)
golden = (209, 196, 130)
black = (0, 0, 0)


def draw_text(text, font, text_color, x, y):  # Вывод текста
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_bg(x):  # Вывод экранных изображений
    screen.blit(x, (0, 0))


def draw_panel(x):  # Вывод панели действий, а также имён и ОЗ бойцов
    screen.blit(x, (0, screen_height - bottom_panel))
    # Параметры игрока
    #draw_text(f'{knight.name} HP: {knight.hp}', game_font, white, 180, 640)



class Fighter():  # Класс бойца
    def __init__(self, x, y, name, max_hp, dmg, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.dmg = dmg
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # Тип анимации; 0:idle, 1:attack, 2:hurt, 3:heal, 4:dead, 5:static
        self.update_time = pygame.time.get_ticks()
        # Загрузка кадров анимации простаивания
        temp_list = []
        for i in range(5):
            img = pygame.image.load(f'images/{self.name}/idle/idle{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # Загрузка анимации кадров атаки
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'images/{self.name}/attacks/atck{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # Загрузка кадров анимации получения урона
        temp_list = []
        for i in range(2):
            img = pygame.image.load(f'images/{self.name}/hurt/hurt{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # Загрузка кадров анимации лечения
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'images/{self.name}/heal/heal{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # Загрузка кадров анимации смерти
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'images/{self.name}/dead/dead{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # Загрузка статичного кадра
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'images/{self.name}/idle/idle0.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 1
        # Обновление изображения
        self.image = self.animation_list[self.action][self.frame_index]
        # Время с прошлого обновления
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # Сброс анимации (приостановка последнего кадра в случае смерти)
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        # анимация простаивания
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        hit_sfx.play()
        # анимация повреждений
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def healing(self):
        heal_sfx.play()
        # анимация лечения
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        # Не перелечивать сверх макс ОЗ:
        hp_difference = self.max_hp - self.hp
        if hp_difference > potion_effect:
            heal_amount = potion_effect
        else:
            if hp_difference < potion_effect:
                total_difference = hp_difference
                heal_amount = total_difference
            else:
                heal_amount = hp_difference
        self.hp += heal_amount
        damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
        damage_text_group.add(damage_text)  # Вывод вылеченного ОЗ над героем

    def dead(self):
        death_sfx.play()
        # анимация смерти
        self.action = 4
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def static(self):
        # статика
        self.action = 5
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        atck_sfx.play()
        # анимация атаки
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        # нанесение урона цели
        damage = self.dmg + random.randint(-1, 2)
        target.hp -= damage
        target.hurt()
        # Проверка на добивание
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.dead()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), golden)
        damage_text_group.add(damage_text)  # вывод полученного урона над целью атаки

    def reset(self):  # Возврат ключевых параметров класса "Боец" к нач. значениям
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def player_reset(self):  # Возврат не всех параметров игрока, для перехода от уровня к уровню
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):  # Вывод коллизии и картинки бойца
        screen.blit(self.image, self.rect)


class HealthBar():  # Шкала ОЗ
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):  # Вывод
        # hp update
        self.hp = hp
        ratio = self.hp / self.max_hp
        if self.hp < 1 or self.hp == 0:
            pass  # Убрать к. полосу в момент смерти
        else:
            draw_text(f'{self.hp}/{self.max_hp}', game_font, white, self.x+45, self.y + 30)
            pygame.draw.rect(screen, black, (self.x-2, self.y-2, 154, 19))  # Чёрная обводка
            pygame.draw.rect(screen, red, (self.x, self.y, 150, 15))  # Красная полоса - сколько ОЗ потеряно
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 15))  # Зелёная - сколько осталось, убывает


class DamageText(pygame.sprite.Sprite):  # Спрайт цифр урона/лечения
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = game_font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y - 20)
        self.counter = 0

    def update(self):
        self.rect.y -= 8  # взлёт цифр вверх
        self.counter += 1
        if self.counter > 12:
            self.kill()  # удаление при достижении определённой высоты


damage_text_group = pygame.sprite.Group()
# Статы бойцов
knight = Fighter(250, 470, 'Knight', 42, 7, 3)
enemy1 = Fighter(800, 470, 'Enemy', 18, 4, 0)
enemy2 = Fighter(1000, 470, 'Enemy', 18, 4, 0)
enemy3 = Fighter(900, 470, 'boss', 40, 7, 0)
# Список врагов
enemy_list = []
enemy_list.append(enemy1)
enemy_list.append(enemy2)
enemy_list.append(enemy3)
# Места отображения полосок ОЗ
knight_hp_bar = HealthBar(180, 610, knight.hp, knight.max_hp)
enemy1_hp_bar = HealthBar(720, 610, enemy1.hp, enemy1.max_hp)
enemy2_hp_bar = HealthBar(920, 610, enemy2.hp, enemy2.max_hp)
enemy3_hp_bar = HealthBar(820, 610, enemy3.hp, enemy3.max_hp)


# Класс кнопок
class Button():
    def __init__(self, surface, x, y, image, size_x, size_y, type, usable):
        self.image = pygame.transform.scale(image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.surface = surface
        self.type = type
        self.usable = usable
        self.size_x = size_x
        self.size_y = size_y


    def draw(self):
        action = False

        # Получение позиции мыши

        pos = pygame.mouse.get_pos()

        # проверка на наличие курсора и клика
        if self.rect.collidepoint(pos) and self.usable is True:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Отрисовка кнопки
        self.surface.blit(self.image, (self.rect.x, self.rect.y))
        if not self.usable:
            self.surface.blit(unuse, (self.rect.x, self.rect.y))
        return action


# Кнопки; где их отображать, их размер
skill_button = Button(screen, 100, screen_height - bottom_panel + 30, potion_button, 96, 96, 'skill', True)
exit_button = Button(screen, 350, 590, exit_button, 140, 140, 'exit', True)
restart_button = Button(screen, 564, 620, restart_button, 140, 140, 'restart', True)
next_button = Button(screen, 550, 560, next_button, 140, 140, 'next', True)
next_button2 = Button(screen, 520, 440, next_button2, 140, 140, 'next', True)
heal_button = Button(screen, 400, 330, heal_button, 140, 140, 'heal', True)
dmg_button = Button(screen, 700, 330, dmg_button, 140, 140, 'dmg', True)
# Кнопки наполняющие карту
boss_button = Button(screen, 1100, 290, boss_button, 60, 60, 'boss', False)

level_buttons = []
level_buttons1 = []
i = 0
while i != 12:
    rand = random.randint(0, 100)
    if i < 6:
        if rand in range(90, 100):
            x = Button(screen, 165 * (1 + i), 165, elite_button, 60, 60, 'elite', True)
            level_buttons.append(x)
        elif rand in range(80, 89):
            x = Button(screen, 165 * (1 + i), 165, camp_button, 60, 60, 'camp', True)
            level_buttons.append(x)
        else:
            x = Button(screen, 165 * (1 + i), 165, enemy_button, 60, 60, 'enemy', True)
            level_buttons.append(x)
    else:
        if rand in range(90, 100):
            x = Button(screen, 164 * (-5 + i), 415, elite_button, 60, 60, 'elite', True)
            level_buttons1.append(x)
        elif rand in range(80, 89):
            x = Button(screen, 165 * (-5 + i), 415, camp_button, 60, 60, 'camp', True)
            level_buttons1.append(x)
        else:
            x = Button(screen, 164 * (-5 + i), 415, enemy_button, 60, 60, 'enemy', True)
            level_buttons1.append(x)
    i += 1

temp = 0  # Одноразовая переменная для выбора маршрута


background_sfx.play(-1).set_volume(1)




# Игровой цикл
running = True
while running:
    screen.fill(black)
    # Интерфейс
    # # Меню
    if menu_state == 'main':
        draw_bg(menuIMG)  # Раздел меню
        if next_button2.draw():  # При нажатии заставляет отображать экран карты, а не меню
            menu_state = 'not_main'
            map_state = 'main'
            draw_bg(mapIMG)
        if exit_button.draw():
            running = False

    if camp_state == 'main':
        draw_bg(campIMG)
        heal_button.usable = True
        dmg_button.usable = True
        draw_text(f'HP: {knight.hp}/{knight.max_hp}', game_font, white, 200, 780)
        draw_text(f'Potions: {knight.potions}', game_font, white, 200, 820)
        draw_text(f'DMG: {knight.dmg-1}~{knight.dmg+2}', game_font, white, 200, 860)
        draw_text(f'DMG + 2', game_font, white, 700, 480)
        draw_text(f'Heal', game_font, white, 410, 480)
        draw_text(f'MaxHP + 8', game_font, white, 410, 510)
        if heal_button.draw():
            heal_button.usable = False
            dmg_button.usable = False
            knight.max_hp += 8
            knight_hp_bar = HealthBar(180, 610, knight.hp, knight.max_hp)
            knight.healing()
            knight.potions += 1
            knight.player_reset()
            for enemy in enemy_list:
                enemy.reset()
            unblock += 1
            current_fighter = 1
            action_cooldown = 0
            camp_state = 'not_main'
            map_state = 'main'
            game_over = 0
        if dmg_button.draw():
            heal_button.usable = False
            dmg_button.usable = False
            dmpUP_sfx.play()
            knight.dmg += 2
            knight.player_reset()
            for enemy in enemy_list:
                enemy.reset()
            unblock += 1
            current_fighter = 1
            action_cooldown = 0
            camp_state = 'not_main'
            map_state = 'main'
            game_over = 0

    if map_state == 'main':
        play_error_sound = True
        draw_bg(mapIMG)  # Раздел карты уровней
        draw_text(f'HP: {knight.hp}/{knight.max_hp}', game_font, black, 200, 800)
        draw_text(f'Potions: {knight.potions}', game_font, black, 200, 840)
        draw_text(f'DMG: {knight.dmg - 1}~{knight.dmg + 2}', game_font, black, 200, 880)
        if unblock == 6:
            boss_button.usable = True
            for i in range(0, len(level_buttons)):
                level_buttons[i].usable = False
                level_buttons1[i].usable = False
                level_buttons[i].draw()
                level_buttons1[i].draw()
            if boss_button.draw():
                map_state = 'not_main'
                battle_state = 'main'
                choice = 3
                special_mark = 1
        else:
            boss_button.draw()
            for i in range(0, len(level_buttons)):
                level_buttons[i].usable = False
            level_buttons[unblock].usable = True
            if route_choice == 2:  # Выбор маршрута
                level_buttons[unblock].usable = False
            for i in range(0, len(level_buttons)):
                if level_buttons[i].draw():  # При нажатии заставляет отображать экран выбранного боя, а не карту
                    if level_buttons[i].type == 'elite':
                        choice = 2
                        map_state = 'not_main'
                        battle_state = 'main'
                        route_choice = 1
                        temp = 1
                    elif level_buttons[i].type == 'camp':
                        map_state = 'not_main'
                        camp_state = 'main'
                    else:
                        choice = 1
                        map_state = 'not_main'
                        battle_state = 'main'
                        route_choice = 1
                        temp = 1
            for i in range(0, len(level_buttons1)):
                level_buttons1[i].usable = False
            level_buttons1[unblock].usable = True
            if route_choice == 1:  # Выбор маршрута
                level_buttons1[unblock].usable = False
            for i in range(0, len(level_buttons1)):
                if level_buttons1[i].draw():  # При нажатии заставляет отображать экран выбранного боя, а не карту
                    if level_buttons1[i].type == 'elite':
                        choice = 2
                        map_state = 'not_main'
                        battle_state = 'main'
                        route_choice = 2
                        temp = 1
                    elif level_buttons1[i].type == 'camp':
                        map_state = 'not_main'
                        camp_state = 'main'
                    else:
                        choice = 1
                        map_state = 'not_main'
                        battle_state = 'main'
                        route_choice = 2
                        temp = 1

    # Боёвка
    if battle_state == 'main':
        if choice == 1:
            draw_bg(stage1IMG)
            draw_panel(panelIMG)
            # Создание бойцов
            knight.update()
            knight.draw()
            enemy2.update()
            enemy2.draw()
            enemy1.alive = False
            enemy3.alive = False
            knight_hp_bar.draw(knight.hp)
            enemy2_hp_bar.draw(enemy2.hp)
        elif choice == 2:
            draw_bg(stage1IMG)
            draw_panel(panelIMG)

            knight.update()
            knight.draw()
            enemy3.alive = False
            enemy1.update()
            enemy1.draw()
            enemy2.update()
            enemy2.draw()

            knight_hp_bar.draw(knight.hp)
            enemy1_hp_bar.draw(enemy1.hp)
            enemy2_hp_bar.draw(enemy2.hp)
        elif choice == 3:
            draw_bg(stage1IMG)
            draw_panel(panelIMG)
            if play_error_sound:
                play_error_sound = False
                background_sfx.stop()
                final_sfx.play(-1).set_volume(0.2)
            knight.update()
            knight.draw()
            enemy1.alive = False
            enemy2.alive = False
            enemy3.update()
            enemy3.draw()

            knight_hp_bar.draw(knight.hp)
            enemy3_hp_bar.draw(enemy3.hp)

        # Полученный урон
        damage_text_group.update()
        damage_text_group.draw(screen)

        # Параметры Игрока перед боем
        attack = False
        effect = False
        target = None
        pos = pygame.mouse.get_pos()
        pygame.mouse.set_visible(True)
        for count, enemy in enumerate(enemy_list):
            if enemy.rect.collidepoint(pos):
                # Подмена иконки курсора
                pygame.mouse.set_visible(False)
                screen.blit(cursor_icon, pos)
                if clicked is True and enemy.alive is True:
                    attack = True  # Клик по врагу
                    target = enemy_list[count]
        if skill_button.draw():
            effect = True  # Активация зелья
        # Кол-во зелий
        draw_text(str(knight.potions), game_font, white, 168, screen_height - bottom_panel + 100)

        if game_over == 0:
            # Действия игрока
            if knight.alive is True:
                if current_fighter == 1:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        # Атака
                        if attack is True and target is not None:
                            knight.attack(target)
                            current_fighter += 1
                            action_cooldown = 0
                        # Лечение
                        if effect is True:
                            if knight.potions > 0:
                                ###
                                knight.healing()
                                knight.potions -= 1
                                current_fighter += 1
                            action_cooldown = 0

            else:
                game_over = -1  # Гибель игрока = конец игры

            # Действия врагов
            for count, enemy in enumerate(enemy_list):
                if current_fighter == 2 + count:
                    if enemy.alive is True:
                        action_cooldown += 1
                        if action_cooldown >= action_wait_time:
                            enemy.attack(knight)
                            current_fighter += 1
                            action_cooldown = 0
                            if enemy is enemy3:
                                enemy3.dmg += 1
                    else:
                        current_fighter += 1

            # После всех ходов
            if current_fighter > total_fighters:
                current_fighter = 1

        alive_enemies = 0  # Кол-во живых врагов
        for enemy in enemy_list:
            if enemy.alive is True:
                alive_enemies += 1  # Не даёт параметру стать равным нулю, пока враги живы
        if alive_enemies == 0:
            game_over = 1  # Победный экран
            knight.static()  # Остановка анимации

        # game over check
        if game_over != 0:
            if game_over == 1:
                screen.blit(win_screen, (450, 225))
                if special_mark == 1:
                    final_sfx.stop()
                    screen.blit(endIMG, (0, 0))
                    screen.blit(win_plus, (940, 520))
                    if restart_button.draw():
                        background_sfx.play()
                        knight.reset()
                        for enemy in enemy_list:
                            enemy.reset()
                        unblock += 1
                        current_fighter = 1
                        action_cooldown = 0
                        unblock = 0
                        route_choice = 0
                        game_over = 0
                        special_mark = 0
                        battle_state = 'not_main'
                        menu_state = 'main'
                        choice = 0
                else:
                    if next_button.draw():
                        knight.player_reset()
                        for enemy in enemy_list:
                            enemy.reset()
                        unblock += 1
                        current_fighter = 1
                        action_cooldown = 0
                        battle_state = 'not_main'
                        map_state = 'main'
                        game_over = 0
                        choice = 0

            else:
                screen.blit(endIMG, (0, 0))
                screen.blit(lose_screen, (140, 520))
                for enemy in enemy_list:
                    if enemy.alive is True:
                        enemy.static()
                if restart_button.draw():
                    click_sfx.play()
                    knight.reset()
                    for enemy in enemy_list:
                        enemy.reset()
                    unblock += 1
                    current_fighter = 1
                    action_cooldown = 0
                    if game_over == 1 and special_mark == 0:
                        battle_state = 'not_main'
                        map_state = 'main'
                    elif game_over == -1 or special_mark == 1:
                        battle_state = 'not_main'
                        menu_state = 'main'
                        unblock = 0
                        route_choice = 0
                    game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_sfx.play()
            clicked = True
        else:
            clicked = False

    pygame.display.update()

    clock.tick(fps)

pygame.quit()
