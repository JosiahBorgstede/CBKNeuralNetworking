import pygame
import random
import math

import torch

class PygameObject:
	def update(self, rate, bounds):
		pass
	def draw(self, screen):
		screen.blit(self.surface, (self.x, self.y))

class Paddle(PygameObject):
	def __init__(self, x, y, v_y, width=20, height=100, color=(255,255,255)):
		self.x = x
		self.y = y - height/2
		self.v_y = v_y
		self.width = width
		self.height = height
		self.color = color

		self.dir = 0

		self.surface = pygame.Surface((width, height))
		self.surface.fill(color)
		self.surface = self.surface.convert()

	def update(self, rate, bounds, dirMove = 0):
		self.y += self.v_y*rate*dirMove
		self.dir = dirMove

		if self.y < 0:
			self.y = 0
		elif self.y > bounds[1] - self.height:
			self.y = bounds[1] - self.height


class Ball(PygameObject):
	def __init__(self, x, y, v_x, v_y, r, color=(255, 255, 255)):
		self.x = x - r
		self.y = y - r
		self.v_x = v_x
		self.v_y = v_y

		self.r = r
		self.color = color

		self.collided = 0

		self.surface = pygame.Surface((2*r, 2*r))
		pygame.draw.circle(self.surface, color, (r, r), r)
		self.surface = self.surface.convert()
		self.surface.set_colorkey((0, 0, 0))
		self.surface = self.surface.convert_alpha()

	def update(self, rate, bounds, leftPaddle, rightPaddle):
		self.x += self.v_x*rate
		self.y += self.v_y*rate

		if self.x < 0:
			self.x = 0
			self.v_x *= -1
			return 'left'
		elif self.x > bounds[0] - 2*self.r:
			self.x = bounds[0] - 2*self.r
			self.v_x *= -1
			return 'right'

		if self.y < 0:
			self.y = 0
			self.v_y *= -1
		elif self.y > bounds[1] - 2*self.r:
			self.y = bounds[1] - 2*self.r
			self.v_y *= -1

		hitPaddle = self.checkCollision(leftPaddle, rightPaddle)

		return hitPaddle

	def checkCollision(self, leftPaddle, rightPaddle):
		self.collided -= 1
		if self.collided > 0:
			return False
		if self.x < leftPaddle.x + leftPaddle.width and (self.y < leftPaddle.y + leftPaddle.height and self.y + 2*self.r > leftPaddle.y):
			self.v_x *= -1
			self.v_x *= 1.1
			self.v_y += 0.5*leftPaddle.v_y*leftPaddle.dir
			self.collided = 3
			return 'left paddle'
		elif self.x + 2*self.r > rightPaddle.x and (self.y < rightPaddle.y + rightPaddle.height and self.y + 2*self.r > rightPaddle.y):
			self.v_x *= -1
			self.v_x *= 1.1
			self.v_y += 0.5*rightPaddle.v_y*rightPaddle.dir
			self.collided = 3
			return 'right paddle'
		else:
			return False

def draw_arrow(screen, colour, start, end):
	pygame.draw.line(screen,colour,start,end,2)

	rotation = math.degrees(math.atan2(start[1]-end[1], end[0]-start[0]))+90

	size = 10
	angle = 145

	pygame.draw.line(screen,colour,end,(end[0]+size*math.sin(math.radians(rotation-angle)), end[1]+size*math.cos(math.radians(rotation-angle))),2)
	pygame.draw.line(screen,colour,end,(end[0]+size*math.sin(math.radians(rotation+angle)), end[1]+size*math.cos(math.radians(rotation+angle))),2)

