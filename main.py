import pygame

clock = pygame.time.Clock()
fps = 10  # Больший фпс требует более плавных анимаций, с большим кол-вом кадров

pygame.init()
# Разрешение, пока что очень неадаптивное
bottom_panel = 340
screen_width = 1250
screen_height = 720 + bottom_panel
# Экран
screen = pygame.display.set_mode((screen_width, screen_height))  # , flags=pygame.NOFRAME) для безрамочного режима
pygame.display.set_caption("TestGame")  # Названия пока нет
# Состояние экрана, который надо отображать в данный момент
menu_state = "main"
map_state = "not_main"
battle_state = "not_main"
# Переменные для боя
current_fighter = 1  # Текущий боец, порядок хода
total_fighters = 3  # Количество бойцов в принципе, включая игрока
action_cooldown = 0  # Набирает порог времени для свершения действий
action_wait_time = 6  # Порог времени, после которого происходят действия; Не допускает прерывания/наслоения анимаций
potion_effect = 5  # Количество ОЗ, которое восстанавливает одно зелье
# Прочие переменные
choice = 0  # Выбор
clicked = False  # Фиксирование нажатия мыши
game_over = 0  # Статус конца игры; 1:Победа, 2:Поражение
# Иконки
icon = pygame.image.load("images/icons/GameIcon.png")  # Для игры
pygame.display.set_icon(icon)
cursor_icon = pygame.image.load("images/icons/sword.png")  # Курсор при наведении на врага
cursor_icon = pygame.transform.scale(cursor_icon, (cursor_icon.get_width() * 0.08, cursor_icon.get_height() * 0.08))
potion_button = pygame.image.load("images/icons/potion.png")  # Зелье лечения
restart_button = pygame.image.load("images/icons/restart.png")  # Кольцевая стрелка
next_button = pygame.image.load("images/icons/next.png")  # Стрелка Далее
enemy_button = pygame.image.load("images/icons/enemy.png")  # Иконка лёгкого боя
elite_button = pygame.image.load("images/icons/elite.png")  # Иконка сложного боя
# Экраны
win_screen = pygame.image.load("images/icons/win.png")  # Победный
lose_screen = pygame.image.load("images/icons/lost.png")  # Проигрышный
stage1IMG = pygame.image.load('images/screens/stage1.png')  # Уровень 1
stage1IMG = pygame.transform.scale(stage1IMG, (stage1IMG.get_width() * 1.25, stage1IMG.get_height() * 1.25))
panelIMG = pygame.image.load('images/screens/panel.png')  # Панель действий
panelIMG = pygame.transform.scale(panelIMG, (stage1IMG.get_width(), bottom_panel))
menuIMG = pygame.image.load('images/screens/menu.png')  # Меню
mapIMG = pygame.image.load('images/screens/map.png')  # Карта уровней, очень сырая
# Шрифты
font = pygame.font.Font("Fonts/FFFFORWA.TTF", 17)  # Пока только этот
# Цвета
red = (255, 0, 0)
green = (0, 255, 0)
white = (250, 251, 252)
golden = (209, 196, 130)


def draw_text(text, font, text_color, x, y):  # Вывод текста
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_bg(x):  # Вывод экранных изображений
    screen.blit(x, (0, 0))


def draw_panel(x):  # Вывод панели действий
    screen.blit(x, (0, screen_height - bottom_panel))
    # Параметры игрока
    draw_text(f'{knight.name} HP: {knight.hp}', font, white, 180, 670)
    # Параметры врагов
    for count, i in enumerate(enemy_list):
        if i.alive == True:
            # for count, (i) in enumerate(enemy_list):
            draw_text(f'{i.name} HP: {i.hp}', font, red, 720+count*200, 670)


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
        for i in range(3):
            img = pygame.image.load(f'images/{self.name}/idle/idle{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # Загрузка анимации кадров атаки
        temp_list = []
        for i in range(2):
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
        for i in range(2):
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
        # анимация повреждений
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def healing(self):
        # анимация лечения
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        # Процесс лечения
        self.hp += heal_amount
        damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
        damage_text_group.add(damage_text)  # Вывод вылеченного ОЗ над героем

    def dead(self):
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
        # анимация атаки
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        # нанесение урона цели
        damage = self.dmg
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
            pygame.draw.rect(screen, red, (self.x, self.y, 150 * ratio, 20))  # Убрать к. полосу в момент смерти
        else:
            pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))  # Красная полоса - сколько ОЗ потеряно
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))  # Зелёная - сколько осталось, убывает


class DamageText(pygame.sprite.Sprite):  # Спрайт цифр урона/лечения
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y - 20)
        self.counter = 0

    def update(self):
        self.rect.y -= 5  # взлёт цифр вверх
        self.counter += 1
        if self.counter > 20:
            self.kill()  # удаление при достижении определённой высоты


damage_text_group = pygame.sprite.Group()
# Статы бойцов
knight = Fighter(250, 470, 'Knight', 10, 2, 5)
enemy1 = Fighter(800, 470, 'Enemy', 8, 2, 0)
enemy2 = Fighter(1000, 470, 'Enemy', 4, 1, 0)
# Список врагов
enemy_list = []
enemy_list.append(enemy1)
enemy_list.append(enemy2)
# Места отображения полосок ОЗ
knight_hp_bar = HealthBar(180, 640, knight.hp, knight.max_hp)
enemy1_hp_bar = HealthBar(720, 640, enemy1.hp, enemy1.max_hp)
enemy2_hp_bar = HealthBar(920, 640, enemy2.hp, enemy2.max_hp)


