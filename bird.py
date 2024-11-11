# 이것은 각 상태들을 객체로 구현한 것임.

from pico2d import get_time, load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, load_font
from state_machine import *
from ball import Ball
import game_world
import game_framework

# Boy Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Boy Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 14

BIRD_WIDTH = 100
BIRD_HEIGHT = 100


class Idle:
    @staticmethod
    def enter(bird, e):
        if start_event(e):
            bird.action = 3
            bird.face_dir = 1
        elif right_down(e) or left_up(e):
            bird.action = 2
            bird.face_dir = -1
        elif left_down(e) or right_up(e):
            bird.action = 3
            bird.face_dir = 1

        bird.frame = 0
        bird.wait_time = get_time()

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        if get_time() - bird.wait_time > 2:
            bird.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(bird):
        if bird.face_dir == -1:
            bird.image.clip_draw(int(bird.frame) * 100, bird.action * 100, 100, 100, bird.x, bird.y)
        else:
            bird.image.clip_composite_draw(int(bird.frame) * 100, bird.action * 100, 100, 0, 'h', 100, bird.x, bird.y)
class Sleep:
    @staticmethod
    def enter(boy, e):
        if start_event(e):
            boy.face_dir = 1
            boy.action = 3
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8


    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(int(boy.frame) * 100, 300, 100, 100,
                                          3.141592 / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(int(boy.frame) * 100, 200, 100, 100,
                                          -3.141592 / 2, '', boy.x + 25, boy.y - 25, 100, 100)

class Run:
    @staticmethod
    def enter(bird, e):
        # if right_down(e) or left_up(e): # 오른쪽으로 RUN
        #     bird.dir, bird.face_dir, bird.action = 1, 1, 1
        # elif left_down(e) or right_up(e): # 왼쪽으로 RUN
        bird.dir, bird.face_dir, bird.action = -1, -1, 2

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()


    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 14
        if int(bird.frame) == 0:
            bird.action = 2
        if int(bird.frame) == 5:
            bird.action = 1
        if int(bird.frame) == 10:
            bird.action = 0

        if bird.x < 100:
            bird.dir, bird.face_dir = 1, 1
        elif bird.x > 1500:
            bird.dir, bird.face_dir = -1, -1
        bird.x += bird.dir * RUN_SPEED_PPS * game_framework.frame_time


    @staticmethod
    def draw(bird):
        if bird.face_dir == 1:
            bird.image.clip_draw(int(bird.frame)%5 * 183, bird.action * 168, 183, 168, bird.x, bird.y, BIRD_WIDTH, BIRD_HEIGHT)
        else:
            bird.image.clip_composite_draw(int(bird.frame)%5 * 183, bird.action * 168, 183, 168, 0, 'h', bird.x, bird.y, BIRD_WIDTH, BIRD_HEIGHT)


class Bird:

    def __init__(self):
        self.x, self.y = 400, 90
        self.face_dir = 1
        self.frame = 0
        self.image = load_image('bird_animation.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start(Run)
        self.state_machine.set_transitions(
            {
                Run: {}
            }
        )
        self.font = load_font('ENCR10B.TTF', 16)

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # 여기서 받을 수 있는 것만 걸러야 함. right left  등등..
        self.state_machine.add_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.x - 60, self.y + 50, f'(Time: {get_time():.2f})', (255, 255, 0))

    # def fire_ball(self):
    #     ball = Ball(self.x, self.y, self.face_dir * 10)
    #     game_world.add_object(ball)