import pygame as pg
import random
import asyncio

pg.init()

win_width = 800
win_height = 600
screen = pg.display.set_mode((win_width, win_height))
pg.display.set_caption('Celestial Harbinger')

font = pg.font.Font(None, 30)

animation = False
devmode = False  # Devmode enabled here
phase4_direction = 1
player_speed = 7  # Start normal speed low
speeding = False
speed_timer = 0

maker_health = 15
actual_health = 50
phase = 0
player_size = 40
player_pos = [win_width / 2, win_height - player_size]
player_image = pg.image.load('mario.png')
player_image = pg.transform.scale(player_image, (player_size, player_size))

obj_size = 20
obj_data = []
obj = pg.image.load('./assets/images/mario.png')
obj = pg.transform.scale(obj, (obj_size, obj_size))

enemy_size = 20
ene_data = []
enemy = pg.image.load('./assets/images/e1.png')
enemy = pg.transform.scale(enemy, (enemy_size, enemy_size))

maker_size = 60
maker = pg.image.load('./assets/images/e1.png')
maker = pg.transform.scale(maker, (maker_size, maker_size))
hittable = True
up = False
other_way = -1
weak = False
on = True

bg_image = pg.image.load('./assets/images/background.png')
bg_image = pg.transform.scale(bg_image, (win_width + 40, win_height + 40))

clock = pg.time.Clock()

spawn_delay = 200
last_spawn_time = pg.time.get_ticks()

jumping = False
jump = 0

opp_control = False

def create_object(obj_data):
    x = player_pos[0] + player_size // 2 - obj_size // 2
    y = player_pos[1] - 10
    obj_data.append([x, y, obj])

def create_enemy(ene_data, choice):
    global maker_x, maker_y
    if len(ene_data) < 10:
        x = random.randint(maker_x - 30, maker_x + 30)
        y = maker_y
        pos = random.choice(choice)
        go_left = random.choice([True, False])

        if go_left:
            for _ in range(pos):
                x += 20
                ene_data.append([x, y, enemy, 0])
        else:
            for _ in range(pos):
                x -= 20
                ene_data.append([x, y, enemy, 0])

def create_enemy2(ene_data):
    if len(ene_data) < 10 and random.random() < 0.5:
        x = random.randint(0, win_width)
        y = 1
        if random.randint(1, 5) != 1:
            ene_data.append([x, y, enemy, 0])
        else:
            ene_data.append([x, y, enemy, random.choice([-1, 1])])

def update_objects(obj_data):
    global maker_health, actual_health
    for i in range(len(obj_data) - 1, -1, -1):
        x, y, image_data = obj_data[i]
        y -= 7

        if y < 0:
            del obj_data[i]
            continue

        obj_data[i][1] = y
        screen.blit(image_data, (x, y))

        obj_rect = pg.Rect(x, y, obj_size, obj_size)
        if obj_rect.colliderect(maker_rect):
            del obj_data[i]
            if hittable:
                maker_health -= 1
                actual_health -= 1

def update_enemy(ene_data):
    for object in ene_data[:]:
        x, y, image_data, direct = object
        if y < win_height - enemy_size:
            y += 3.5
        if y >= win_height - enemy_size:
            if direct == 0:
                ene_data.remove(object)
            else:
                x += direct * 4
                object[0] = x
                if x < 0 or x > win_width:
                    ene_data.remove(object)
                screen.blit(image_data, (x, y))
        else:
            object[1] = y
            screen.blit(image_data, (x, y))