# Класс кнопок
class Button():
    def __init__(self, surface, x, y, image, size_x, size_y):
        self.image = pygame.transform.scale(image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.surface = surface


    def draw(self):
        action = False

        # Получение позиции мыши
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Отрисовка кнопки
        self.surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


# Кнопки; где их отображать, их размер
skill_button = Button(screen, 100, screen_height - bottom_panel + 30, potion_button, 96, 96)
restart_button = Button(screen, 550, 560, restart_button, 140, 140)
next_button = Button(screen, 550, 560, next_button, 140, 140)
enemy_button = Button(screen, 320, 170, enemy_button, 140, 140)
elite_button = Button(screen, 320, 660, elite_button, 140, 140)
# Игровой цикл
running = True
while running:
    # Интерфейс
    # # Меню
    if menu_state == 'main':
        draw_bg(menuIMG)  # Раздел меню
        if next_button.draw():  # При нажатии заставляет отображать экран карты, а не меню
            menu_state = 'not_main'
            map_state = 'main'
            draw_bg(mapIMG)
            # destination choice
            # the choice enemy
    if map_state == 'main':
        draw_bg(mapIMG)  # Раздел карты уровней
        if enemy_button.draw():  # При нажатии заставляет отображать экран выбранного боя, а не карту
            map_state = 'not_main'
            battle_state = 'main'
            choice = 1   # Выбор уровня
        elif elite_button.draw():
            map_state = 'not_main'
            battle_state = 'main'
            choice = 2

    # Боёвка
    # # !!! Надо реализовать рандомную генерацию карты и наборов врагов, а также переход от уровня к уровню!!!
    if battle_state == 'main':
        if choice == 1:
            draw_bg(stage1IMG)
            # Создание бойцов
            knight.update()
            knight.draw()
            enemy2.update()
            enemy2.draw()
            enemy1.alive = False
            draw_panel(panelIMG)
            knight_hp_bar.draw(knight.hp)
            enemy2_hp_bar.draw(enemy2.hp)
        elif choice == 2:
            draw_bg(stage1IMG)
            draw_panel(panelIMG)
            knight_hp_bar.draw(knight.hp)
            enemy1_hp_bar.draw(enemy1.hp)
            enemy2_hp_bar.draw(enemy2.hp)
            # Создание бойцов
            knight.update()
            knight.draw()
            for enemy in enemy_list:
                enemy.update()
                enemy.draw()
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
                if clicked == True and enemy.alive == True:
                    attack = True  # Клик по врагу
                    target = enemy_list[count]
        if skill_button.draw():
            effect = True  # Активация зелья
        # Кол-во зелий
        draw_text(str(knight.potions), font, white, 168, screen_height - bottom_panel + 100)

        if game_over == 0:
            # Действия игрока
            if knight.alive == True:
                if current_fighter == 1:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        # Атака
                        if attack == True and target != None:
                            knight.attack(target)
                            current_fighter += 1
                            action_cooldown = 0
                        # Лечение
                        if effect == True:
                            if knight.potions > 0:
                                # Не перелечивать сверх макс ОЗ:
                                hp_difference = knight.max_hp - knight.hp
                                if hp_difference > potion_effect:
                                    heal_amount = potion_effect
                                else:
                                    if hp_difference < potion_effect:
                                        total_difference = hp_difference
                                        heal_amount = total_difference
                                    else:
                                        heal_amount = hp_difference
                                knight.healing()
                                knight.potions -= 1
                                current_fighter += 1
                            action_cooldown = 0

            else:
                game_over = -1  # Гибель игрока = конец игры

            # Действия врагов
            for count, enemy in enumerate(enemy_list):
                if current_fighter == 2 + count:
                    if enemy.alive == True:
                        action_cooldown += 1
                        if action_cooldown >= action_wait_time:
                            enemy.attack(knight)
                            current_fighter += 1
                            action_cooldown = 0
                    else:
                        current_fighter += 1

            # После всех ходов
            if current_fighter > total_fighters:
                current_fighter = 1

        alive_enemies = 0  # Кол-во живых врагов
        for enemy in enemy_list:
            if enemy.alive == True:
                alive_enemies += 1  # Не даёт параметру стать равным нулю, пока враги живы
        if alive_enemies == 0:
            game_over = 1  # Победный экран
            knight.static()  # Остановка анимации

        # game over check
        if game_over != 0:
            if game_over == 1:
                screen.blit(win_screen, (490, 300))
            else:
                screen.blit(lose_screen, (490, 300))
                for enemy in enemy_list:
                    if enemy.alive == True:
                        enemy.static()
            if restart_button.draw():
                knight.reset()
                for enemy in enemy_list:
                    enemy.reset()
                current_fighter = 1
                action_cooldown = 0
                game_over = 0
                battle_state = 'not_main'
                map_state = 'main'

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

    clock.tick(fps)

pygame.quit()