class Pong:
	def initObjects(self, size):
		width, height = size
		velocity = 0.4
		angle = random.choice((1, -1))*(random.uniform(0, 5*math.pi/8) + 5*math.pi/16)
		self.ball = Ball(width/2, height/2, velocity*math.sin(angle), velocity*math.cos(angle), 20)
		self.playerPaddle = Paddle(10, height/2, 0.5)
		self.cpuPaddle = Paddle(width - 30, height/2, 0.3, 20, 50)

	def __init__(self, size=(1920//2, 1080//2)):
		self.size = size

		self.myfont = pygame.font.SysFont(None, 30)

		self.screen = pygame.display.set_mode(size)
		self.background = pygame.Surface(self.screen.get_size())
		self.background.fill((0, 0, 0))
		self.background = self.background.convert()
		self.clock = pygame.time.Clock()

		self.FPS = 30.0
		self.playtime = 0.0

		self.lwins = 0
		self.rwins = 0

		self.paused = 0#self.FPS*3

		self.initObjects(size)

		self.milliseconds = 0



	def input(self):
		doQuit = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				doQuit = True
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					doQuit = True
				elif event.key == pygame.K_SPACE:
					self.__init__()
					self.playtime = 0.0
					self.lwins = 0
					self.rwins = 0
					self.paused = 3*self.FPS

		return doQuit

	def inputMove(self):
		keys_pressed = pygame.key.get_pressed()
		self.dirMove = 0
		if keys_pressed[pygame.K_DOWN]:
			self.makeMove('down', 'left')
		elif keys_pressed[pygame.K_UP]:
			self.makeMove('up', 'left')

		self.cpuDirMove = 0
		if self.ball.y + self.ball.r > self.cpuPaddle.y + self.cpuPaddle.height/2:
			self.makeMove('down', 'right')
		else:
			self.makeMove('up', 'right')

	def bestMove(self):
		self.cpuDirMove = 0
		if self.ball.y + self.ball.r > self.cpuPaddle.y + self.cpuPaddle.height/2:
			move = 'down'
		else:
			move = 'up'
		return move

	def makeMove(self, move, side):
		if move == 'up':
			if side == 'left':
				self.dirMove = -0.5
			else:
				self.cpuDirMove = -1
		elif move == 'down':
			if side == 'left':
				self.dirMove = 0.5
			else:
				self.cpuDirMove = 1
		else:
			if side == 'left':
				self.dirMove = 0
			else:
				self.cpuDirMove = 0

		if side == 'left':
			self.playerPaddle.update(self.milliseconds, self.screen.get_size(), self.dirMove)
		else:
			self.cpuPaddle.update(self.milliseconds, self.screen.get_size(), self.cpuDirMove)

	def update(self):

		self.milliseconds = self.clock.tick(self.FPS)
		self.playtime += self.milliseconds/1000.0

		done = False
		Q = 0

		if self.paused == 0:
			hitSide = self.ball.update(self.milliseconds, self.screen.get_size(), self.playerPaddle, self.cpuPaddle)

			if hitSide:
				if hitSide == 'left paddle':
					Q = 0.5
				elif hitSide == 'right paddle':
					Q = -0.5
				else:
					done = True
					if hitSide == 'right':
						self.lwins += 1
						Q = 1
					elif hitSide == 'left':
						self.rwins += 1
						Q = -1
					self.initObjects(self.size)
					self.paused = self.FPS*3
					self.paused = 0
		else:
			self.paused -= 1

		return done, torch.tensor([[Q]]).float()

	def draw(self):
		#draw
		self.screen.blit(self.background, (0, 0))
		text = "FPS: {0:.2f}   Playtime: {1:.2f}".format(self.clock.get_fps(), self.playtime)
		pygame.display.set_caption(text)

		scoreTitle = self.myfont.render(' SCORE ', True, (255, 255, 255))
		self.screen.blit(scoreTitle, (self.screen.get_width()/2 - scoreTitle.get_width()/2, 20))
		score = self.myfont.render('{0}  {1}'.format(self.lwins, self.rwins), True, (255, 255, 255))
		self.screen.blit(score, (self.screen.get_width()/2 - score.get_width()/2, 20 + scoreTitle.get_height()))

		self.ball.draw(self.screen)
		self.playerPaddle.draw(self.screen)
		self.cpuPaddle.draw(self.screen)
		draw_arrow(self.screen, (255, 255, 255), (self.ball.x + self.ball.r, self.ball.y + self.ball.r), (self.ball.x + self.ball.r + 100*self.ball.v_x, self.ball.y + self.ball.r + 100*self.ball.v_y))

		if self.paused != 0:
			countdownFont = pygame.font.SysFont(None, int(1.5*min(self.screen.get_size())*(((self.paused-1)%self.FPS)+1)/self.FPS))
			countdown = countdownFont.render('{}'.format(math.ceil(self.paused/self.FPS)), True, (255, 255, 255))
			self.screen.blit(countdown, (self.screen.get_width()/2 - countdown.get_width()/2, self.screen.get_height()/2 - countdown.get_height()/2))

		image = torch.from_numpy((pygame.surfarray.pixels_red(self.screen) + pygame.surfarray.pixels_blue(self.screen) + pygame.surfarray.pixels_green(self.screen))/3)
		pool = torch.nn.MaxPool2d(2, 2)
		image = pool(pool(pool(pool(image.view(1, 1, image.size(0), image.size(1))))))
		return image.float()

	def display(self):
		pygame.display.flip()



if __name__ == '__main__':
	pygame.init()

	pong = Pong()

	doQuit = False
	while not doQuit:

		doQuit = pong.input()
		pong.inputMove()

		pong.update()

		screen = pong.draw()
		pong.display()

	pygame.quit()