def collision_check(ene_data):
    global running
    player_rect = pg.Rect(player_pos[0], player_pos[1], player_size, player_size)
    # Check collision with enemies
    for object in ene_data:
        x, y, object_data, direct = object
        enemy_rect = pg.Rect(x, y, enemy_size, enemy_size)
        if player_rect.colliderect(enemy_rect) and phase != 0 and not devmode:
            death_text("You were hit by an enemy!")
            pg.display.flip()
            pg.time.delay(2000)
            running = False
        # Original condition for enemy touching bottom
        if y > win_height - enemy_size - 3.5:
            if phase == 0 and not devmode:  # Only trigger during phase 0
                death_text("An alien has invaded you!")
                pg.display.flip()
                pg.time.delay(2000)
                running = False
    # Check collision with maker (boss)
    if player_rect.colliderect(maker_rect) and phase != 0 and not devmode:
        death_text("You touched the boss!")
        pg.display.flip()
        pg.time.delay(2000)
        running = False

def objects_vs_enemies_collision(obj_data, ene_data):
    for obj in obj_data[:]:
        obj_rect = pg.Rect(obj[0], obj[1], obj_size, obj_size)
        for ene in ene_data[:]:
            ene_rect = pg.Rect(ene[0], ene[1], enemy_size, enemy_size)
            if obj_rect.colliderect(ene_rect):
                if obj in obj_data:
                    obj_data.remove(obj)
                if ene in ene_data:
                    ene_data.remove(ene)
                break

def death_text(text):
    death_text_render = font.render(text, True, (255, 255, 255))
    transparent_surface = pg.Surface((win_width, win_height), pg.SRCALPHA)

    pg.draw.rect(transparent_surface, (255, 0, 0, 150), (0, 0, win_width, win_height))

    text_x = win_width // 2 - death_text_render.get_width() // 2
    text_y = win_height // 2 - death_text_render.get_height() // 2
    transparent_surface.blit(death_text_render, (text_x, text_y))

    screen.blit(transparent_surface, (0, 0))

maker_x = 400
maker_y = 10
player_speed = 10
slamming = False
rep = 0
p4rep = 0
run_floor = 0

running = True

