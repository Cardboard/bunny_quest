import pygame
import os

class Bunny(pygame.sprite.Sprite):
    def __init__(self, *groups):
	super(Bunny, self).__init__(*groups)
	self.rect = pygame.Rect(0,0, 16,16)
	self.frame = 0
	self.max_frame = 4
	self.image = pygame.image.load(os.path.join('graphics', 'bunny.png'))
	self.images = []
	for i in range(0, self.max_frame):
	    newframe = self.image.subsurface(i*16, 0, 16, 16)
	    self.images.append(newframe)
	self.anim = 0
	self.anim_speed = 50

    def frameCheck(self, dt):
	if self.anim >= self.anim_speed:
	    if self.frame >= self.max_frame-1:
		self.frame = 0
	    else:
		self.frame += 1
	    self.anim = 0
	else:
	    self.anim += dt

    def update(self, dt, game):
	cell = game.tilemap.layers['triggers'].find('bunny')[0]
	self.rect.x, self.rect.y = cell.px, cell.py

	self.frameCheck(dt)
	self.image = self.images[self.frame]