async def main():

    global running, player_pos, jumping, jump, last_spawn_time, maker_rect
    global phase, maker_health, maker_x, maker_y
    global hittable, up, slamming, direction, on, rep, run_floor

    while running:
        maker_rect = pg.Rect(maker_x, maker_y, maker_size, maker_size)

        if not animation:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    print(actual_health)
                    running = False

            keys = pg.key.get_pressed()
            if not opp_control:
                if keys[pg.K_LEFT]:
                    player_pos[0] -= player_speed
                if keys[pg.K_RIGHT]:
                    player_pos[0] += player_speed
                if keys[pg.K_UP] and not jumping:
                    jumping = True
                    jump = 15
            else:
                if keys[pg.K_LEFT]:
                    player_pos[0] += player_speed + random.randint(-5, 5)
                if keys[pg.K_RIGHT]:
                    player_pos[0] -= player_speed + random.randint(-5, 5)
                if keys[pg.K_UP] and not jumping:
                    jumping = True
                    jump = 15

            if jumping:
                player_pos[1] -= jump
                jump -= 1
            if jump <= -15:
                jump = 0
                jumping = False
                player_pos[1] = win_height - player_size

            current_time = pg.time.get_ticks()
            if current_time - last_spawn_time > spawn_delay:
                create_object(obj_data)
                if phase == 0:
                    create_enemy(ene_data, [1, 1, 1, 1, 2, 2, 2, 3, 3, 4])
                elif phase == 1:
                    create_enemy(ene_data, [0, 0, 0, 1, 1, 2])
                else:
                    create_enemy2(ene_data)
                last_spawn_time = current_time

        screen.blit(bg_image, (-10, -30))

        screen.blit(maker, (maker_x, maker_y))
        text = f"Health: {actual_health}"
        text_render = font.render(text, True, (0, 0, 0))
        pg.draw.rect(screen, (0, 0, 0), (win_width - 304, 40, 208, 28), 4)
        if actual_health < 16:
            pg.draw.rect(screen, (255, 0, 0), (win_width - 300, 44, actual_health * 4, 20))
        elif actual_health < 32:
            pg.draw.rect(screen, (255, 255, 0), (win_width - 300, 44, actual_health * 4, 20))
        else:
            pg.draw.rect(screen, (0, 255, 0), (win_width - 300, 44, actual_health * 4, 20))
        pg.draw.rect(screen, (255, 255, 255), (win_width - 300 + actual_health * 4, 44, 200 - (actual_health * 4), 20))

        # Dev mode indicator
        if devmode:
            dev_text = font.render(str(maker_health), True, (255, 0, 0))
            screen.blit(dev_text, (10, 10))

        # PHASE transitions
        if not animation:
            if maker_health <= 0:
                if phase == 0:
                    phase = 1
                    maker_health = 10
                    maker_x = 400
                    print("Phase changed to 1")
                elif phase == 1:
                    phase = 2
                    maker_health = 20
                    print("Phase changed to 2")
                elif phase == 2:
                    phase = 3
                    maker_health = 5
                    print("Phase changed to 3")
                elif phase == 3:
                    phase = 4
                    print("You totally win!")
                    maker_x = -100
                    maker_y = 540

        if phase == 1:
            if devmode:
                maker_y += 0
            else:
                maker_y += 1
                maker_x += random.randint(-2, 2) * 10
            if maker_x < 0 or maker_x > win_width:
                maker_x = random.randint(0, win_width)
            if maker_y > win_height - maker_size:
                death_text("The boss has invaded!!!!!!!")
                pg.display.flip()
                pg.time.delay(2000)
                running = False

        elif phase == 2:
            if not up:
                hittable = False
                maker_y -= 4
                if maker_y <= 50:
                    up = True
                    slamming = False
            else:
                if not slamming:
                    if abs(player_pos[0] - maker_x) > 10:
                        direction = 1 if player_pos[0] > maker_x else -1
                        maker_x += 5 * direction
                        hittable = False
                    else:
                        slamming = True
                else:
                    if devmode:
                        maker_y += 1
                    else:
                        maker_y += 35
                    hittable = True
                    if maker_y > win_height - maker_size:
                        maker_y = win_height - maker_size
                    if maker_y >= win_height - maker_size:
                        up = False

        elif phase == 3:
            hittable = False
            if maker_y > 11:
                maker_y -= 4
            else:
                maker_y = 10

                if on:
                    pg.draw.rect(screen, (255, 0, 0), (maker_x + maker_size/2, maker_y + maker_size, 10, win_height))
                    if player_pos[0] + player_size + 5 > maker_x > player_pos[0] - player_size - 5 and not devmode:
                        death_text("You were shot by a laser!")
                        pg.display.flip()
                        pg.time.delay(2000)
                        running = False

                    if random.randint(1, 100) == 1:
                        on = False
                        rep = 0
                else:
                    rep += 1
                    hittable = True
                    if rep > 100:
                        on = True
                        rep = 0

                if 100 <= maker_x <= 700:
                    maker_x += phase4_direction
                else:
                    phase4_direction *= -1
                    maker_x += phase4_direction

                if 100 <= maker_x <= 700:
                    maker_x += phase4_direction
                else:
                    phase4_direction *= -1
                    maker_x += phase4_direction
        elif phase == 4:
            maker_x += 40
            if maker_x > win_width - maker_size:
                maker_x = 0
                run_floor += 1
            if run_floor == 1:
                death_text("YOU WIN!!!!!!!")
                pg.display.flip()
                pg.time.delay(200)
                running = False

        # Player boundary
        if player_pos[0] < 0:
            player_pos[0] = 0
        elif player_pos[0] > win_width - player_size:
            player_pos[0] = win_width - player_size

        screen.blit(player_image, player_pos)

        update_objects(obj_data)
        update_enemy(ene_data)
        collision_check(ene_data)
        objects_vs_enemies_collision(obj_data, ene_data)

        pg.display.update()
        clock.tick(30)
        await asyncio.sleep(0)


    pg.quit()


asyncio.run(main())