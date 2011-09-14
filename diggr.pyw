
import math
import os
import random
import copy
import time

import cPickle

import libtcodpy as libtcod

import sqlite3


random__ = random

qqq1 = None

class random(object):
    @staticmethod
    def randint(*a):
        print >> qqq1, 'randint', a
        return random__.randint(*a)
    @staticmethod
    def seed(*a):
        print >> qqq1, 'seed', a
        return random__.seed(*a)
    @staticmethod
    def gauss(*a):
        print >> qqq1, 'gauss', a
        return random__.gauss(*a)
    @staticmethod
    def uniform(*a):
        print >> qqq1, 'uniform', a
        return random__.uniform(*a)
    @staticmethod
    def choice(*a):
        print >> qqq1, 'choice', a
        return random__.choice(*a)


#
# achievements!
#

# B: large bird
# d: small dinosaur
# D: dinosaur
# f: faerie
# F: powerful faerie
# G: Japanese giant reptile
# h: humanoid
# H: powerful human
# k: knight, warrior or soldier
# K: epic hero, demigod or deity
# o: turtle, armadillo or porcupine
# O: large turtle
# q: quadruped mammal
# Q: huge quadriped mammal
# R: large reptile
# S: large snake
# u: urthian being
# U: urthian megatherian
# v: apparition, illusion or digital construct
# V: powerful digital construct
# w: worm
# W: giant worm
# x: insect, fungus or plant
# X: huge insect or insectoid
# y: undead
# Y: elder undead
# z: robot
# Z: large robot



global _version
_version = '11.09.11'

global _inputs
global _inputqueue
_inputqueue = None
class fakekey:
    def __init__(self, c, vk):
        self.c = c
        self.vk = vk


def console_wait_for_keypress():
    global _inputqueue
    if _inputqueue is not None:

        if len(_inputqueue) == 0:
            raise Exception('Malformed replay file.')

        c, vk = _inputqueue[0]
        _inputqueue = _inputqueue[1:]
        #libtcod.console_wait_for_keypress(False)
        libtcod.console_check_for_keypress()
        libtcod.sys_sleep_milli(100)
        return fakekey(c, vk)

    k = libtcod.console_wait_for_keypress(False)
    _inputs.append((k.c, k.vk))
    return k


class Coeffs:
    def __init__(self):
        self.movetired = 0.01
        self.movesleep = 0.005
        self.movethirst = 0.005
        self.movehunger = 0.0005

        self.resttired = 0.03
        self.restsleep = 0.005
        self.restthirst = 0.005
        self.resthunger = 0.0005

        self.sleeptired = 0.06
        self.sleepsleep = 0.01
        self.sleepthirst = 0.005
        self.sleephunger = 0.0005

        self.sleeptime = (350, 50)
        self.quicksleeptime = (50, 10)
        self.waterpois = 0.85
        self.watercold = 0.03

        self.colddamage = 0.03
        self.thirstdamage = 0.02
        self.hungerdamage = 0.01

        self.unarmedattack = 0.1
        self.unarmeddefence = 0.0

        self.nummonsters = (5, 1)
        self.monlevel = 0.75
        self.numitems = (3, 1.5)
        self.itemlevel = 0.75

        self.boozestrength = (2, 0.5)
        self.coolingduration = (50, 5)

        self.glueduration = (10,1)
        self.gluedefencepenalty = 3

        self.shivadecstat = 2.0
        self.graceduration = 1000

        self.raddamage = 3.0


class Stat:
    def __init__(self):
        self.x = 3.0
        self.reason = None

    def dec(self, dx, reason=None):
        if reason and self.x > -3.0:
            self.reason = reason
        self.x -= dx
        if self.x <= -3.0: self.x = -3.0


    def inc(self, dx):
        self.x += dx
        if self.x > 3.0: self.x = 3.0

class Stats:
    def __init__(self):
        self.health = Stat()
        self.sleep = Stat()
        self.tired = Stat()
        self.hunger = Stat()
        self.thirst = Stat()
        self.warmth = Stat()

        libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.white, libtcod.black)
        libtcod.console_set_color_control(libtcod.COLCTRL_2, libtcod.darker_green, libtcod.black)
        libtcod.console_set_color_control(libtcod.COLCTRL_3, libtcod.yellow, libtcod.black)
        libtcod.console_set_color_control(libtcod.COLCTRL_4, libtcod.red, libtcod.black)
        libtcod.console_set_color_control(libtcod.COLCTRL_5, libtcod.gray, libtcod.black)

    def draw(self, x, y):
        s = "%cHealth: %c%s\n" \
            "%cWarmth: %c%s\n" \
            "%c Tired: %c%s\n" \
            "%c Sleep: %c%s\n" \
            "%cThirst: %c%s\n" \
            "%cHunger: %c%s\n"

        def pr(x):
            if x >= 2.0: return    '   +++'
            elif x >= 1.0: return  '   ++'
            elif x >= 0.0: return  '   +'
            elif x >= -1.0: return '  -'
            elif x >= -2.0: return ' --'
            else: return           '---'

        def cl(x):
            if x >= 1.5: return libtcod.COLCTRL_2
            elif x >= -0.5: return libtcod.COLCTRL_3
            else: return libtcod.COLCTRL_4

        h = self.health.x
        d = self.warmth.x
        t = self.tired.x
        e = self.sleep.x
        i = self.thirst.x
        u = self.hunger.x

        q = (libtcod.COLCTRL_1, cl(h), pr(h),
             libtcod.COLCTRL_1, cl(d), pr(d),
             libtcod.COLCTRL_1, cl(t), pr(t),
             libtcod.COLCTRL_1, cl(e), pr(e),
             libtcod.COLCTRL_1, cl(i), pr(i),
             libtcod.COLCTRL_1, cl(u), pr(u))

        libtcod.console_print(None, x, y, s % q)




_kbdmap = {
    libtcod.KEY_LEFT: 'h',
    libtcod.KEY_RIGHT: 'l',
    libtcod.KEY_UP: 'k',
    libtcod.KEY_DOWN: 'j',
    libtcod.KEY_HOME: 'y',
    libtcod.KEY_PAGEUP: 'u',
    libtcod.KEY_END: 'b',
    libtcod.KEY_PAGEDOWN: 'n',
    libtcod.KEY_KP4: 'h',
    libtcod.KEY_KP6: 'l',
    libtcod.KEY_KP8: 'k',
    libtcod.KEY_KP2: 'j',
    libtcod.KEY_KP7: 'y',
    libtcod.KEY_KP9: 'u',
    libtcod.KEY_KP1: 'b',
    libtcod.KEY_KP3: 'n'
}

def draw_window(msg, w, h, do_mapping=False):
    maxl = 0
    for x in msg:
        maxl = max(len(x), maxl)

    l = len(msg)
    s = '\n'.join(msg)
    s = ('%c' % libtcod.COLCTRL_1) + s

    x0 = max(w - maxl - 4, 0)
    y0 = min(l + 2, h)
    libtcod.console_set_default_background(None, libtcod.darkest_blue)
    libtcod.console_rect(None, x0, 0, w - x0, y0, True, libtcod.BKGND_SET)
    libtcod.console_print_rect(None, x0 + 2, 1, w - x0 - 2, y0 - 1, s)
    libtcod.console_set_default_background(None, libtcod.black)

    libtcod.console_flush()
    #k = libtcod.console_wait_for_keypress(False)
    #_inputs.append((k.c, k.vk))
    k = console_wait_for_keypress()

    libtcod.console_rect(None, x0, 0, w - x0, y0, True)
    libtcod.console_flush()

    if do_mapping:
        if k.vk in _kbdmap: return _kbdmap[k.vk]

    return chr(k.c)

def draw_blast(x, y, w, h, r, func):
    x0 = min(x - r, 0)
    y0 = min(y - r, 0)
    x1 = max(x + r + 1, w)
    y1 = max(y + r + 1, h)
    c = []
    for xi in xrange(x0, x1):
        for yi in xrange(y0, y1):
            d = math.sqrt(math.pow(abs(yi - y),2) + math.pow(abs(xi - x),2))
            if d <= r and xi >= 0 and xi < w and yi >= 0 and yi < h:
                c.append((xi, yi))

    def dr():
        for c0 in c:
            libtcod.console_put_char_ex(None, c0[0], c0[1], '*', fore, back)
        libtcod.console_flush()
        libtcod.sys_sleep_milli(100)

    back = libtcod.darkest_red
    fore = libtcod.yellow
    dr()
    fore = libtcod.color_lerp(fore, back, 0.5)
    dr()
    fore = libtcod.color_lerp(fore, back, 0.5)
    dr()
    for c0 in c:
        func(c0[0], c0[1])


def draw_blast2(x, y, w, h, r, func1, func2):
    x0 = min(x - r, 0)
    y0 = min(y - r, 0)
    x1 = max(x + r + 1, w)
    y1 = max(y + r + 1, h)
    c = []
    for xi in xrange(x0, x1):
        for yi in xrange(y0, y1):
            d = math.sqrt(math.pow(abs(yi - y),2) + math.pow(abs(xi - x),2))
            if d <= r and xi >= 0 and xi < w and yi >= 0 and yi < h:
                if func1(xi, yi):
                    c.append((xi, yi))

    def dr():
        for c0 in c:
            libtcod.console_put_char_ex(None, c0[0], c0[1], '*', fore, back)
        libtcod.console_flush()
        libtcod.sys_sleep_milli(100)

    back = libtcod.darkest_blue
    fore = libtcod.light_azure
    dr()
    fore = libtcod.color_lerp(fore, back, 0.5)
    dr()
    fore = libtcod.color_lerp(fore, back, 0.5)
    dr()
    for c0 in c:
        func2(c0[0], c0[1])



class Messages:
    def __init__(self):
        self.strings = []

    def draw(self, x, y, w):
        l = []
        for v,m in self.strings[:3]:
            if v:
                l.append('%c%s' % (v,m))
            elif len(l) == 0:
                l.append('%c%s' % (libtcod.COLCTRL_1, m))
            else:
                l.append('%c%s' % (libtcod.COLCTRL_5, m))

        libtcod.console_print_rect(None, x, y, w, 3, '\n'.join(l))

    def m(self, s, bold = None):
        if len(self.strings) > 0 and s == self.strings[0][1]:
            return

        if bold:
            self.strings.insert(0, (libtcod.COLCTRL_3, s))
        else:
            self.strings.insert(0, (None, s))
        if len(self.strings) > 25:
            self.strings.pop()

    def show_all(self, w, h):
        l = []
        for v,m in self.strings[:24]:
            if v:
                l.append('%c%s' % (v,m))
            elif len(l) == 0:
                l.append('%c%s' % (libtcod.COLCTRL_1, m))
            else:
                l.append('%c%s' % (libtcod.COLCTRL_5, m))
        draw_window(l, w, h)


class Inventory:
    def __init__(self):
        self.head = None
        self.neck = None
        self.trunk = None
        self.left = None
        self.right = None
        self.legs = None
        self.feet = None
        self.backpack1 = None
        self.backpack2 = None

    def draw(self, w, h, dlev, plev):
        s = [
            ("a)       Head: %c%s", self.head),
            ("b)       Neck: %c%s", self.neck),
            ("c)      Trunk: %c%s", self.trunk),
            ("d)  Left hand: %c%s", self.left),
            ("e) Right hand: %c%s", self.right),
            ("f)       Legs: %c%s", self.legs),
            ("g)       Feet: %c%s", self.feet),
            ("h) Backpack 1: %c%s", self.backpack1),
            ("i) Backpack 2: %c%s", self.backpack2),
            "",
            "Character level: %d" % plev,
            "  Dungeon level: %d" % dlev]

        def pr(x):
            if not x:
                return ' -'
            return str(x)

        for x in xrange(len(s)):
            if type(s[x]) == type((0,)):
                s[x] = ("%c" % libtcod.COLCTRL_5) + \
                       s[x][0] % (libtcod.COLCTRL_1, pr(s[x][1]))

        return draw_window(s, w, h)

    def take(self, i, slot=None):
        if not slot:
            slot = i.slot
        if   slot == 'a' and not self.head: self.head = i
        elif slot == 'b' and not self.neck: self.neck = i
        elif slot == 'c' and not self.trunk: self.trunk = i
        elif slot == 'd' and not self.left: self.left = i
        elif slot == 'e' and not self.right: self.right = i
        elif slot == 'f' and not self.legs: self.legs = i
        elif slot == 'g' and not self.feet: self.feet = i
        elif slot == 'h' and not self.backpack1: self.backpack1 = i
        elif slot == 'i' and not self.backpack2: self.backpack2 = i
        elif not self.backpack1: self.backpack1 = i
        elif not self.backpack2: self.backpack2 = i
        else: return False
        return True

    def drop(self, i):
        if i == 'a':
            i, self.head = self.head, None
            return i
        elif i == 'b':
            i, self.neck = self.neck, None
            return i
        elif i == 'c':
            i, self.trunk = self.trunk, None
            return i
        elif i == 'd':
            i, self.left = self.left, None
            return i
        elif i == 'e':
            i, self.right = self.right, None
            return i
        elif i == 'f':
            i, self.legs = self.legs, None
            return i
        elif i == 'g':
            i, self.feet = self.feet, None
            return i
        elif i == 'h':
            i, self.backpack1 = self.backpack1, None
            return i
        elif i == 'i':
            i, self.backpack2 = self.backpack2, None
            return i
        else:
            return None

    def check(self, slot):
        if   slot == 'a': return self.head
        elif slot == 'b': return self.neck
        elif slot == 'c': return self.trunk
        elif slot == 'd': return self.left
        elif slot == 'e': return self.right
        elif slot == 'f': return self.legs
        elif slot == 'g': return self.feet
        elif slot == 'h': return self.backpack1
        elif slot == 'i': return self.backpack2
        return None

    class _iter:
        def __init__(self, i):
            self.inv = i
            self.slot = 0
        def __iter__(self):
            return self
        def next(self):
            self.slot += 1
            if self.slot == 1: return self.inv.head
            elif self.slot == 2: return self.inv.neck
            elif self.slot == 3: return self.inv.trunk
            elif self.slot == 4: return self.inv.left
            elif self.slot == 5: return self.inv.right
            elif self.slot == 6: return self.inv.legs
            elif self.slot == 7: return self.inv.feet
            elif self.slot == 8: return self.inv.backpack1
            elif self.slot == 9: return self.inv.backpack2
            else: raise StopIteration()

    def __iter__(self):
        return self._iter(self)

    def purge(self, item):
        if self.head == item: self.head = None
        elif self.neck == item: self.neck = None
        elif self.trunk == item: self.trunk = None
        elif self.left == item: self.left = None
        elif self.right == item: self.right = None
        elif self.legs == item: self.legs = None
        elif self.feet == item: self.feet = None
        elif self.backpack1 == item: self.backpack1 = None
        elif self.backpack2 == item: self.backpack2 = None

    def get_lightradius(self):
        return getattr(self.head,  'lightradius', 0) + \
               getattr(self.neck,  'lightradius', 0) + \
               getattr(self.legs,  'lightradius', 0) + \
               getattr(self.trunk, 'lightradius', 0)

    def get_attack(self):
        return getattr(self.right, 'attack', 0) + \
               getattr(self.left, 'attack', 0) + \
               getattr(self.feet, 'attack', 0)

    def get_defence(self):
        return getattr(self.head, 'defence', 0) + \
               getattr(self.left, 'defence', 0) + \
               getattr(self.trunk, 'defence', 0) + \
               getattr(self.legs, 'defence', 0) + \
               getattr(self.feet, 'defence', 0)

    def get_heatbonus(self):
        return getattr(self.trunk, 'heatbonus', 0) + \
               getattr(self.legs, 'heatbonus', 0)

    def get_confattack(self):
        return getattr(self.right, 'confattack', None) or \
               getattr(self.left, 'confattack', None)

    def get_psyimmune(self):
        return getattr(self.head, 'psyimmune', None) or \
               getattr(self.right, 'psyimmune', None) or \
               getattr(self.left, 'psyimmune', None)


class Item:
    def __init__(self, name, slot='', bonus=0, count=None, ident=False,
                 skin=('~', libtcod.yellow), lightradius=0, explodes=0,
                 applies=False, liveexplode=None, radius=0, attack=0,
                 defence=0, desc=None, throwable=False, throwrange=8, booze=False,
                 cursedchance=0, range=None, ammochance=None, rangeattack=0,
                 straightline=False, confattack=None, rarity=None, healing=None,
                 homing=False, cooling=False, digging=False, psyimmune=False,
                 rangeexplode=False, springy=False, detector=False,
                 detect_monsters=False, detect_items=False, food=None,
                 tracker=False, wishing=False, repelrange=None, selfdestruct=None,
                 digray=None, jinni=False, heatbonus=0, use_an=False,
                 stackrange=None, mapper=None, converts=None, jumprange=None,
                 explodeimmune=False, telepathyrange=None, makestrap=False,
                 summon=None, radimmune=False, radexplode=False, fires=None,
                 camorange=None, sounding=False):
        self.slot = slot
        self.bonus = bonus
        self.name = name
        self.count = count
        self.ident = ident
        self.skin = skin
        self.lightradius = lightradius
        self.explodes = explodes
        self.applies = applies
        self.liveexplode = liveexplode
        self.radius = radius
        self.attack = attack
        self.defence = defence
        self.desc = desc
        self.throwable = throwable
        self.throwrange = throwrange
        self.booze = booze
        self.cursedchance = cursedchance
        self.range = range
        self.ammochance = ammochance
        self.rangeattack = rangeattack
        self.straightline = straightline
        self.confattack = confattack
        self.rarity = rarity
        self.healing = healing
        self.homing = homing
        self.cooling = cooling
        self.digging = digging
        self.psyimmune = psyimmune
        self.rangeexplode = rangeexplode
        self.springy = springy
        self.detector = detector
        self.detect_monsters = detect_monsters
        self.detect_items = detect_items
        self.food = food
        self.tracker = tracker
        self.wishing = wishing
        self.repelrange = repelrange
        self.selfdestruct = selfdestruct
        self.digray = digray
        self.jinni = jinni
        self.heatbonus = heatbonus
        self.use_an = use_an
        self.stackrange = stackrange
        self.mapper = mapper
        self.converts = converts
        self.jumprange = jumprange
        self.explodeimmune = explodeimmune
        self.telepathyrange = telepathyrange
        self.makestrap = makestrap
        self.summon = summon
        self.radimmune = radimmune
        self.radexplode = radexplode
        self.fires = fires
        self.camorange = camorange
        self.sounding = sounding

        self.ammo = None
        self.gencount = 0


    def __str__(self):
        s = ''
        if self.ident:
            if self.bonus > 0:
                s += 'blessed '
            elif self.bonus < 0:
                s += 'cursed '
        s += self.name
        if self.count > 1:
            s = str(self.count) + " " + s.replace('$s', 's')
        elif self.count != 0 and len(s) > 0:
            if self.count == 1:
                s = s.replace('$s', '')

            if self.use_an or s[0] in 'aeiouAEIOU':
                s = 'an ' + s
            else:
                s = 'a ' + s
        if self.ammo:
            s = s + ' [%d]' % self.ammo
        return s

    def postprocess(self):
        if self.cursedchance:
            if random.randint(0, self.cursedchance) == 0:
                self.bonus = -1

        if self.ammochance:
            self.ammo = random.randint(self.ammochance[0], self.ammochance[1])

        if self.selfdestruct:
            self.selfdestruct = int(max(random.gauss(*self.selfdestruct), 1))


class ItemStock:
    def __init__(self):
        self.necklamp = Item("miner's lamp", slot='b', lightradius=8, rarity=8,
                             desc=['A lamp that provides light while you are cave-crawling.'])

        self.helmet = Item("miner's hardhat", slot='a', rarity=8,
                           skin=('[', libtcod.sepia), defence=0.25,
                           desc=['A simple plastic item of protective headgear.'])

        self.boots = Item('boots', slot='g', count=0, rarity=8,
                          skin=('[', libtcod.sepia), defence=0.1,
                          desc=['Steel-toed boots made of genuine leather.'])

        self.dynamite = Item('stick$s of dynamite', count=3, stackrange=3,
                             skin=('!', libtcod.red), applies=True, explodes=True,
                             radius=4, rarity=8, converts='litdynamite',
                             desc=['Sticks of dynamite can be lit to create an explosive device.'])

        self.minibomb = Item('minibomb$s', count=3, skin=('(', libtcod.pink),
                             applies=True, explodes=True, radius=1, rarity=8,
                             converts='litminibomb', stackrange=3,
                             desc=['Tiny hand-held grenades.'])

        self.gbomb = Item('gamma bomb$s', count=5, stackrange=5,
                          skin=('!', libtcod.azure), applies=True,
                          rarity=5, converts='litgbomb',
                          desc=["An object that looks something like a grenade, "
                                "but with a 'radiation sickness' sign painted on it."])

        self.litdynamite = Item('burning stick of dynamite',
                                skin=('!', libtcod.yellow), explodes=True,
                                liveexplode=7, slot='d', radius=4, throwable=True,
                                desc=['Watch out!!'])

        self.litminibomb = Item('armed minibomb', skin=('!', libtcod.yellow),
                                explodes=True, liveexplode=2, slot='d', radius=1,
                                throwable=True,
                                desc=['Watch out!!'])

        self.litgbomb = Item('activated gamma bomb', skin=('!', libtcod.yellow),
                             radexplode=True, liveexplode=4, slot='d', radius=12,
                             throwable=True, desc=['Watch out!!'])

        self.bomb = Item('exploding spore', skin=('!', libtcod.yellow), explodes=True,
                         liveexplode=4, slot='d', radius=3, throwable=True,
                         desc=['Uh-oh.'])

        self.radblob = Item('radiation blob', skin=('!', libtcod.yellow), radexplode=True,
                            liveexplode=2, slot='d', radius=8, throwable=True,
                            desc=['Uh-oh.'])

        self.pickaxe = Item("miner's pickaxe", slot='e', skin=('(', libtcod.gray),
                            attack=2.0, rarity=8, applies=True, digging=True,
                            desc=['Ostensibly to be used as an aid in traversing the caves,',
                                  'this sporting item is a good makeshift weapon.'])

        self.longsword = Item('longsword', slot='e', skin=('(', libtcod.silver),
                              attack=6.0, rarity=8,
                              desc=['Ye olde assault weapon.'])

        self.excalibur = Item('Excalibur', slot='e', skin=('(', libtcod.silver),
                              attack=7.5, count=0,
                              desc=['A larger-than-life sword.'])

        self.booze = Item("potion$s of booze", slot='d', skin=('!', libtcod.green),
                          booze=True, cursedchance=10, applies=True, stackrange=2,
                          count=1, rarity=10,
                          desc=['Sweet, sweet aqua vitae.',
                                'It helps keep one warm in these horrible caves.'])

        self.homing = Item("dowsing rod", slot='d', skin=(')', libtcod.cyan),
                           applies=True, rarity=8, homing=True,
                           desc=["A low-tech device for finding holes."])

        self.sonar = Item("rock sonar", slot='d', skin=(')', libtcod.darker_cyan),
                          applies=True, rarity=7, sounding=True,
                          desc=["A device that uses sonar for discovering rock thickness."])

        self.medpack = Item("magic pill$s", slot='d', skin=('%', libtcod.white),
                            rarity=20, applies=True, healing=(3, 0.5),
                            cursedchance=7, stackrange=5, count=1,
                            desc=['A big white pill with a large red cross drawn on one side.'])

        self.mushrooms = Item("mushroom$s", slot='d', skin=('%', libtcod.light_orange),
                              rarity=20, applies=True, food=(3, 0.5),
                              cursedchance=7, stackrange=3, count=1,
                              desc=['A mushroom growing on the cave floor.'])

        self.rpg = Item('RPG launcher', slot='e', skin=('(', libtcod.red),
                        rarity=15, applies=True, rangeexplode=True, range=(4, 15),
                        explodes=True, radius=3, attack=0, ammochance=(1,1),
                        use_an=True,
                        desc=['A metal tube that holds a single explosive rocket.'])

        self.killerwand = Item('killer wand', slot='e', skin=('/', libtcod.red),
                               rarity=5, applies=True, rangeexplode=True, range=(1, 3),
                               explodes=True, radius=0, attack=0, ammochance=(1,1),
                               desc=['A metallic wand with a skull-and-crossbones embossed on it.',
                                     'There is an annoying blinking LED light mounted in the handle.'])

        self.mauser = Item("Mauser C96", slot='e', skin=('(', libtcod.blue),
                           rangeattack=7.0, range=(0,15), ammochance=(0, 10),
                           straightline=True, applies=True, rarity=15,
                           desc=['This antique beauty is a powerful handgun, ',
                                 'though a bit rusty for some reason.'])

        self.ak47 = Item('AK-47', slot='e', skin=('(', libtcod.desaturated_blue),
                         rangeattack=3.5, range=(0, 7), ammochance=(0, 30),
                         straightline=True, applies=True, rarity=15,
                         desc=['A semi-automatic rifle.'])

        self.shotgun = Item('shotgun', slot='e', skin=('(', libtcod.turquoise),
                            rangeattack=14.0, range=(2,5), ammochance=(1,4),
                            straightline=True, applies=True, rarity=15,
                            desc=['A powerful, killer weapon.',
                                  'You learned that much from playing videogames.'])

        self.flamethrower = Item("flamethrower", slot='e', skin=('(', libtcod.orange),
                                 rangeattack=7.0, range=(2,6), ammochance=(1, 6),
                                 straightline=True, applies=True, rarity=15, fires=10,
                                 desc=['A device for setting monsters on fire.',
                                       'Truly ingenious.'])

        self.tazer = Item("tazer", slot='e', skin=('(', libtcod.gray),
                          attack=1.0, confattack=(10, 1), rarity=5,
                          desc=['Very useful for subduing enemies.'])

        self.redgloves = Item("red hand gloves", slot='d', skin=('(', libtcod.dark_red),
                          attack=0.1, confattack=(10, 1), rarity=3, count=0,
                          desc=['These magical gloves have a very confusing red glow.'])

        self.dartgun = Item('dart gun', slot='e', skin=('(', libtcod.light_crimson),
                            attack=0.5, confattack=(30, 5), rarity=5, range=(0,5),
                            rangeattack=0.5, ammochance=(10,30), straightline=True,
                            applies=True,
                            desc=['A small plastic gun loaded with suspicious-looking darts.'])

        self.bigdartgun = Item('elephant sedative', slot='e', skin=('(', libtcod.crimson),
                               attack=0.1, confattack=(150, 5), rarity=3, range=(0,4),
                               rangeattack=4.5, ammochance=(2,4), straightline=True,
                               applies=True,
                               desc=['An applicator used for delivering ',
                                     'sedative darts to elephants.'
                                     'It looks like a small rocket launcher.'])

        self.tinfoilhat = Item('tin foil hat', slot='a', skin=('[', libtcod.gray),
                               psyimmune=True, rarity=6,
                               selfdestruct=(3000,500),
                               desc=['A metallic hat that protects against attempts of ',
                                     'mind control by various crazies.'])

        self.tinfoilcrystal = Item('crystal of tin', slot='d', skin=('+', libtcod.gray),
                                   psyimmune=True, rarity=6,
                                   selfdestruct=(3000,500),
                                   desc=['A magical crystal of tin.',
                                         'It acts much the same as a tin foil hat.'])

        self.tinstaff = Item('eldritch staff', slot='e', skin=('/', libtcod.gray),
                             psyimmune=True, rarity=5, attack=0.01,
                             desc=['A staff covered with ornate carvings of lovecraftian horrors.',
                                   'It seems to be a powerful psyonic artefact, albeit a useless weapon.'])

        self.coolpack = Item("some cold mud", slot='d', skin=('%', libtcod.light_blue),
                             applies=True, cooling=True, rarity=12, count=0,
                             desc=['A bluish lump of mud. ',
                                   'Useful for tricking predators with infrared vision.'])

        self.tinfoil = Item("tin foil", slot='a', skin=('[', libtcod.lightest_sepia), count=0,
                            psyimmune=True, rarity=12, selfdestruct=(450, 100),
                            desc=['Not as good as a real tin foil hat, but will still help in emergencies.'])

        self.springboots = Item("springy boots", slot='g', count=0,
                                skin=('[', libtcod.pink), defence=0.01, rarity=3,
                                springy=True,
                                desc=['Strange boots with giant springs attached to the soles.'])

        self.spikeboots = Item('spiked boots', slot='g', count=0,
                               skin=('[', libtcod.darkest_gray), attack=1.0, defence=0.05,
                               rarity=5,
                               desc=['These boots have giant spikes attached to them.',
                                   'Very heavy metal.'])

        self.shinypants = Item('shiny pants', slot='f', count=0,
                               skin=('[', libtcod.lightest_yellow), defence=0.01,
                               lightradius=3, rarity=5,
                               desc=["These pants a completely covered in spiffy sparkles and shiny LED's.",
                                     "Here in the caves there is nothing to be ashamed of, really."])

        self.furpants = Item('fur pants', slot='f', count=0,
                             skin=('[', libtcod.gray), defence=0.15, heatbonus=0.005, rarity=5,
                             desc=['Shaggy pants made of fur. You would look like a true barbarian in them.'])

        self.furcoat = Item('fur coat', slot='c',
                             skin=('[', libtcod.gray), defence=0.15, heatbonus=0.005, rarity=5,
                             desc=['A shaggy coat made of fur. You would look like a true barbarian in it.'])

        self.halolamp = Item("halogen lamp", slot='b', lightradius=12, rarity=3,
                             selfdestruct=(1000,100),
                             desc=['A lamp that is somewhat brighter than a generic lamp.'])

        self.helmetlamp = Item("flashlight helmet", slot='a',
                               skin=('[', libtcod.orange), defence=0.15, rarity=8, lightradius=4,
                               desc=['A plastic helmet with a lamp mounted on it.'])

        self.pelorusm = Item('pelorus', slot='b', skin=('"', libtcod.gray),
                            applies=True, detector=True, rarity=3, detect_monsters=True,
                            desc=['A device that looks somewhat like an old cellphone.',
                                  'It comes with a necklace strap, a display and a large antenna.'])

        self.pelorusi = Item('pelorus', slot='b', skin=('"', libtcod.gray),
                            applies=True, detector=True, rarity=3, detect_items=True,
                            desc=['A device that looks somewhat like an old cellphone.',
                                  'It comes with a necklace strap, a display and a large antenna.'])

        self.pelorusim = Item('pelorus', slot='b', skin=('"', libtcod.gray),
                            applies=True, detector=True, rarity=2, detect_monsters=True, detect_items=True,
                            desc=['A device that looks somewhat like an old cellphone.',
                                  'It comes with a necklace strap, a display and a large antenna.'])

        self.gps = Item('GPS tracker', slot='b', skin=('"', libtcod.green),
                        tracker=True, rarity=6, applies=True,
                        desc=["A device that tracks and remembers where you've already been."])

        self.wishing = Item('wand of wishes', slot='e', skin=('/', libtcod.gray),
                            applies=True, wishing=True, rarity=2,
                            desc=['A magic wand.'])

        self.digwandh = Item('wand of digging', slot='e', skin=('/', libtcod.azure),
                             applies=True, digray=(1,0), rarity=4,
                             desc=['A magic wand.'])

        self.digwandv = Item('wand of digging', slot='e', skin=('/', libtcod.azure),
                             applies=True, digray=(0,1), rarity=4,
                             desc=['A magic wand.'])

        self.repellerarmor = Item('repeller armor', slot='c', skin=('[', libtcod.white),
                                  repelrange=3, rarity=3, defence=0.01,
                                  selfdestruct=(1000, 100),
                                  desc=['A vest that provides a portable force-field shield.'])

        self.camo = Item('nanoparticle camouflage', slot='c', skin=('[', libtcod.dark_green),
                         camorange=3, rarity=3, defence=0.01, count=0,
                         selfdestruct=(1000, 100),
                         desc=['An ultra-hightech piece of camoflage clothing.',
                               "It's made of nanoparticles that render the wearer",
                               'practically invisible.'])

        self.vikinghelmet = Item('viking helmet', slot='a', skin=('[', libtcod.green),
                                 rarity=5, defence=0.5,
                                 desc=['An iron helmet with large horns, for extra protection.'])

        self.shield = Item('shield', slot='d', skin=('[', libtcod.dark_green),
                           rarity=5, defence=1.0,
                           desc=['A sturdy wooden shield.'])

        self.metalboots = Item('metal boots', slot='g', skin=('[', libtcod.brass),
                               count=0, rarity=5, defence=0.5,
                               desc=['Heavy boots made out of a single piece of sheet metal.'])

        self.legarmor = Item('leg armor', slot='f', skin=('[', libtcod.copper),
                             count=0, rarity=5, defence=0.5,
                             desc=['Protective iron plates that go on your thighs and shins.'])

        self.ringmail = Item('ring mail', slot='c', skin=('[', libtcod.gold),
                             rarity=5, defence=2.0,
                             desc=['Ye olde body protection armor.'])

        self.magiclamp = Item('magic lamp', slot='d', skin=('(', libtcod.gold),
                              rarity=4, jinni=True, applies=True,
                              desc=['Rub me for a surprise!'])

        self.magicmapper = Item('magic mapper', slot='e', skin=('"', libtcod.light_yellow),
                                rarity=6, applies=True, mapper=4,
                                desc=['A strange device that looks something like a large fishing sonar.'])


        self.portablehole = Item('portable hole$s', slot='d', skin=('`', libtcod.sepia),
                                 rarity=6, applies=True, jumprange=3, stackrange=5,
                                 count=2,
                                 desc=['A portable hole. Used as an escape device.'])

        self.bombsuit = Item('bomb suit', slot='c', skin=('[', libtcod.lightest_yellow),
                             explodeimmune=True, rarity=3, defence=0.1,
                             selfdestruct=(300, 50),
                             desc=['The standard protective suit for bomb squads.'])

        self.radsuit = Item('radiation suit', slot='c', skin=('[', libtcod.dark_lime),
                             radimmune=True, rarity=0, defence=0.1,
                             selfdestruct=(1000, 50),
                             desc=['A very special piece of equipment that protects against radiation.'])

        self.psyhelmet = Item('crystal helmet', slot='a', skin=('[', libtcod.white),
                               telepathyrange=6, rarity=6,
                               desc=['An ornate helmet made of crystal.',
                                     'It is a powerful artifact of psyonic magic.'])

        self.stickyglue = Item('sticky glue$s', slot='d', skin=('+', libtcod.light_yellow),
                               applies=True, makestrap=True, rarity=8, count=1,
                               stackrange=4,
                               desc=['A tube of very sticky glue. It can be used to make traps.'])

        self.gluegun = Item('gluegun', slot='d', skin=('+', libtcod.light_yellow),
                            applies=True, makestrap=True, rarity=0, count=None,
                            desc=['A device that holds a practically unlimited amount of glue.'])

        self.cclarva = Item('carrion crawler larva', slot='', skin=(',', libtcod.white),
                            rarity=0, summon=('carrion crawler', 2),
                            throwable=True, liveexplode=4,
                            desc=['A tiny larva of the carrion crawler species.'])

        self.triffidlarva = Item('triffid seed', slot='', skin=(',', libtcod.peach),
                                 rarity=0, summon=('triffid', 1),
                                 throwable=True, liveexplode=4,
                                 desc=['A tiny larva of the carrion crawler species.'])

        self.avern = Item('avern', slot='e', skin=('(', libtcod.dark_green),
                          attack=6.0, rarity=0, selfdestruct=(500, 100),
                          desc=['A makeshift weapon made from the poisonous avern plant.'])

        self.alzabobrain = Item('alzabo brain matter', slot='', skin=(',', libtcod.darkest_red),
                                 rarity=0, summon=('alzabo', 1),
                                 throwable=True, liveexplode=4, count=0,
                                 desc=["Bits and pieces of the alzabo's brain."])

        self.regenpool()

    def regenpool(self):
        self._randpool = []
        for x in dir(self):
            i = getattr(self, x)
            if type(i) == type(self.booze) and i.rarity:
                for n in xrange(i.rarity):
                    self._randpool.append(i)


    def get(self, item):
        i = getattr(self, item, None)
        if i:
            r = copy.copy(i)
            r.postprocess()
            return r
        return None

    def find(self, item):
        if len(item) < 3:
            return None

        l = []
        for x in xrange(len(self._randpool)):
            if self._randpool[x].name.replace('$s','').lower().find(item) >= 0:
                l.append((x, self._randpool[x]))

        if len(l) == 0:
            return None

        x = int(random.randint(0, len(l)-1))
        item = l[x][1]
        r = copy.copy(item)
        r.postprocess()
        del self._randpool[l[x][0]]
        return r

    def generate(self, level):
        if len(self._randpool) == 0:
            self.regenpool()

        i = int(random.randint(0, len(self._randpool)-1))
        item = self._randpool[i]

        item.gencount += 1
        r = copy.copy(item)
        r.postprocess()

        del self._randpool[i]

        return r



class Monster:
    def __init__(self, name, skin=('x', libtcod.cyan), count=10, level=1,
                 attack=0.5, defence=0.5, explodeimmune=False, range=11,
                 itemdrop=None, heatseeking=False, desc=[], psyattack=0,
                 psyrange=0, confimmune=False, slow=False, selfdestruct=False,
                 straightline=False, stoneeating=False, sleepattack=False,
                 hungerattack=False, flying=False, radimmune=False, no_a=False,
                 summon=False, branch=None, fireimmune=False):
        self.name = name
        self.skin = skin
        self.count = count
        self.level = level
        self.attack = attack
        self.defence = defence
        self.explodeimmune = explodeimmune
        self.range = range
        self.itemdrop = itemdrop
        self.heatseeking = heatseeking
        self.desc = desc
        self.psyattack = psyattack
        self.psyrange = psyrange
        self.confimmune = confimmune
        self.slow = slow
        self.selfdestruct = selfdestruct
        self.straightline = straightline
        self.stoneeating = stoneeating
        self.sleepattack = sleepattack
        self.hungerattack = hungerattack
        self.flying = flying
        self.radimmune = radimmune
        self.no_a = no_a
        self.summon = summon
        self.branch = branch
        self.fireimmune = fireimmune

        self.x = 0
        self.y = 0
        self.known_px = None
        self.known_py = None
        self.did_move = False
        self.do_move = None
        self.do_die = False
        self.hp = 3.0
        self.items = []
        self.confused = 0
        self.glued = 0
        self.visible = False
        self.visible_old = False
        self.gencount = 0

        self.onfire = 0
        self.fireattack = None
        self.fireduration = 0


    def __str__(self):
        s = self.name
        if not self.no_a:
            if s[0] in 'aeiouAEIOU':
                s = 'an ' + s
            else:
                s = 'a ' + s
        return s


class MonsterStock:
    def __init__(self):
        self.monsters = {}

        # Megafauna dungeon branch

        self.add(Monster('Australopithecus afarensis', skin=('h', libtcod.sepia),
                         branch='a', attack=0.1, defence=0.3, range=4, level=1,
                         itemdrop='booze', count=9, no_a=True,
                         desc=['An early hominid, this creature walked upright',
                               'but lacked the intelligence of the modern human.']))

        self.add(Monster('Calvatia gigantea', skin=('x', libtcod.white),
                         branch='a', attack=0.0, defence=0.2, range=1, level=1,
                         itemdrop='mushrooms', confimmune=True, count=8, no_a=True,
                         desc=['(Also known as the giant puffball.)',
                               'An edible mushroom about the same size, color and texture',
                               'as a volleyball.']))

        self.add(Monster('Meganeura monyi', skin=('X', libtcod.light_gray),
                         branch='a', attack=0.5, defence=1.7, range=5, level=2,
                         count=7, confimmune=True, no_a=True, flying=True,
                         desc=['One of the largest insects to have ever lived,',
                               'it is a relative of the modern-day dragonfly from',
                               'the Carboniferous period.',
                               "It's about the same size as a modern-day crow."]))

        self.add(Monster('Sus barbatus', skin=('q', libtcod.dark_sepia),
                         branch='a', attack=1.2, defence=0.6, range=4, level=2,
                         count=6, no_a=True,
                         desc=['(Also known as the bearded pig.)',
                               'A species of pig. It is characterized by its beard-like',
                               'facial hair. It is native to the tropics.']))

        self.add(Monster('Dinornis giganteus', skin=('B', libtcod.light_sepia),
                         branch='a', attack=1.0, defence=0.5, range=7, level=2,
                         count=5, no_a=True,
                         desc=['(Also known as the giant moa.)',
                               'A gigantic flightless bird, like the modern-day',
                               'ostrich, only about twice as big.']))

        self.add(Monster('Megatherium americanum', skin=('Q', libtcod.light_amber),
                         branch='a', attack=0.5, defence=3.5, range=5, level=3,
                         count=6, no_a=True, slow=True,
                         desc=['A gigantic ground sloth from the Pliocene period.',
                               'It was one of the largest land animals to ever live,',
                               'larger than the modern-day African elephant.']))

        self.add(Monster('Argentavis magnificens', skin=('B', libtcod.dark_blue),
                         branch='a', attack=3.0, defence=0.3, range=17, level=3,
                         count=6, no_a=True, flying=True,
                         desc=['The largest flying bird to have ever lived.',
                               'A relative of the modern-day Andean condor,',
                               'this bird had a wingspan of 7 meters and weighed',
                               'up to 80 kilograms.']))

        self.add(Monster('Bos primigenius', skin=('Q', libtcod.lightest_gray),
                         branch='a', attack=7.0, defence=1.0, range=10, level=3,
                         count=3, no_a=True,
                         desc=['(Also known as the aurochs.)',
                               'This magnificent animal was the ancesor of modern-day',
                               'domestic cattle. It is much larger and stronger than any',
                               'domestic bull.']))

        self.add(Monster('Crocodylus porosus', skin=('R', libtcod.green),
                         branch='a', attack=5.0, defence=3.0, range=9, level=4,
                         count=7, no_a=True, slow=True, heatseeking=True,
                         desc=['(Also known as the saltwater crocodile.)',
                               'The largest of all living reptiles.']))

        self.add(Monster('Varanus komodoensis', skin=('R', libtcod.gray),
                         branch='a', attack=2.0, defence=2.0, range=9, level=4,
                         count=7, no_a=True,
                         desc=['(Also known as the Komodo dragon.)',
                               'Not as large as a crocodile, this truly huge',
                               'lizard is still a fearsome opponent.']))

        self.add(Monster('Colossochelys atlas', skin=('O', libtcod.darkest_green),
                         branch='a', attack=1.0, defence=24.0, explodeimmune=True,
                         range=10, confimmune=True, slow=True, level=5, count=4, no_a=True,
                         desc=['The largest land turtle, ever.',
                               'Found in the Pleistoce perood, it is the size and weight',
                               'of your average SUV vehicle.']))

        self.add(Monster('Gigantophis garstini', skin=('S', libtcod.green),
                         branch='a', attack=4.0, defence=1.0, range=20, level=5, count=9, no_a=True,
                         heatseeking=True, confimmune=True,
                         desc=['One of the largest snakes known, it is an almost',
                               '10 meter long ancient relative of the modern boa constrictor.']))

        self.add(Monster('Arctotherium bonariense', skin=('Q', libtcod.dark_sepia),
                         branch='a', attack=10.0, defence=2.0, range=10, level=6, count=3, no_a=True,
                         desc=['The most fearsome mammal to have ever lived, this bear',
                               'lived during the Pleistocene epoch.',
                               'It is more than twice the size of the modern-day grizzly bear.']))

        self.add(Monster('Glyptodon perforatus', skin=('o', libtcod.brass),
                         branch='a', attack=0.2, defence=20.0, range=7, count=7, no_a=True,
                         explodeimmune=True, level=6, heatseeking=True,
                         desc=['A relative of the armadillo from the Pleistocene epoch.',
                               'Unlike the modern armadillos, this armored monstrocity is',
                               'the size and weight of a car.']))

        self.add(Monster('Pteranodon longiceps', skin=('B', libtcod.lightest_lime),
                         branch='a', attack=3.0, defence=4.0, range=10, level=7, count=8,
                         no_a=True,
                         desc=['A flying reptile that had a wingspan of over 6 meters!',
                               'It was a very common animal during the Cretaceous period.']))

        self.add(Monster('Hippopotamus gorgops', skin=('Q', libtcod.light_azure),
                         branch='a', attack=8.0, defence=2.0, range=4, level=7, count=5, no_a=True,
                         desc=['This hippo from the Miocene period was much, much larger than',
                               'its modern-day living relatives.']))

        self.add(Monster('Velociraptor mongoliensis', skin=('d', libtcod.yellow),
                         branch='a', attack=1.5, defence=1.0, range=20, level=8, count=24,
                         no_a=True, summon=('Velociraptor mongoliensis', 4),
                         desc=['A small theropod from the Cretaceous period.',
                               'It is about the size of a chicken and is covered with',
                               'bright, feathery plumage. It has a relatively large, ',
                               'dangerous-looking beak.',
                               'It was also a vicious pack-hunting carnivore.']))

        self.add(Monster('Titanoceratops ouranos', skin=('D', libtcod.sepia), branch='a',
                         attack=11.0, defence=4.0, range=3, level=8, count=8,
                         no_a=True,
                         desc=['The largest of many species of triceratops.',
                               'You recognize the familiar triceratops profile from',
                               'numerous film, cartoon and book descriptions of this',
                               'dinosaur.']))

        self.add(Monster('Indricotherium transouralicum', skin=('Q', libtcod.sepia),
                         branch='a', attack=1.0, defence=6.0, range=7, level=9, count=6,
                         no_a=True,
                         desc=['Named after the mystical Indrik-Beast, this is the ',
                               'largest land mammal ever to have lived!',
                               'A relative of the rhinoceros, it looks like a ridiculously',
                               'muscled cross between wooly mammoth and a giraffe.',
                               'Its long neck reaches to 8 meters in height, more than',
                               'a 3-story building!']))

        self.add(Monster('Mammuthus primigenius', skin=('Q', libtcod.darker_amber),
                         branch='a', attack=3.0, defence=4.0, range=6, level=9, count=6,
                         no_a=True,
                         desc=['Also known as the wooly mammoth.']))

        self.add(Monster('Tyrannosaurus rex', skin=('D', libtcod.light_lime), branch='a',
                         attack=15.0, defence=15.0, range=20, level=10, count=1, no_a=True,
                         confimmune=True,
                         desc=['The Tyrant Lizard King, in person. No introduction necessary.']))

        self.add(Monster('Sauroposeidon proteles', skin=('D', libtcod.light_azure), branch='a',
                         attack=1.0, defence=64.0, range=10, level=11, count=1, no_a=True,
                         slow=True, confimmune=True, explodeimmune=True, radimmune=True,
                         desc=['The Earthshaker-Lizard. A sauropod so truly, veritably huge that',
                               'it might have indeed caused earthquakes merely by walking.',
                               "Also, the World's Largest Dinosaur.",
                               'For a creature so large, researchers have wondered how it survived',
                               'with its tiny brain.']))

        # Eldritch/Faerie dungeon branch

        self.add(Monster('gibbering maniac', skin=('h', libtcod.gray),
                         attack=0.3, defence=0.1, range=3, level=1,
                         itemdrop='booze', count=7, branch='b',
                         desc=['Eldritch horrors have driven this poor wretch',
                               'to the cusp of insanity.',
                               "He's probably an alumnus of Miskatonic University."]))

        self.add(Monster('chanterelle', skin=('x', libtcod.orange),
                         attack=0.0, defence=0.3, range=1, level=1,
                         itemdrop='mushrooms', confimmune=True, count=6, branch='b',
                         desc=['It looks delicious.']))

        self.add(Monster('brownie', skin=('h', libtcod.light_red),
                         attack=1.5, defence=0.2, range=8, level=2, count=4, branch='b',
                         desc=['Once a friendly house spirit, this small fey humanoid',
                               'has been driven to hate humanity after years of neglect',
                               'and abuse by its master.']))

        self.add(Monster('pixie', skin=('h', libtcod.green),
                         attack=1.0, defence=0.7, range=6, level=2, count=4, branch='b',
                         desc=['A magical creature that has been driven underground',
                               'by human pollution and habitat loss.']))

        self.add(Monster('sprite', skin=('f', libtcod.light_lime),
                         attack=0.5, defence=0.9, range=8, level=2, count=3, branch='b',
                         desc=['A ghost of a dead faerie.']))

        self.add(Monster('nematode', skin=('w', libtcod.yellow),
                         attack=0, psyattack=2.0, defence=0.1, range=30, psyrange=4,
                         level=3, count=5, branch='b',
                         desc=['A gigantic (5 meter long) yellow worm.',
                               'It has no visible eyes, but instead has a ',
                               'giant, bulging, pulsating brain.']))

        self.add(Monster('shoggoth', skin=('x', libtcod.dark_sepia),
                         attack=0.7, psyattack=0.5, defence=0.6, range=5, psyrange=3, level=3,
                         count=3, branch='b',
                         desc=['A creature of a terrible servant race created by the',
                               'Elder Things. A shapeless congeries of protoplasmic',
                               'bubbles, faintly self-luminous.']))

        self.add(Monster('ghost', skin=('h', libtcod.dark_grey),
                         attack=0.5, defence=2.5, range=7, level=3,
                         hungerattack=True, count=3, branch='b', fireimmune=True,
                         desc=['A spirit of an adventurer that perished in these',
                               'terrible and wondorous caves.',
                               'Its eyes are glowing with a malignant hunger.']))

        self.add(Monster('satyr', skin=('h', libtcod.light_sepia),
                         attack=7.0, defence=0.01, range=5, level=4,
                         count=4, branch='b',
                         desc=["A savage worshipper of the Mad God Dionysus.",
                                'He is completely naked and gibbering wildly.']))

        self.add(Monster('sylphid', skin=('f', libtcod.light_blue),
                         attack=1.4, defence=1.4, range=4, level=4,
                         count=4, psyattack=0.1, psyrange=10, branch='b',
                         desc=['An air elemental. It takes the form of a beautiful',
                               'young woman.']))

        self.add(Monster('chthonian', skin=('W', libtcod.dark_blue),
                         attack=4.0, psyattack=2.0, defence=1.0, range=8, psyrange=2,
                         level=5, count=4, straightline=True, stoneeating=True, branch='b',
                         desc=['An immense squid-like creature that burrows in the',
                               "dark, loathsome depths of the Earth's crust.",
                               'It is covered in slime and is accompanied by a faint',
                               'chanting sound.']))

        self.add(Monster('gnophkeh', skin=('h', libtcod.gray),
                         attack=7.0, defence=1.0, range=18,
                         level=5, count=4, branch='b',
                         desc=['A member of a race of disgusting, hairy cannibal humanoids.']))

        self.add(Monster('sleep faerie', skin=('f', libtcod.light_pink),
                         attack=1.0, defence=1.0, range=9, level=6, count=5,
                         sleepattack=True, flying=True, branch='b',
                         desc=["A tiny fay creature dressed in pink ballet clothes.",
                               "It looks adorable."]))

        self.add(Monster('aelf', skin=('f', libtcod.green),
                         attack=3.0, defence=2.0, range=20, level=6, count=5,
                         confimmune=True, flying=True, branch='b', fireimmune=True,
                         desc=["A faery creature from the elemental plane of Aelfrice."]))

        self.add(Monster('leipreachan', skin=('f', libtcod.azure),
                         attack=2.5, defence=1.5, range=9, level=7, count=5,
                         hungerattack=True, branch='b',
                         desc=['A fay creature in the form of a dirty, lecherous old man.']))

        self.add(Monster('black knight', skin=('k', libtcod.darker_grey),
                         attack=6.0, defence=4.5, range=8, level=7, count=6, branch='b',
                         desc=['An evil humanoid in black cast-iron armor.',
                               'He is armed with a longsword.']))

        self.add(Monster('frost giant', skin=('k', libtcod.lighter_sky),
                         attack=6.0, defence=4.5, range=8, level=8, count=5, branch='b',
                         desc=['A humanoid about twice the size of a human.',
                               'He is an evil, emotionless immigrant from the dark',
                               'planes of Jotunheim.']))

        self.add(Monster('Oberon', skin=('F', libtcod.purple),
                         attack=3.0, defence=3.0, range=10, level=9, count=1,
                         flying=True, explodeimmune=True, confimmune=True,
                         psyrange=8, psyattack=2.0, branch='b', no_a=True,
                         desc=['A faerie king.',
                               'He takes on the appearance of a 2 meter tall',
                               'handsome man, wearing a delicate crown.']))

        self.add(Monster('Caliban', skin=('H', libtcod.sea),
                         attack=7.0, defence=7.0, range=10, level=9, count=1,
                         confimmune=True, branch='b', no_a=True,
                         desc=["A deformed beast-man. Half-devil on his father's side,"
                               'he is a resentful slave of Prospero.']))

        self.add(Monster('Prospero', skin=('H', libtcod.purple),
                         attack=2.0, defence=7.0, range=20, level=10, count=1,
                         explodeimmune=True, flying=True, confimmune=True,
                         psyrange=2, psyattack=2.0, branch='b',
                         summon=('black knight', 2), no_a=True,
                         desc=["Self-styled royalty, self-styled wizard, self-styled",
                               'ruler of this dungeon.',
                               'He has instilled unthinking loyalty into his subjects',
                               'and slaves.']))

        self.add(Monster('Yog-Sothoth', skin=('X', libtcod.pink),
                         attack=2.0, defence=7.0, range=20, level=10, count=1,
                         explodeimmune=True, flying=True, confimmune=True,
                         psyrange=20, psyattack=2.0, branch='b', fireimmune=True,
                         summon=('Prospero', 2), no_a=True,
                         desc=['An Outer God: The Lurker at the Threshold, The Key and the Gate,',
                               'The Beyond One, Opener of the Way, The All-in-One',
                               'and the One-in-All.',
                               ' "Only a congeries of iridescent globes, yet stupendous',
                               '  in its malign suggestiveness."']))


        # Cyberspace dungeon branch.


        self.add(Monster('cyberpunk', skin=('h', libtcod.light_purple),
                         attack=0.2, defence=0.1, range=4, level=1,
                         itemdrop='booze', count=6, branch='c',
                         desc=['Stoned out of his gourd, he is chatting with his avatar',
                               'in cyberspace while wearing VR glasses.']))

        self.add(Monster('cramration', skin=('x', libtcod.pink),
                         attack=0.0, defence=0.2, range=1, level=1,
                         itemdrop='mushrooms', confimmune=True, count=6, branch='c',
                         desc=['A mushroom/pork genetically engineered vegetarian',
                               'food ration. It sports tiny legs.']))

        self.add(Monster('snorlax', skin=('v', libtcod.purple),
                         attack=1.0, defence=1.2, range=5, slow=True, level=2, count=5,
                         branch='c',
                         desc=['A 2 meter tall, enourmously obese creature of',
                               'some indeterminate cat-bear-dog race. It has',
                               'a pinkish-purple hide.']))

        self.add(Monster('charizard', skin=('v', libtcod.green),
                         attack=1.0, defence=0.4, range=8, level=2, count=5,
                         branch='c',
                         desc=['A creature of indeterminate race, looking like',
                               'some sort of small dragonish flying reptile.',
                               'It is greenish in color.']))

        self.add(Monster('squirtle', skin=('v', libtcod.light_blue),
                         attack=0.4, defence=1.0, range=6, level=2, count=7,
                         heatseeking=True, branch='c',
                         desc=['A bluish creature of indeterminate race.',
                               'It looks like a cute turtle.']))

        self.add(Monster('spore plant', skin=('x', libtcod.dark_yellow),
                         attack=0.3, defence=0.2, range=7, level=3,
                         itemdrop='bomb', confimmune=True, count=7,
                         heatseeking=True, branch='c',
                         desc=['A large plantlike carnivorous creature.',
                               'It has large bulbous appendages growing out of its stalk.',
                               'It looks like it is radiating heat from the inside.']))

        self.add(Monster('scavenger drone', skin=('Z', libtcod.silver),
                         attack=1.0, defence=24.0, explodeimmune=True, range=30,
                         confimmune=True, slow=True, level=3, count=4, branch='c',
                         fireimmune=True,
                         desc=['A remotely-controlled robot used for exploring the dungeon.']))

        self.add(Monster('memetic virus', skin=('v', libtcod.dark_gray),
                         attack=0.3, defence=0.3, explodeimmune=True, radimmune=True,
                         branch='c', fireimmune=True,
                         range=30, level=3, count=16, summon=('memetic virus', 5),
                         desc=["It doesn't exist. It's a memetic virus."]))

        self.add(Monster('spore', skin=('x', libtcod.pink),
                         attack=0, defence=0.2, range=30, level=4,
                         itemdrop='bomb', heatseeking=True, selfdestruct=True,
                         confimmune=True, count=7, flying=True, branch='c',
                         desc=['A pulsating pink spherical spore, about 1 meter in diameter.',
                               'It is levitating.',
                               'It looks like it is radiating heat from the inside.']))

        self.add(Monster('xenomorph', skin=('X', libtcod.silver),
                         attack=7.0, defence=7.0, range=5, level=4,
                         count=2, confimmune=True, radimmune=True, branch='c', fireimmune=True,
                         desc=["A horrifying alien creature. It looks like a giant,",
                               "very evil insect. It is truly scary."]))

        self.add(Monster('cthulhumon', skin=('v', libtcod.gray),
                         attack=3.0, psyattack=2.0, defence=1.0, range=8, psyrange=8,
                         level=5, confimmune=True, count=4, branch='c',
                         desc=['The other Pokemon nobody told you about.']))

        self.add(Monster('cyberdemon', skin=('Z', libtcod.red),
                         attack=7.0, defence=2.0, range=4, level=5, count=2,
                         explodeimmune=True, summon=('spore', 2), branch='c',
                         desc=['A 3 meter tall hellish demon-robot hybrid.',
                               'Fleshy parts of its demonic body have rotted away,',
                               'to be replaced with crude stainless-steel robotic parts.']))

        self.add(Monster('shai-hulud', skin=('W', libtcod.gray),
                         attack=2.0, defence=4.5, explodeimmune=True, range=30,
                         level=6, count=4, straightline=True, stoneeating=True,
                         heatseeking=True, branch='c',
                         desc=['A giant worm. It is gray in color and has a skin made of something like granite.',
                               'It is about 15 meters in length.']))

        self.add(Monster('klingon', skin=('k', libtcod.brass),
                         attack=5.0, defence=0.5, range=5, level=6,
                         count=5, branch='c',
                         desc=["A member of a chivalrous warrior race of extraterrestrial aliens."]))

        self.add(Monster('autobot', skin=('z', libtcod.silver),
                         attack=1.5, defence=1.5, range=15, level=7,
                         itemdrop='bomb', confimmune=True, radimmune=True,
                         explodeimmune=True, count=7, branch='c',
                         desc=['An extraterrestrial sentient robot from the planet',
                               'Cybertron. Powered by the energy source Nucleon,',
                               'he fights for intergalactic Good.']))

        self.add(Monster('T-1 terminator', skin=('z', libtcod.lightest_sepia),
                         attack=0.4, defence=0.4, range=7, level=7,
                         itemdrop='radblob', confimmune=True, count=7,
                         radimmune=True, heatseeking=True, branch='c', fireimmune=True,
                         desc=["The very first model in Cyberdine's robot-killer lineup.",
                               '(Brought to you by Skynet.)']))

        self.add(Monster('decepticon', skin=('z', libtcod.dark_gray),
                         attack=1.5, defence=1.5, range=15, level=8,
                         confimmune=True, radimmune=True, branch='c',
                         explodeimmune=True, count=7, summon=('autobot', 3),
                         desc=['An extraterrestrial sentient robot from the planet',
                               'Cybertron. Powered by the energy source Nucleon,',
                               'he fights for intergalactic Evil.']))

        self.add(Monster('triffid', skin=('x', libtcod.peach),
                         attack=2.0, defence=2.0, range=5, level=8, count=16,
                         itemdrop='triffidlarva', confimmune=True, branch='c',
                         desc=['A carnivorous plant. It is a sneaky pest that is very',
                               'hard to get rid of.']))

        self.add(Monster('mosura-chan', skin=('x', libtcod.dark_lime),
                         attack=0, defence=0.2, range=30, level=9,
                         itemdrop='radblob', selfdestruct=True,
                         radimmune=True, explodeimmune=True, branch='c',
                         confimmune=True, count=16, flying=True, no_a=True,
                         desc=['A bird-sized, moth-like creature.',
                               'It has a strange green glow.']))

        self.add(Monster('Wintermute', skin=('V', libtcod.azure),
                         attack=0.5, defence=4.0, range=30, sleepattack=True,
                         confimmune=True, explodeimmune=True, radimmune=True, flying=True,
                         no_a=True, count=2, level=9, branch='c', fireimmune=True,
                         desc=["A manifestation of the powerful AI construct named 'Wintermute'."]))

        self.add(Monster('Voltron', skin=('Z', libtcod.white),
                         attack=6.0, defence=5.0, range=5, level=10, count=1, no_a=True,
                         explodeimmune=True, confimmune=True, branch='c', heatseeking=True,
                         fireimmune=True,
                         desc=['Defender of the Universe.']))

        self.add(Monster('Gojira-sama', skin=('G', libtcod.green),
                         attack=6.0, defence=5.0, range=10, level=11, count=1,
                         radimmune=True, explodeimmune=True, branch='c', no_a=True,
                         summon=('mosura-chan', 3), itemdrop=['gbomb', 'radsuit'],
                         desc=['She really hates Japan after what they did',
                               'to the nuclear power plant.']))

        # Urthian dungeon branch.


        self.add(Monster('omophagist', skin=('h', libtcod.dark_purple),
                         attack=0.3, defence=0.1, range=4, level=1,
                         count=4, branch='d',
                         desc=['A poor, degenerate inhabitant of the poorest parts of the City.',
                               '(Those parts that are composed of mostly ancient ruins.)',
                               'He might be a little insane and a cannibal, as well.']))

        self.add(Monster('avern', skin=('x', libtcod.green),
                         attack=0.3, defence=0.01, range=1, level=1,
                         itemdrop='avern', confimmune=True, count=4, branch='d',
                         desc=['A poisonous, carnivorous species of plant.',
                               '(It might actually be at least in part an animal.)']))

        self.add(Monster('armiger', skin=('k', libtcod.silver),
                         attack=2.0, defence=1.0, range=8, level=2,
                         count=4, branch='d',
                         desc=['A member of the warrior caste.']))

        self.add(Monster('exultant', skin=('h', libtcod.gold),
                         attack=0.5, defence=0.5, range=8, level=2,
                         count=3, branch='d', summon=('armiger', 2),
                         desc=['A member of the nobility caste.']))

        self.add(Monster('aquastor', skin=('v', libtcod.gray),
                         attack=1.5, defence=1.0, range=10, level=3, count=4,
                         hungerattack=True, branch='d', flying=True,
                         desc=['An entity formed by the power of a concentrated thought',
                               'and which assumed a physical form.']))

        self.add(Monster('eidolon', skin=('v', libtcod.white),
                         attack=0.0, defence=2.0, range=8, level=3,
                         count=4, psyattack=1.5, psyrange=7, branch='d', flying=True,
                         fireimmune=True,
                         desc=["A spirit-image of a living or dead person;",
                               "a shade or phantom look-alike of the human form."]))

        self.add(Monster('destrier', skin=('q', libtcod.dark_gray),
                         attack=2.5, defence=1.5, range=6, level=4, count=3,
                         branch='d',
                         desc=['A mount; A highly modified horse, possessing',
                               'clawed feet (for better traction) and large canine teeth.',
                               'It is carnivorous.']))

        self.add(Monster('cacogen', skin=('u', libtcod.silver),
                         attack=0.5, defence=1.0, range=10, level=4, count=3,
                         summon=('eidolon', 2), itemdrop='radblob',
                         branch='d',
                         desc=['In fact an extraterrestrial who disguises itself as an',
                               'urthly monster.']))

        self.add(Monster('ascian', skin=('h', libtcod.gray),
                         attack=2.0, defence=1.0, range=5, level=5,
                         psyattack=1.5, psyrange=10,
                         count=4, branch='d',
                         desc=['A human from Ascia, the tyrannical empire ruled',
                               'by the evil Abaia. His mind is warped to the point',
                               'where he cannot any longer speak or understand any',
                               'real human language.']))

        self.add(Monster('smilodon', skin=('Q', libtcod.dark_orange),
                         attack=2.5, defence=1.5, range=12, level=5, count=3,
                         branch='d',
                         desc=['An ancient genetically-engineered feline animal.',
                               'It looks somewhat like the familiar sabre-toothed tiger.']))

        self.add(Monster('alzabo', skin=('u', libtcod.darkest_red),
                         attack=2.0, defence=2.0, range=12, level=6, count=3,
                         branch='d', itemdrop='alzabobrain',
                         desc=[' "The red orbs of the alzabo were something more, neither',
                               '  the intelligence of humankind nor the the innocence of',
                               '  the brutes. So a fiend might look, I thought, when it had',
                               '  at last struggled up from the pit of some dark star."']))

        self.add(Monster('undine', skin=('u', libtcod.darkest_blue),
                         attack=0.7, defence=3.0, range=10, level=6, count=5,
                         sleepattack=True, branch='d',
                         desc=["A monstrous slave-servant of its megetherian overlords.",
                               'It looks like humongous, deformed mermaid.']))

        self.add(Monster('Scylla', skin=('U', libtcod.white),
                         attack=10, defence=10, range=15, level=7, count=1,
                         branch='d', no_a=True,
                         desc=['A megatherian: an evil, immortal, gigantic creature of',
                               'possibly extraterrestrial origin. They are hellbent on ruling',
                               'Urth. They are powerful enough and amoral enough to be',
                               'essentially equal to gods.']))

        self.add(Monster('Uroboros', skin=('U', libtcod.light_green),
                         attack=10, defence=10, range=15, level=8, count=1,
                         branch='d', confimmune=True, no_a=True,
                         desc=['A megatherian: an evil, immortal, gigantic creature of',
                               'possibly extraterrestrial origin. They are hellbent on ruling',
                               'Urth. They are powerful enough and amoral enough to be',
                               'essentially equal to gods.']))

        self.add(Monster('Erebus', skin=('U', libtcod.light_pink),
                         attack=10, defence=10, range=15, level=9, count=1,
                         branch='d', confimmune=True, explodeimmune=True, no_a=True,
                         fireimmune=True,
                         desc=['A megatherian: an evil, immortal, gigantic creature of',
                               'possibly extraterrestrial origin. They are hellbent on ruling',
                               'Urth. They are powerful enough and amoral enough to be',
                               'essentially equal to gods.']))

        self.add(Monster('Arioch', skin=('U', libtcod.light_sky),
                         attack=10, defence=10, range=15, level=10, count=1, no_a=True,
                         branch='d', confimmune=True, explodeimmune=True, radimmune=True,
                         fireimmune=True,
                         desc=['A megatherian: an evil, immortal, gigantic creature of',
                               'possibly extraterrestrial origin. They are hellbent on ruling',
                               'Urth. They are powerful enough and amoral enough to be',
                               'essentially equal to gods.']))

        self.add(Monster('Abaia', skin=('U', libtcod.grey),
                         attack=10, defence=10, range=15, level=11, count=1,
                         branch='d', confimmune=True, explodeimmune=True, radimmune=True,
                         fireimmune=True,
                         summon=('undine', 3), no_a=True, itemdrop='gluegun',
                         desc=['A megatherian: an evil, immortal, gigantic creature of',
                               'possibly extraterrestrial origin. They are hellbent on ruling',
                               'Urth. They are powerful enough and amoral enough to be',
                               'essentially equal to gods.']))

        # Hyborian dungeon branch

        self.add(Monster('peasant', skin=('h', libtcod.dark_sepia),
                         attack=0.1, defence=0.2, range=3, level=1,
                         itemdrop='booze', count=9, branch='e',
                         desc=["He's dirty, suspicious and closed-minded."]))

        self.add(Monster('lichen', skin=('x', libtcod.light_purple),
                         attack=0.3, defence=0.2, range=1, level=1, branch='e',
                         itemdrop='mushrooms', confimmune=True, count=9,
                         desc=['Looks yummy.']))

        self.add(Monster('Aquilonian marshall', skin=('h', libtcod.dark_blue),
                         attack=0.5, defence=0.5, range=6, level=2, count=8,
                         summon=('Aquilonian marshall', 5), branch='e',
                         desc=['A mercenary, sent from the Aquilonian cities on',
                               'the surface to partol these dangerous tunnels.']))

        self.add(Monster('giant spider', skin=('X', libtcod.gray),
                         attack=0.7, defence=0.7, range=5, level=2, count=8,
                         branch='e',
                         desc=['A huge, very ugly and disturbing spider.']))

        self.add(Monster('Turanian nomad', skin=('h', libtcod.orange),
                         attack=1.3, defence=0.4, range=7, level=2, count=8,
                         branch='e',
                         desc=['A nomad from the boundless steppes of Turania.']))

        self.add(Monster('Cimmerian pirate', skin=('h', libtcod.red),
                         attack=1.2, defence=0.6, range=7, level=3, count=8,
                         branch='e', summon=('Cimmerian pirate', 4),
                         desc=['A cruel-hearted Cimmerian tribesman, turned to piracy',
                               'in search of loot and women.',
                               "The poor man is probably looking for treasure in these",
                               'caves.']))

        self.add(Monster('giant serpent', skin=('S', libtcod.darkest_lime),
                         attack=1.8, defence=0.5, range=9, level=3, count=8,
                         branch='e',
                         desc=['A malevolent nag, a giant snake borne from the',
                               'unholy mixture of human and cobra seed.']))

        self.add(Monster('Hyperborean barbarian', skin=('h', libtcod.peach),
                         attack=2.2, defence=0.9, range=6, level=3, count=6,
                         branch='e',
                         desc=['A barbarian who hails from one of the hearty tribes',
                               'of great frosty Hyperborea.']))

        self.add(Monster('Stygian priest', skin=('h', libtcod.light_sepia),
                         attack=1.0, defence=1.0, range=8, level=4, count=6,
                         branch='e', summon=('giant serpent', 3),
                         desc=['Hailing from the banks of the river Stygs, he has',
                               'a swarthy complexion and sports a completely shaved head.',
                               'He is skilled in the arcane worship of the enigmatic',
                               'Stygian gods.']))

        self.add(Monster('giant slug', skin=('w', libtcod.purple),
                         attack=0.7, defence=2.8, range=4, level=4, count=10,
                         branch='e', summon=('giant slug', 2),
                         desc=['It is truly giant and truly disgusting.']))

        self.add(Monster('zombie', skin=('y', libtcod.silver),
                         attack=1.8, defence=2.9, range=3, level=4, count=10,
                         branch='e',
                         desc=['A decomposed corpse brought back to unlife by',
                               'the darkest arts.']))

        self.add(Monster('Amazon warrior', skin=('h', libtcod.pink),
                         attack=1.8, defence=1.8, range=10, level=5, count=8,
                         branch='e',
                         desc=['She is a woman-warrior from the enigmatic Amazonian tribe.',
                               'She hates men.']))

        self.add(Monster('wolf', skin=('q', libtcod.silver),
                         attack=3.5, defence=3.0, range=7, level=5, count=10,
                         branch='e',
                         desc=['A man-eating wolf.']))

        self.add(Monster('Thulian price', skin=('h', libtcod.sky),
                         attack=1.0, defence=1.0, range=18, level=6, count=8,
                         branch='e', summon=('Amazon warrior', 1),
                         desc=['Ultima Thule is the mystical land of fancy and dark legend.',
                               "You're not sure he is really from Thule, much less a real price."]))

        self.add(Monster('cannibal', skin=('h', libtcod.dark_purple),
                         attack=2.0, defence=2.0, range=15, level=6, count=8,
                         branch='e',
                         desc=['A deranged human who developed an unnatural, unholy',
                               'addiction to human flesh.']))

        self.add(Monster('Lemurian wizard', skin=('h', libtcod.dark_han),
                         attack=1.2, defence=1.2, range=15, level=7, count=6,
                         branch='e', summon=('cannibal', 2),
                         desc=['Lemuria is the mythical island-empire of evil magicians',
                               'and demon-worshippers.']))

        self.add(Monster('apeman', skin=('h', libtcod.light_pink),
                         attack=2.5, defence=2.5, range=10, level=7, count=8,
                         branch='e',
                         desc=['Part human, part ape, if he has any intelligence, then his',
                               'gaze does not betray any, only pure malevolence.']))

        self.add(Monster('Atlantian sorceror', skin=('h', libtcod.light_han),
                         attack=1.2, defence=1.2, range=15, level=8, count=6,
                         branch='e', summon=('evil demon', 2),
                         desc=['Atlantis is another evil island-empire, the competitor',
                               'to Lemuria in the dark art of demon-worship.']))

        self.add(Monster('evil demon', skin=('Y', libtcod.red),
                         attack=1.0, defence=1.6, range=10, level=8, count=6,
                         branch='e', summon=('wolf', 2), fireimmune=True,
                         desc=['Summoned from the depths of Infernus to commit',
                               'unspeakable deeds of evil and hatred.']))

        self.add(Monster('carrion crawler', skin=('w', libtcod.white),
                         attack=2.0, defence=2.0, range=5, level=9, count=16,
                         itemdrop='cclarva', branch='e',
                         desc=['A creature that looks like a maggot,',
                               'only a thousand times bigger.']))

        self.add(Monster('vampire', skin=('Y', libtcod.blue),
                         attack=2.5, defence=2.5, range=15, level=9, count=5,
                         branch='e', summon=('zombie', 1),
                         desc=['One of the Elder Ones, the most ancient and powerful of',
                               'vampires.']))

        self.add(Monster('Conan', skin=('K', libtcod.sepia),
                         attack=7.5, defence=5.5, range=8, level=10, count=1,
                         confimmune=True, itemdrop='excalibur', branch='e', no_a=True,
                         desc=['A well-muscled adventurer,',
                               'he looks like he just stepped off a movie poster.',
                               "He hates competition."]))

        self.add(Monster('Crom', skin=('K', libtcod.peach),
                         attack=7.5, defence=7.5, range=10, level=10, count=1,
                         explodeimmune=True, fireimmune=True, branch='e',
                         confimmune=True, summon=('Conan', 1), no_a=True,
                         desc=['The most high god of all Cimmerians, Crom is the god',
                               'of valor and battle. He is a dark, vengeful and',
                               'judgemental god.']))




    def add(self, mon):
        if mon.branch not in self.monsters:
            self.monsters[mon.branch] = {}

        mms = self.monsters[mon.branch]

        if mon.level not in mms:
            mms[mon.level] = [mon]
        else:
            mms[mon.level].append(mon)


    def clear_gencount(self):
        for v2 in self.monsters.itervalues():
            for v in v2.itervalues():
                for m in v:
                    m.gencount = 0


    def find(self, name, n, itemstock):
        for v2 in self.monsters.itervalues():
            for v in v2.itervalues():
                for m in v:
                    if m.name == name:
                        l = []

                        if m.gencount >= m.count:
                            return l

                        n2 = min(n, m.count - m.gencount)
                        m.gencount += n2

                        for x in xrange(n2):
                            mm = copy.copy(m)
                            if mm.itemdrop:
                                if type(mm.itemdrop) == type(''):
                                    item = itemstock.get(mm.itemdrop)
                                    if item:
                                        mm.items = [item]
                                else:
                                    item = [itemstock.get(ii) for ii in mm.itemdrop]
                                    mm.items = [ii for ii in item if ii]
                            l.append(mm)

                        return l

        return []

    def generate(self, branch, level, itemstock):
        #for k,v in self.monsters.iteritems():
        #    n = sum(sum(m.count for m in v2) for v2 in v.itervalues())
        #    at = sum(sum(m.attack for m in v2) for v2 in v.itervalues())
        #    de = sum(sum(m.defence for m in v2) for v2 in v.itervalues())
        #    atw = sum(sum(m.attack*m.level for m in v2) for v2 in v.itervalues())
        #    dew = sum(sum(m.defence*m.level for m in v2) for v2 in v.itervalues())
        #    print '//', k, n, at/n, de/n, '|', atw/n, dew/n

        while level > 0 and level not in self.monsters[branch]:
            level -= 1

        m = self.monsters[branch][level]
        tmp = None

        for x in xrange(6):
            if x >= 5:
                return None
            tmp = m[random.randint(0, len(m)-1)]
            if tmp.gencount >= tmp.count:
                continue
            tmp.gencount += 1
            break

        m = copy.copy(tmp)

        if m.itemdrop:
            if type(m.itemdrop) == type(''):
                i = itemstock.get(m.itemdrop)
                if i:
                    m.items = [i]
            else:
                item = [itemstock.get(ii) for ii in m.itemdrop]
                m.items = [ii for ii in item if ii]

        return m

    def death(self, mon):
        if not mon.branch:
            return

        if mon.level not in self.monsters[mon.branch]:
            return (len(self.monsters[mon.branch]) == 0)

        m = self.monsters[mon.branch][mon.level]

        for x in xrange(len(m)):
            if mon.name == m[x].name:
                if m[x].count <= 1:
                    del m[x]
                else:
                    m[x].count -= 1
                break

        if len(m) == 0:
            del self.monsters[mon.branch][mon.level]

        return (len(self.monsters) == 0)



class Feature:
    def __init__(self, walkable=False, visible=False, skin=('=', libtcod.white),
                 name="something strange", stairs=False, sticky=False, water=None,
                 s_shrine=False, b_shrine=False, v_shrine=False, height=-10,
                 shootable=False, warm=False, branch=None):
        self.walkable = walkable
        self.visible = visible
        self.water = water
        self.skin = skin
        self.stairs = stairs
        self.name = name
        self.sticky = sticky
        self.s_shrine = s_shrine
        self.b_shrine = b_shrine
        self.v_shrine = v_shrine
        self.height = height
        self.shootable = shootable
        self.warm = warm
        self.branch = branch


class FeatureStock:
    def __init__(self):
        self.f = {}

        self.f['>'] = Feature(walkable=True, visible=True, skin=('>', libtcod.white),
                              stairs=1, name='a hole in the floor')

        self.f['1'] = Feature(walkable=True, visible=True, skin=('>', libtcod.lime),
                              stairs=1, name='a hole in the floor', branch='a')

        self.f['2'] = Feature(walkable=True, visible=True, skin=('>', libtcod.crimson),
                              stairs=1, name='a hole in the floor', branch='b')

        self.f['3'] = Feature(walkable=True, visible=True, skin=('>', libtcod.sky),
                              stairs=1, name='a hole in the floor', branch='c')

        self.f['4'] = Feature(walkable=True, visible=True, skin=('>', libtcod.dark_gray),
                              stairs=1, name='a hole in the floor', branch='d')

        self.f['5'] = Feature(walkable=True, visible=True, skin=('>', libtcod.light_gray),
                              stairs=1, name='a hole in the floor', branch='e')

        self.f['*'] = Feature(walkable=True, visible=False, skin=('*', libtcod.lightest_green),
                              name='rubble')

        self.f['^'] = Feature(walkable=True, visible=True, skin=(250, libtcod.red),
                              sticky=True, name='a cave floor covered with glue')

        self.f['s'] = Feature(walkable=True, visible=True, skin=(234,  libtcod.darker_grey),
                              s_shrine=True, name='a shrine to Shiva')

        self.f['b'] = Feature(walkable=True, visible=True, skin=(127, libtcod.white),
                              b_shrine=True, name='a shrine to Brahma')

        self.f['v'] = Feature(walkable=True, visible=True, skin=(233, libtcod.azure),
                              v_shrine=True, name='a shrine to Vishnu')

        self.f[':'] = Feature(walkable=False, visible=False, skin=(9, libtcod.white),
                              name='a column', height=0)

        self.f['h'] = Feature(walkable=True, visible=True, skin=(242, libtcod.white),
                              stairs=6, name='a dropchute')

        self.f['a'] = Feature(walkable=True, visible=True, skin=(254, libtcod.green),
                              name='an abandoned altar stone')

        self.f['@'] = Feature(walkable=True, visible=True, skin=(15, libtcod.yellow),
                              name='a hearth', warm=True)


        self.f['='] = Feature(walkable=False, visible=True, skin=(196, libtcod.gray),
                              name='barricades', shootable=True)
        self.f['l'] = Feature(walkable=False, visible=True, skin=(179, libtcod.gray),
                              name='barricades', shootable=True)
        self.f['r'] = Feature(walkable=False, visible=True, skin=(218, libtcod.gray),
                              name='barricades', shootable=True)
        self.f['q'] = Feature(walkable=False, visible=True, skin=(191, libtcod.gray),
                              name='barricades', shootable=True)
        self.f['p'] = Feature(walkable=False, visible=True, skin=(192, libtcod.gray),
                              name='barricades', shootable=True)
        self.f['d'] = Feature(walkable=False, visible=True, skin=(217, libtcod.gray),
                              name='barricades', shootable=True)


        self.f['|'] = Feature(walkable=False, visible=False, skin=(186, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['-'] = Feature(walkable=False, visible=False, skin=(205, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['+'] = Feature(walkable=False, visible=False, skin=(206, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['R'] = Feature(walkable=False, visible=False, skin=(201, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['L'] = Feature(walkable=False, visible=False, skin=(200, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['T'] = Feature(walkable=False, visible=False, skin=(203, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['F'] = Feature(walkable=False, visible=False, skin=(204, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['J'] = Feature(walkable=False, visible=False, skin=(202, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['7'] = Feature(walkable=False, visible=False, skin=(187, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['/'] = Feature(walkable=False, visible=False, skin=(188, libtcod.white),
                              name='a smooth stone wall', height=0)
        self.f['Z'] = Feature(walkable=False, visible=False, skin=(185, libtcod.white),
                              name='a smooth stone wall', height=0)

        self.f['Y'] = Feature(walkable=False, visible=False, skin=(157, libtcod.green),
                              name='a tree', height=5)
        self.f['!'] = Feature(walkable=True, visible=False, skin=(173, libtcod.dark_green),
                              name='a giant fern')

        self.f['w'] = Feature(walkable=True, visible=True, skin=('-', libtcod.sky),
                              water=True, name='a pool of water')


class Vault:
    def __init__(self, syms=None, pic=None, chance=1, level=(1,10), count=10, branch=None):
        self.syms = syms
        self.pic = pic
        self.chance = chance
        self.level = level
        self.count = count
        self.branch = branch

    def postprocess(self):
        a = None
        for k,v in self.syms.iteritems():
            if v and v[-1]:
                a = k

        self.h = len(self.pic)
        self.w = max(len(x) for x in self.pic)

        for y in xrange(len(self.pic)):
            for x in xrange(len(self.pic[y])):
                if self.pic[y][x] == a:
                    self.anchor = (x, y)
                    return

        self.anchor = (0, 0)


class VaultStock:

    def __init__(self):
        self.vaults = {}

        syms = {' ': None,
                '.': (None, False),
                '#': (0, False),
                'o': (':', False),
                'R': ('R', False),
                'L': ('L', False),
                'T': ('T', False),
                'F': ('F', False),
                'J': ('J', False),
                'Z': ('Z', False),
                '7': ('7', False),
                '/': ('/', False),
                '-': ('-', False),
                '|': ('|', False),
                '+': ('+', False),
                'a': ('a', False),
                'h': ('h', False),
                '=': ('=', False),
                'l': ('l', False),
                'p': ('p', False),
                'r': ('r', False),
                'q': ('q', False),
                'd': ('d', False),
                '*': ('@', True),
                '^': ('^', False),
                '1': (None, 'mushrooms', False),
                '2': (None, 'medpack', False),
                '3': (None, 'killerwand', False),
                '4': (None, 'cclarva', False),
                '5': (None, 'stickyglue', False),
                '6': (None, 'minibomb', False),
                '9': (None, 'coolpack', False),
                '8': (None, 'gbomb', False),
                'v': ('v', True),
                's': ('s', True),
                'b': ('b', True),
                'Y': ('Y', False),
                '!': ('!', False),
                'w': ('w', False),
                '@': (None, True)}

        symsb = { '1': ('1', True),
                  '2': ('2', True),
                  '3': ('3', True),
                  '4': ('4', True),
                  '5': ('5', True) }


        #v1 = Vault(chance=3, level=(1,6), count=3,

        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(3,3), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(6,6), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(9,9), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(3,3), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(6,6), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(9,9), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(3,3), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(6,6), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(9,9), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(3,3), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(6,6), count=1, branch='a'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(9,9), count=1, branch='a'))

        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(3,3), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(6,6), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(9,9), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(3,3), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(6,6), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(9,9), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(3,3), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(6,6), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(9,9), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(3,3), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(6,6), count=1, branch='b'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(9,9), count=1, branch='b'))

        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(3,3), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(6,6), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(9,9), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(3,3), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(6,6), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(9,9), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(3,3), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(6,6), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(9,9), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(3,3), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(6,6), count=1, branch='c'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(9,9), count=1, branch='c'))

        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(3,3), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(6,6), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(9,9), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(3,3), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(6,6), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(9,9), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(3,3), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(6,6), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["5"], chance=3, level=(9,9), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(3,3), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(6,6), count=1, branch='d'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(9,9), count=1, branch='d'))

        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(3,3), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(6,6), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["2"], chance=3, level=(9,9), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(3,3), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(6,6), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["4"], chance=3, level=(9,9), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(3,3), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(6,6), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["1"], chance=3, level=(9,9), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(3,3), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(6,6), count=1, branch='e'))
        self.add(Vault(syms=symsb, pic=["3"], chance=3, level=(9,9), count=1, branch='e'))

        self.add(Vault(syms=syms,
                       pic=["o.o.o.o.o.o.o.o.o.o.o.o.o",
                            ".........................",
                            "o.R-T---------------T--.o",
                            "..|.|.......@.........o..",
                            "o.|hF--.o.a.o.o.o.o.|...o",
                            "..|.|.................o..",
                            "o.L-J---------------J--.o",
                            ".........................",
                            "o.o.o.o.o.o.o.o.o.o.o.o.o"],
                       chance=3, level=(2,7), count=1, branch='b'))

        self.add(Vault(syms=syms,
                       pic=["       R7.R7.R7.R7       ",
                            "    R7.L/.L/.L/.L/.R7    ",
                            "  ..L/.............L/..  ",
                            " R7.....o........o....R7 ",
                            ".L/....o..R---7...o...L/.",
                            "......o...|h.a.....o ....",
                            ".R7....o..L---/...o...R7.",
                            " L/.....o........o....L/ ",
                            "  ..R7.............R7..  ",
                            "    L/.R7.R7.R7.R7.L/    ",
                            "       L/.L/.L/.L/       "],
                       chance=3, level=(3,8), count=1, branch='b'))

        self.add(Vault(syms=syms,
                       pic=[" !       .     ...   .   ",
                            "!....   ... . ..YY.....  ",
                            "...!!. .Y ........  .!!..",
                            "  !!...YY...YY..      ...",
                            " ...Y..Y.....YY!!   ..Y..",
                            "...YYY.!!.  !h!!!!!!!Y.. ",
                            "   .!YY...   !!!YYY...   ",
                            "!!!!!!Y..!! .@YYYY...... ",
                            "  !!!Y..... .....   !  !.",
                            " !!!....YY...  ..! !.... ",
                            "    !  ..     !.. !  !! !"],
                       chance=3, level=(2,7), count=1, branch='a'))

        self.add(Vault(syms=syms,
                       pic=[" Y   !!. .   !! ..   .   ",
                            "  !  .!.... . ..!Y..... !",
                            "  Y!!. .Y .....!.!Y .!!..",
                            "  !!...YY...!!.! YYYY ...",
                            " ...Y..Y@....  !!YYY..Y..",
                            "...YYYh!!. !.....     .. ",
                            "   .!YY...   !!!YYY..!! Y",
                            "YY!. ....!! ..YY.....!.Y ",
                            " YY!!..Y... ...YY !!!  !.",
                            " .YY  ..YY...  Y.YYY.!!. ",
                            ".  Y!! ..     !..!Y! .. Y"],
                       chance=3, level=(3,8), count=1, branch='a'))

        self.add(Vault(syms=syms,
                       pic=[" r====q.=========.r====q ",
                            "......l...........l......",
                            ".l....l...r.=.q...l....l.",
                            ".p===...==d.@.p==...===d.",
                            "......l...........l......",
                            "......l.....h.....l......",
                            ".r===...==q...r==...===q ",
                            " l....l...p.=.d...l....l.",
                            " .....l...........l..... ",
                            " p====d ========= p====d "],
                       chance=3, level=(2,7), count=1, branch='c'))

        self.add(Vault(syms=syms,
                       pic=[" r====q.=====q.=====q.=q ",
                            ".l....l......l......l....",
                            ".l..r=..=q.==..=q.==..=q.",
                            ".l..l....l...@..l......l.",
                            ".l..l..r=..=q.==..=q...l.",
                            ".l..l..l....lh.....l...l.",
                            ".l..l.....==..====..l..l ",
                            " l..p=====..........d..l.",
                            " l..........r====q.....l ",
                            " p==========d    p=====d "],
                       chance=3, level=(3,8), count=1, branch='c'))

        self.add(Vault(syms=syms,
                       pic=[" R----------T----------7 ",
                            "R/..........|..........L7",
                            "|..R--=--7.....R--=--7..|",
                            "|..|.....|..|..|.....|..|",
                            "|..|.....|.-+-.|.....|..|",
                            "l@.F--=--Z..|..F--=--Z..l",
                            "|..|.....|..|..|...h.|..|",
                            "|..L--T--/..|..L--T--/..|",
                            "L7....l...........l....R/",
                            " L---------------------/ "],
                       chance=3, level=(2,7), count=1, branch='d'))

        self.add(Vault(syms=syms,
                       pic=[" R-- -------T-------7-   ",
                            "R/.. L....../ R.....R..  ",
                            "|-. --=- 7     R--=--7.R|",
                            " ..|... .|..|..|.....|.||",
                            "|.| ..||. .-+-.|.....|.L|",
                            "l@.F--= -Z..|..F--=--Z..l",
                            "|7.|..|.. ..+..|  .h.|R7 ",
                            " ..L-  --/ .| .    --/L/ ",
                            "L ....l........  .l....R/",
                            " L-------------  ------/ "],
                       chance=3, level=(2,8), count=1, branch='d'))


        self.add(Vault(syms=syms,
                       pic=["        .........        ",
                            "    ......Y.Y.Y......    ",
                            "  .....Y.Y......Y.Y....  ",
                            " ..Y.Y....YYYYYY....Y... ",
                            "..YYY...YYwwwwwwYY....Y..",
                            ".YYYYY..YYwwh.wwYY.......",
                            "..YYY...YYwwwwwwYY....Y..",
                            " ..Y.Y....YYYYYY....Y... ",
                            "  .....Y.Y......Y.Y....  ",
                            "    ......Y.Y.Y......    ",
                            "        .........        "],
                       chance=3, level=(2,7), count=1, branch='e'))

        self.add(Vault(syms=syms,
                       pic=["wwwwwwwwwwwwwwwwwwwwwwwww",
                            "wR-----7wwwwwwwwwR-----7w",
                            "w|h....L---------/.....|w",
                            "w|.....................|w",
                            "wL-7.R-J---------J-7.R-/w",
                            "www|.|             |.|www",
                            "wR-/.L-T---/.L---T-/.L-7w",
                            "w|.....................|w",
                            "w|.....R---/.L---7.....|w",
                            "wL-----/...@.....L-----/w",
                            "wwwwwwwwwwwwwwwwwwwwwwwww"],
                       chance=3, level=(3,8), count=1, branch='e'))

        self.add(Vault(syms=syms,
                       pic=["   .......   ",
                            " ........... ",
                            ".............",
                            "......*......",
                            ".............",
                            " ........... ",
                            "   .......   "],
                       chance=3, level=(2,12), count=4))

        self.add(Vault(syms=syms,
                       pic=[".........@..........",
                            "====================",
                            "...................."],
                       chance=3, level=(2,5), count=2, branch='c'))

        self.add(Vault(syms=syms,
                       pic=[".l.",
                            ".l.",
                            "@l.",
                            ".l.",
                            ".l.",
                            ".l."],
                       chance=3, level=(2,5), count=2, branch='c'))

        self.add(Vault(syms=syms,
                       pic=["  .^^^^^  ",
                            " ^^.^^^^^ ",
                            "^^^^.^^^^^",
                            "^^^r=.q^^^",
                            "^^^l..l^^^",
                            "^^^l..l^^^",
                            "^^^p==d^^^",
                            "^^^^^^^^^^",
                            " ^^^^^^^^ ",
                            "  ^^^^^^  "],
                       chance=3, level=(2,10), count=1, branch='c'))

        self.add(Vault(syms=syms,
                       pic=["  ^^^^^^  ",
                            " ^^^^^^^^ ",
                            "^^^^^^^^^^",
                            "^^^r==q^^^",
                            "^^^l..l^^^",
                            "^^^l..l^^^",
                            "^^^p.=d^^^",
                            "^^^^^.^^^^",
                            " ^^^^^.^^ ",
                            "  ^^^^^.  "],
                       chance=3, level=(2,10), count=1, branch='c'))

        self.add(Vault(syms=syms,
                       pic=["  ^^^^^^  ",
                            " ^^^^^^^^.",
                            "^^^^^^^^.^",
                            "^^^r==q.^^",
                            "^^^l...^^^",
                            "^^^l..l^^^",
                            "^^^p==d^^^",
                            "^^^^^^^^^^",
                            " ^^^^^^^^ ",
                            "  ^^^^^^  "],
                       chance=3, level=(2,10), count=1, branch='c'))

        self.add(Vault(syms=syms,
                       pic=["  ^^^^^^  ",
                            " ^^^^^^^^ ",
                            "^^^^^^^^^^",
                            "^^^r==q^^^",
                            "^^^l..l^^^",
                            "^^^...l^^^",
                            "^^.p==d^^^",
                            "^.^^^^^^^^",
                            ".^^^^^^^^ ",
                            "  ^^^^^^  "],
                       chance=3, level=(2,10), count=1, branch='c'))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|111|",
                            "|111|",
                            "L---/"],
                       chance=3, level=(4,14), count=3))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|222|",
                            "|222|",
                            "L---/"],
                       chance=3, level=(6,14), count=3))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|444|",
                            "|444|",
                            "L---/"],
                       chance=3, level=(10,14), count=3))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|333|",
                            "|333|",
                            "L---/"],
                       chance=3, level=(8,14), count=3, branch='e'))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|555|",
                            "|555|",
                            "L---/"],
                       chance=3, level=(4,14), count=3, branch='d'))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|666|",
                            "|666|",
                            "L---/"],
                       chance=3, level=(4,14), count=3, branch='a'))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|999|",
                            "|999|",
                            "L---/"],
                       chance=3, level=(4,14), count=3, branch='c'))

        self.add(Vault(syms=syms,
                       pic=["R---7",
                            "|888|",
                            "|888|",
                            "L---/"],
                       chance=3, level=(4,14), count=3, branch='b'))






    def add(self, v):
        v.postprocess()

        if v.branch:
            if v.branch not in self.vaults:
                self.vaults[v.branch] = {}

        for k,val in self.vaults.iteritems():
            if v.branch and v.branch != k:
                continue

            for x in xrange(v.level[0], v.level[1]+1):
                if x not in val:
                    val[x] = []
                val[x].append(v)

    def purge(self, vault):
        l = []

        for branch,v in self.vaults.iteritems():
            for level,v2 in v.iteritems():
                for x in xrange(len(v2)):
                    if id(vault) == id(v2[x]):
                        l.append((branch, level, x))

        for branch,level,x in l:
            del self.vaults[branch][level][x]

            if len(self.vaults[branch][level]) == 0:
                del self.vaults[branch][level]

            if len(self.vaults[branch]) == 0:
                del self.vaults[branch]


    def get(self, branch, level):
        if len(self.vaults) == 0:
            return None

        if branch not in self.vaults or len(self.vaults[branch]) == 0:
            return None

        while level > 0 and level not in self.vaults[branch]:
            level -= 1

        if level == 0:
            return None

        for x in xrange(len(self.vaults[branch][level])):
            v = self.vaults[branch][level][x]

            if random.randint(1, v.chance) != 1:
                continue

            if v.count == 1:
                self.purge(v)

            else:
                v.count -= 1

            return v

        return None


class Achieve:
    def __init__(self, tag=None, desc=None, weight=0):
        self.tag = tag
        self.desc = desc
        self.weight = weight


class Achievements:
    def __init__(self):
        self.achs = []
        self.killed_monsters = []
        self.prayed = 0
        self.shrines = set()
        self.used = 0
        self.wishes = 0
        self.rangeattacks = 0
        self.branches = set()
        self.onlyonce = set()
        self.extinguished = 0

    def finish(self, world):
        self.add('plev%d' % world.plev, 'Reached player level %d' % world.plev)
        self.add('dlev%d' % world.dlev, 'Reached dungeon level %d' % world.dlev)

        if len(self.killed_monsters) == 0:
            self.add('loser', 'Scored *no* kills')
        else:
            killbucket = ((len(self.killed_monsters) / 5) * 5)
            if killbucket > 0:
                self.add('%dkills' % killbucket, 'Killed at least %d monsters' % killbucket, weight=10*killbucket)

        reason = world.stats.health.reason
        self.add('dead_%s' % reason, 'Killed by %s' % reason)

        if len(self.shrines) >= 3:
            self.add('3gods', 'Worshipped 3 gods', weight=60)
        elif len(self.shrines) >= 2:
            self.add('2gods', 'Worshipped 2 gods.', weight=50)
        elif len(self.shrines) >= 1:
            self.add('religion', 'Worshipped a god')

        praybucket = ((self.prayed / 3) * 3)
        if praybucket > 0:
            self.add('%dprayers' % praybucket, 'Prayed at least %d times' % praybucket, weight=10*praybucket)

        usebucket = ((self.used / 20) * 20)
        if usebucket > 0:
            self.add('%duses' % usebucket, 'Used an item at least %d times' % usebucket, weight=10)

        if self.wishes == 0:
            self.add('nowish', 'Never wished for an item', weight=20)
        else:
            self.add('%dwish' % self.wishes, 'Wished for an item %d times' % self.wishes, weight=20)

        if self.rangeattacks == 0:
            self.add('nogun', 'Never used a firearm', weight=20)
        else:
            firebucket = ((self.rangeattacks / 10) * 10)
            if firebucket > 0:
                self.add('%dfires' % firebucket, 'Used a firearm at least %d times' % firebucket, weight=20)

        if len(self.branches) <= 1:
            self.add('onebranch', 'Visited only one dungeon branch', weight=15)
        else:
            self.add('%dbranch' % len(self.branches), 'Visited %d dungeon branches' % len(self.branches), weight=25)

        if self.extinguished > 0:
            self.add('%dxting' % self.extinguished, 'Extinguished %d monster species' % self.extinguished)


    def descend(self, world):
        if world.dlev >= world.plev+5:
            self.add('tourist', 'Dived to a very deep dungeon', weight=50, once=True)

        elif world.dlev >= world.plev+2:
            self.add('small_tourist', 'Dived to a deep dungeon', weight=15, once=True)

        self.branches.add(world.branch)


    def winner(self):
        self.add('winner', ' =*= Won the game =*= ', weight=100)

    def mondeath(self, world, mon):
        if mon.level >= world.plev+5:
            self.add('stealth', 'Killed a monster massively out of depth', weight=50)
        elif mon.level >= world.plev+2:
            self.add('small_stealth', 'Killed a monster out of depth', weight=10)
        self.killed_monsters.append((mon.level, mon.name, world.dlev, world.plev))

        if mon.count is not None and mon.count <= 1:
            self.extinguished += 1

    def pray(self, shrine):
        self.shrines.add(shrine)
        self.prayed += 1

    def use(self, item):
        self.used += 1

        if item.rangeattack or item.rangeexplode:
            self.rangeattacks += 1

    def wish(self):
        self.wishes += 1

    def __iter__(self):
        return iter(self.achs)

    def add(self, tag, desc, weight=0, once=False):
        if once:
            if tag in self.onlyonce:
                return
            else:
                self.onlyonce.add(tag)

        self.achs.append(Achieve(tag=tag, desc=desc, weight=weight))


class World:

    def __init__(self):
        self.grid = None

        self.walkmap = None
        self.watermap = None
        self.featmap = {}
        self.exit = None
        self.itemap = {}
        self.monmap = {}
        self.visitedmap = {}

        self.px = None
        self.py = None
        self.w = None
        self.h = None
        self.tcodmap = None
        self.done = False
        self.dead = False
        self.ckeys = None
        self.vkeys = None

        self.stats = Stats()
        self.msg = Messages()
        self.coef = Coeffs()
        self.inv = Inventory()
        self.itemstock = ItemStock()
        self.monsterstock = MonsterStock()
        self.featstock = FeatureStock()
        self.vaultstock = VaultStock()
        self.achievements = Achievements()

        self.dlev = 1
        self.plev = 1
        self.branch = None
        self.t = 0
        self.oldt = -1
        self.sleeping = 0
        self.forcedsleep = False
        self.forced2sleep = False
        self.resting = False
        self.cooling = 0
        self.digging = None
        self.blind = False
        self.mapping = 0
        self.glued = 0

        self.s_grace = 0
        self.b_grace = 0
        self.v_grace = 0

        self.floorpath = None

        self.monsters_in_view = []

        self._seed = None
        self._inputs = []

        self.save_disabled = False

        self.theme = { 'a': (libtcod.lighter_lime,),
                       'b': (libtcod.lighter_crimson,),
                       'c': (libtcod.lighter_sky,),
                       'd': (libtcod.dark_grey,),
                       'e': (libtcod.silver,) }





    def makegrid(self, w_, h_):
        self.w = w_
        self.h = h_
        self.grid = [[10 for x in xrange(self.w)] for y in xrange(self.h)]

    def randgen(self, a, b, c, d, mid):
        x = ((c - a) / 2) + a
        y = ((d - b) / 2) + b
        if (a == x or c == x) and (b == y or d == y): return

        s = max((c-a), (d-b))
        step = 0 #max(n, 1)
        s = 1 #max(step / 3, 1)

        if not mid:
            mid = self.grid[b][a] + self.grid[b][c] + self.grid[d][a] + self.grid[d][c]
            mid = int(mid / 4.0) - step + random.randint(-s, s)

        self.grid[y][x] = mid

        top = ((self.grid[b][a] + self.grid[b][c] + mid) / 3) - step + random.randint(-s, s)
        self.grid[b][x] = top

        bot = ((self.grid[d][a] + self.grid[d][c] + mid) / 3) - step + random.randint(-s, s)
        self.grid[d][x] = bot

        lef = ((self.grid[b][a] + self.grid[d][a] + mid) / 3) - step + random.randint(-s, s)
        self.grid[y][a] = lef

        rig = ((self.grid[b][c] + self.grid[d][c] + mid) / 3) - step + random.randint(-s, s)
        self.grid[y][c] = rig

        self.randgen(a, b, x, y, None)
        self.randgen(x, b, c, y, None)
        self.randgen(a, y, x, d, None)
        self.randgen(x, y, c, d, None)

    def normalize(self, ):
        avg = 0.0
        min = 2000
        max = -2000
        for row in self.grid:
            for v in row:
                avg += v

        avg = avg / (self.w * self.h)

        for x in xrange(self.w):
            for y in xrange(self.h):
                self.grid[y][x] -= avg
                v = self.grid[y][x]
                if v > max: max = v
                elif v < min: min = v

        scale = (max - min) / 20

        for x in xrange(self.w):
            for y in xrange(self.h):
                self.grid[y][x] = int(self.grid[y][x] / scale)
                if self.grid[y][x] > 10: self.grid[y][x] = 10
                elif self.grid[y][x] < -10: self.grid[y][x] = -10


    def terra(self):
        self.randgen(0, 0, self.w - 1, self.h - 1, -10)
        self.normalize()
        return self.grid


    def flow(self, x, y, out, n, q):
        if n < 1e-5: return

        v0 = self.grid[y][x]
        l = []
        if (x,y) in out: return
        out.add((x, y))

        for ix in xrange(-1, 2):
            for iy in xrange(-1, 2):
                zx = x + ix
                zy = y + iy
                if zx < 0 or zy < 0 or zx >= self.w or zy >= self.h:
                    continue
                v = self.grid[zy][zx]

                if (zx,zy) not in out and v <= v0:
                    l.append((v, zx, zy))

        if len(l) == 0: return

        l.sort()
        l = l[:2]
        qq = n / (len(l) + 1)

        for v,ix,iy in l:
            self.flow(ix, iy, out, qq, q)


    def makeflow(self, gout, watr, n, q):

        x = random.randint(0, self.w-1)
        y = random.randint(0, self.h-1)
        out = set()
        self.flow(x, y, out, n, q)

        for ix,iy in out:

            if (ix,iy) not in watr:
                watr[(ix,iy)] = 1
            else:
                watr[(ix,iy)] += 1

            self.grid[iy][ix] -= q
            if self.grid[iy][ix] < -10:
                self.grid[iy][ix] = -10

        gout.update(out)


    def makerivers(self):
        gout = set()
        watr = {}
        for x in xrange(50):
            self.makeflow(gout, watr, 100.0, 1)

        self.walkmap = set()
        for x,y in gout:
            if self.grid[y][x] <= 0:
                self.walkmap.add((x,y))

        watr = [(v,k) for (k,v) in watr.iteritems()]
        watr.sort()
        watr.reverse()

        pctwater = random.gauss(5, 1)
        if pctwater <= 1: pctwater = 1
        watr = watr[:int(len(watr)/pctwater)]

        self.watermap = set()
        for n,v in watr:
            self.watermap.add(v)

        self.visitedmap = {}
        self.featmap = {}


    def make_map(self):
        self.tcodmap = libtcod.map_new(self.w, self.h)
        libtcod.map_clear(self.tcodmap)

        for x in xrange(self.w):
            for y in xrange(self.h):
                if (x,y) in self.walkmap:
                    v = True
                    w = True
                else:
                    v = False
                    w = False

                if (x,y) in self.featmap:
                    f = self.featstock.f[self.featmap[(x, y)]]
                    w = f.walkable
                    v = f.visible

                libtcod.map_set_properties(self.tcodmap, x, y, v, w)

    def set_feature(self, x, y, f_):
        if (x, y) in self.featmap and self.featstock.f[self.featmap[(x, y)]].stairs:
            return

        if not f_:
            if (x, y) in self.featmap:
                del self.featmap[(x, y)]

            if f_ is None:
                self.walkmap.add((x, y))
                libtcod.map_set_properties(self.tcodmap, x, y, True, True)
                self.grid[y][x] = -10
            else:
                self.walkmap.discard((x, y))
                libtcod.map_set_properties(self.tcodmap, x, y, False, False)
                self.grid[y][x] = 0
            return

        f = self.featstock.f[f_]
        w = f.walkable
        v = f.visible
        libtcod.map_set_properties(self.tcodmap, x, y, v, w)
        self.featmap[(x, y)] = f_

        if w:
            self.walkmap.add((x, y))
        else:
            if (x, y) in self.walkmap:
                self.walkmap.discard((x, y))
        self.grid[y][x] = f.height

        if f.water:
            self.watermap.add((x, y))
        elif f.water is not None:
            if (x, y) in self.watermap:
                self.watermap.discard((x, y))



    def paste_vault(self, v, m):
        x = None
        y = None

        for x in xrange(10):
            d = m[random.randint(0, len(m)-1)]

            x0 = d[0] - v.anchor[0]
            y0 = d[1] - v.anchor[1]

            if x0 < 0 or y0 < 0 or x0 + v.w >= self.w or y0 + v.h >= self.h:
                continue

            x = x0
            y = y0
            break

        if x is None or y is None:
            return

        for yi in xrange(v.h):
            for xi in xrange(v.w):
                z = v.pic[yi]
                if xi >= len(z):
                    continue
                z = z[xi]
                z = v.syms[z]
                if z is None:
                    continue

                xx = x + xi
                yy = y + yi
                self.set_feature(xx, yy, z[0])

                if len(z) >= 3:
                    itm = self.itemstock.get(z[1])
                    if itm:
                        if (xx, yy) not in self.itemap:
                            self.itemap[(xx, yy)] = [itm]
                        else:
                            self.itemap[(xx, yy)].append(itm)


    def make_feats(self):
        m = list(self.walkmap - self.watermap)

        if len(m) == 0: return

        d = m[random.randint(0, len(m)-1)]

        self.featmap = {}
        self.featmap[d] = '>'
        self.exit = d

        a = random.randint(-1, 1)
        d = m[random.randint(0, len(m)-1)]
        if a == -1:
            self.featmap[d] = 's'
        elif a == 0:
            self.featmap[d] = 'b'
        elif a == 1:
            self.featmap[d] = 'v'

        # HACK!
        # This is done here, and not in make_items(),
        # so that vaults could generate items.
        self.itemap = {}

        vault = self.vaultstock.get(self.branch, self.dlev)

        if vault:
            self.paste_vault(vault, m)


    def try_feature(self, x, y, att):
        if (x,y) not in self.featmap:
                return None
        return getattr(self.featstock.f[self.featmap[(x, y)]], att, None)


    def make_paths(self):
        if self.floorpath:
            libtcod.path_delete(self.floorpath)

        def floor_callback(xfrom, yfrom, xto, yto, world):
            if (xto, yto) in world.monmap:
                return 0.0
            elif (xto, yto) in world.walkmap:
                return 1.0
            return 0.0

        self.floorpath = libtcod.path_new_using_function(self.w, self.h, floor_callback, self, 1.0)

    def make_monsters(self):

        self.monsterstock.clear_gencount()
        self.monmap = {}
        n = int(max(random.gauss(*self.coef.nummonsters), 1))
        ll = list(self.walkmap)

        for i in xrange(n):
            lev = self.dlev + random.gauss(0, self.coef.monlevel)
            lev = max(int(round(lev)), 1)

            while 1:
                x, y = ll[random.randint(0, len(ll)-1)]
                if (x, y) not in self.monmap: break

            m = self.monsterstock.generate(self.branch, lev, self.itemstock)
            if m:
                m.x = x
                m.y = y
                self.monmap[(x, y)] = m

    def make_items(self):

        n = int(max(random.gauss(self.coef.numitems[0] + self.dlev, self.coef.numitems[1]), 1))
        ll = list(self.walkmap)

        for i in xrange(n):
            lev = self.dlev + random.gauss(0, self.coef.itemlevel)
            lev = max(int(round(lev)), 1)
            x, y = ll[random.randint(0, len(ll)-1)]
            item = self.itemstock.generate(lev)
            if item:
                if (x, y) not in self.itemap:
                    self.itemap[(x, y)] = [item]
                else:
                    self.itemap[(x, y)].append(item)

        for pl,dl,itm in self.bones:
            if dl == self.dlev and len(itm) > 0:
                itm2 = [copy.copy(i) for i in itm]

                x, y = ll[random.randint(0, len(ll)-1)]

                if (x, y) not in self.itemap:
                    self.itemap[(x,y)] = itm2
                else:
                    self.itemap[(x,y)].extend(itm2)


    def regen(self, w_, h_):
        if self.branch is None:
            self.branch = random.choice(['a', 'b', 'c', 'd', 'e'])

        self.makegrid(w_, h_)
        self.terra()
        self.makerivers()
        self.make_map()
        self.make_feats()
        self.make_paths()
        self.make_monsters()
        self.make_items()

    def place(self):
        while 1:
            x = random.randint(0, self.w-1)
            y = random.randint(0, self.h-1)
            if (x,y) in self.walkmap and (x,y) not in self.monmap:
                self.px = x
                self.py = y
                return

        self.stats = Stats()

    def generate_inv(self):
        self.inv.take(self.itemstock.find('lamp'))
        l = [self.itemstock.get('pickaxe')]
        for x in range(3):
            l.append(self.itemstock.generate(1))
        if (self.px, self.py) not in self.itemap:
            self.itemap[(self.px, self.py)] = l
        else:
            self.itemap[(self.px, self.py)].extend(l)

        #self.inv.take(self.itemstock.get('necklamp'))
        #self.inv.take(self.itemstock.get('helmet'))
        #self.inv.take(self.itemstock.get('boots'))

        #self.itemap[(self.px, self.py)] = [
        #            self.itemstock.get('dynamite'),
        #            self.itemstock.get('mauser'),
        #            self.itemstock.get('pickaxe'),
        #            self.itemstock.get('tazer')]


    def move(self, _dx, _dy, do_spring=True):

        if self.glued > 0:
            self.glued -= 1
            if self.glued == 0:
                self.msg.m('You dislodge yourself from the glue.')
                del self.featmap[(self.px, self.py)]
            else:
                self.msg.m('You are stuck in the glue!')
                self.tick()
                return

        dx = _dx + self.px
        dy = _dy + self.py
        if (dx,dy) in self.walkmap and dx >= 0 and dx < self.w and dy < self.h:

            if (dx, dy) in self.monmap:
                self.fight(self.monmap[(dx, dy)], True)
                self.tick()
                return
            else:
                self.px = dx
                self.py = dy

                if (dx, dy) not in self.visitedmap:
                    self.visitedmap[(dx, dy)] = 0

                if (self.px, self.py) in self.itemap:
                    if len(self.itemap[(self.px, self.py)]) > 1:
                        self.msg.m("You see several items here.")
                    else:
                        self.msg.m("You see " + str(self.itemap[(self.px, self.py)][0]) + '.')

                if self.try_feature(self.px, self.py, 'sticky'):
                    self.msg.m('You just stepped in some glue!', True)
                    self.glued = max(int(random.gauss(*self.coef.glueduration)), 1)


        else:
            return

        if do_spring and self.inv.feet and self.inv.feet.springy:
            self.move(_dx, _dy, do_spring=False)
            return

        self.tick()

    def tick(self):
        self.stats.tired.dec(self.coef.movetired)
        self.stats.sleep.dec(self.coef.movesleep)
        self.stats.thirst.dec(self.coef.movethirst)
        self.stats.hunger.dec(self.coef.movehunger)

        if self.try_feature(self.px, self.py, 'warm'):
            self.stats.warmth.inc(self.coef.watercold)
        elif (self.px, self.py) in self.watermap or self.cooling:
            self.stats.warmth.dec(self.coef.watercold)
        else:
            self.stats.warmth.inc(self.inv.get_heatbonus())

        if self.b_grace > 0: self.b_grace -= 1
        if self.v_grace > 0: self.v_grace -= 1
        if self.s_grace > 0: self.s_grace -= 1

        self.tick_checkstats()
        self.t += 1

    def tick_checkstats(self):

        for i in self.inv:
            if i and i.liveexplode > 0:
                i.liveexplode -= 1
                if i.liveexplode == 0:
                    if i.summon:
                        self.summon(self.px, self.py, i.summon[0], i.summon[1])
                    elif i.radexplode:
                        self.rayblast(self.px, self.py, i.radius)
                    else:
                        self.explode(self.px, self.py, i.radius)
                    self.inv.purge(i)

            elif i and i.selfdestruct > 0 and \
                 i != self.inv.backpack1 and i != self.inv.backpack2:
                i.selfdestruct -= 1
                #print '-', i.selfdestruct, i.name
                if i.selfdestruct == 0:
                    self.msg.m('Your ' + i.name + ' falls apart!', True)
                    self.inv.purge(i)

        if self.cooling > 0:
            self.cooling -= 1
            if self.cooling == 0:
                self.msg.m("Your layer of cold mud dries up.")

        if self.dead: return

        if self.stats.warmth.x <= -3.0:
            self.msg.m("Being so cold makes you sick!", True)
            self.stats.health.dec(self.coef.colddamage, "cold")
            if self.resting: self.resting = False
            if self.digging: self.digging = None

        if self.stats.thirst.x <= -3.0:
            self.msg.m('You desperately need something to drink!', True)
            self.stats.health.dec(self.coef.thirstdamage, "thirst")
            if self.resting: self.resting = False
            if self.digging: self.digging = None

        if self.stats.hunger.x <= -3.0:
            self.msg.m('You desperately need something to eat!', True)
            self.stats.health.dec(self.coef.hungerdamage, "hunger")
            if self.resting: self.resting = False
            if self.digging: self.digging = None

        if self.stats.health.x <= -3.0:
            self.dead = True
            return

        if self.stats.tired.x <= -3.0:
            self.msg.m('You pass out from exhaustion!', True)
            self.start_sleep(force=True, quick=True)
            return

        if self.stats.sleep.x <= -3.0:
            self.msg.m('You pass out from lack of sleep!', True)
            self.start_sleep(force=True)
            return



    def rest(self):
        self.stats.tired.inc(self.coef.resttired)
        self.stats.sleep.dec(self.coef.restsleep)
        self.stats.thirst.dec(self.coef.restthirst)
        self.stats.hunger.dec(self.coef.resthunger)

        if self.try_feature(self.px, self.py, 'warm'):
            self.stats.warmth.inc(self.coef.watercold)
        elif (self.px, self.py) in self.watermap or self.cooling:
            self.stats.warmth.dec(self.coef.watercold)
        else:
            self.stats.warmth.inc(self.inv.get_heatbonus())
        self.tick_checkstats()
        self.t += 1

    def sleep(self):
        self.stats.tired.inc(self.coef.sleeptired)
        self.stats.sleep.inc(self.coef.sleepsleep)
        self.stats.thirst.dec(self.coef.sleepthirst)
        self.stats.hunger.dec(self.coef.sleephunger)

        if self.try_feature(self.px, self.py, 'warm'):
            self.stats.warmth.inc(self.coef.watercold)
        elif (self.px, self.py) in self.watermap or self.cooling:
            self.stats.warmth.dec(self.coef.watercold)
        else:
            self.stats.warmth.inc(self.inv.get_heatbonus())
        self.tick_checkstats()

        if self.sleeping > 0:
            self.sleeping -= 1

            if self.sleeping == 0:
                self.forcedsleep = False
                self.forced2sleep = False
        self.t += 1


    def start_sleep(self, force = False, quick = False,
                    realforced = False, realforced2 = False):
        if not force and self.stats.sleep.x > -2.0:
            self.msg.m('You don\'t feel like sleeping yet.')
            return

        if quick:
            self.sleeping = int(random.gauss(*self.coef.quicksleeptime))
        else:
            if not realforced2:
                self.msg.m('You fall asleep.')
            self.sleeping = int(random.gauss(*self.coef.sleeptime))
        if self.sleep <= 10:
            self.sleep = 10
        self.digging = None
        self.resting = False

        if realforced:
            self.forcedsleep = True
        elif realforced2:
            self.forced2sleep = True

    def start_rest(self):
        self.msg.m('You start resting.')
        self.resting = True

    def drink(self):
        if (self.px,self.py) not in self.watermap:
            self.msg.m('There is no water here you could drink.')
            return

        if self.v_grace:
            self.msg.m('Your religion prohibits drinking from the floor.')
            return

        self.stats.thirst.inc(6)

        x = abs(random.gauss(0, 0.7))
        tmp = x - self.coef.waterpois
        if tmp > 0:
            self.stats.health.dec(tmp, "unclean water")
            if tmp > 0.2:
                self.msg.m('This water has a bad smell.')
        else:
            self.msg.m('You drink from the puddle.')

        self.tick()

    def pray(self):
        if (self.px,self.py) not in self.featmap:
            self.msg.m('You need to be standing at a shrine to pray.')
            return

        a = self.featstock.f[self.featmap[(self.px, self.py)]]

        if a.s_shrine:
            if self.b_grace or self.v_grace:
                self.msg.m("You don't believe in Shiva.")
                return
            if self.s_grace > self.coef.graceduration - 300:
                self.msg.m('Nothing happens.')
                return

            ss = "sthwp"
            decc = self.coef.shivadecstat
            ss = ss[random.randint(0, len(ss)-1)]

            if ss == 's': self.stats.sleep.dec(decc)
            elif ss == 't': self.stats.tired.dec(decc)
            elif ss == 'h': self.stats.hunger.dec(decc)
            elif ss == 'w': self.stats.warmth.dec(decc)
            elif ss == 'p': self.stats.health.dec(decc, 'the grace of Shiva')

            self.msg.m('You pray to Shiva.')
            self.wish('Shiva grants you a wish.')
            self.s_grace = self.coef.graceduration
            self.tick()
            self.achievements.pray('s')

        elif a.b_shrine:
            if self.s_grace or self.v_grace:
                self.msg.m("You don't believe in Brahma.")
                return
            self.msg.m('You feel enlightened.')
            self.b_grace = self.coef.graceduration
            self.tick()
            self.achievements.pray('b')

        elif a.v_shrine:
            if self.s_grace or self.b_grace:
                self.msg.m("You don't believe in Vishnu.")
                return

            if self.v_grace > self.coef.graceduration - 300:
                self.msg.m('Nothing happens.')
                return

            self.msg.m('You meditate on the virtues of Vishnu.')
            self.start_sleep(force=True, realforced2=True)

            self.stats.health.inc(6.0)
            self.stats.sleep.inc(6.0)
            self.stats.tired.inc(6.0)
            self.stats.hunger.inc(6.0)
            self.stats.thirst.inc(6.0)
            self.stats.warmth.inc(6.0)
            self.v_grace = self.coef.graceduration
            self.tick()
            self.achievements.pray('v')

        else:
            self.msg.m('You need to be standing at a shrine to pray.')
            return


    def convert_to_floor(self, x, y, rubble=0):
        if rubble == 0:
            self.set_feature(x, y, None)
        else:
            self.set_feature(x, y, '*')


    def showinv(self):
        return self.inv.draw(self.w, self.h, self.dlev, self.plev)


    def showinv_apply(self):
        slot = self.inv.draw(self.w, self.h, self.dlev, self.plev)
        i = self.inv.drop(slot)
        if not i:
            if slot in 'abcdefghi':
                self.msg.m('You have no item in that slot.')
            return

        if not i.applies:
            self.msg.m('This item cannot be applied.')
            self.inv.take(i, slot)
            return

        i2 = self.apply(i)
        if i2:
            self.inv.take(i2)
        else:
            if i.count > 0:
                i.count -= 1
            if i.count > 0:
                self.inv.take(i)

        self.tick()


    def slot_to_name(self, slot):
        if slot == 'a': return 'head'
        elif slot == 'b': return 'neck'
        elif slot == 'c': return 'trunk'
        elif slot == 'd': return 'left hand'
        elif slot == 'e': return 'right hand'
        elif slot == 'f': return 'legs'
        elif slot == 'g': return 'feet'
        else: return 'backpack'


    def showinv_interact(self):
        slot = self.inv.draw(self.w, self.h, self.dlev, self.plev)
        i = self.inv.drop(slot)
        if not i:
            if slot in 'abcdefghi':
                self.msg.m('You have no item in that slot.')
            return

        si = str(i)
        si = si[0].upper() + si[1:]
        s = [si + ':', '']
        choices = 'd'


        if i.applies:
            s.append('a) use it')
            choices += 'a'

        if not self.inv.backpack1 or not self.inv.backpack2:
            s.append('b) move it to a backpack slot')
            choices += 'b'

        if i.desc:
            s.append('c) examine this item')
            choices += 'c'

        s.append('d) drop this item')
        if i.throwable:
            s.append('f) throw this item')
            choices += 'f'

        if i.slot in 'abcdefg' and slot in 'hi':
            s.append('x) swap this item with item in equipment')
            choices += 'x'

        s.append('')
        s.append('any other key to equip it')
        cc = draw_window(s, self.w, self.h)

        if cc not in choices:
            self.inv.take(i)
            self.tick()
            return

        if cc == 'a' and i.applies:
            i2 = self.apply(i)
            if i2:
                self.inv.take(i2)
            else:
                if i.count > 0:
                    i.count -= 1
                if i.count > 0:
                    self.inv.take(i)

            self.tick()

        elif cc == 'b':
            if not self.inv.backpack1:
                self.inv.backpack1 = i
                self.tick()
            elif not self.inv.backpack2:
                self.inv.backpack2 = i
                self.tick()

        elif cc == 'c' and i.desc:
            ss = i.desc[:]
            ss.append('')
            ss.append('Slot: ' + self.slot_to_name(i.slot))
            draw_window(ss, self.w, self.h)
            self.inv.take(i)
            self.tick()

        elif cc == 'd':
            if (self.px, self.py) in self.itemap:
                self.itemap[(self.px, self.py)].append(i)
            else:
                self.itemap[(self.px, self.py)] = [i]
            self.tick()

        elif cc == 'f':
            while 1:
                nx, ny = self.target(i.throwrange)
                if nx is not None:
                    break

            if nx >= 0:
                self.msg.m('You throw ' + str(i) + '.')

                if (nx, ny) in self.itemap:
                    self.itemap[(nx, ny)].append(i)
                else:
                    self.itemap[(nx, ny)] = [i]
            else:
                self.inv.take(i)
            self.tick()

        elif cc == 'x':
            item2 = self.inv.drop(i.slot)
            self.inv.take(i)
            if item2:
                self.inv.take(item2)

        else:
            self.inv.take(i)
            self.tick()

    def apply(self, item):
        if not item.applies:
            return item

        if item.converts:
            inew = self.itemstock.get(item.converts)

            if self.inv.check(inew.slot) is not None:
                self.msg.m('Your ' + self.slot_to_name(inew.slot) + ' slot needs to be free to use this.')
                return item

            self.inv.take(inew)
            s = str(inew)
            s = s[0].upper() + s[1:]
            self.msg.m(s + ' is now in your ' + self.slot_to_name(inew.slot) + ' slot!', True)

            self.achievements.use(item)
            return None

        elif item.digging:
            k = draw_window(['Dig in which direction?'], self.w, self.h, True)

            self.digging = None
            if k == 'h': self.digging = (self.px - 1, self.py)
            elif k == 'j': self.digging = (self.px, self.py + 1)
            elif k == 'k': self.digging = (self.px, self.py - 1)
            elif k == 'l': self.digging = (self.px + 1, self.py)
            else:
                return item

            if self.digging[0] < 0 or self.digging[0] >= self.w:
                self.digging = None
            if self.digging[1] < 0 or self.digging[1] >= self.h:
                self.digging = None

            if not self.digging:
                return item

            if self.digging in self.walkmap:
                self.msg.m('There is nothing to dig there.')
                self.digging = None
            else:
                self.msg.m("You start hacking at the wall.")
                self.achievements.use(item)

        elif item.healing:

            if self.v_grace:
                self.msg.m('Your religion prohibits taking medicine.')
                return item

            if item.bonus < 0:
                self.msg.m('This pill makes your eyes pop out of their sockets!', True)
                self.stats.tired.dec(max(random.gauss(*item.healing), 0))
                self.stats.sleep.dec(max(random.gauss(*item.healing), 0))
            else:
                self.msg.m('Eating this pill makes you dizzy.')
                self.stats.health.inc(max(random.gauss(*item.healing), 0))
                self.stats.hunger.dec(max(random.gauss(*item.healing), 0))
                self.stats.sleep.dec(max(random.gauss(*item.healing), 0))

            self.achievements.use(item)
            return None

        elif item.food:

            if self.v_grace:
                self.msg.m('Your religion prohibits eating unclean food.')
                return item

            if item.bonus < 0:
                self.msg.m('Yuck, eating this makes you vomit!', True)
                self.stats.hunger.dec(max(random.gauss(*item.food), 0))
            else:
                self.msg.m('Mm, yummy.')
                self.stats.hunger.inc(max(random.gauss(*item.food), 0))

            self.achievements.use(item)
            return None

        elif item.booze:

            if self.v_grace:
                self.msg.m('Your religion prohibits alcohol.')
                return item

            if item.bonus < 0:
                self.msg.m("This stuff is contaminated! You fear you're going blind!", True)
                self.blind = True
            else:
                self.msg.m('Aaahh.')
                self.stats.sleep.dec(max(random.gauss(*self.coef.boozestrength), 0))
                self.stats.warmth.inc(max(random.gauss(*self.coef.boozestrength), 0))

            self.achievements.use(item)
            return None

        elif item.homing:
            d = math.sqrt(math.pow(abs(self.px - self.exit[0]), 2) +
                          math.pow(abs(self.py - self.exit[1]), 2))
            if d > 30:
                self.msg.m('Cold as ice!')
            elif d > 20:
                self.msg.m('Very cold!')
            elif d > 15:
                self.msg.m('Cold!')
            elif d > 10:
                self.msg.m('Getting warmer...')
            elif d > 5:
                self.msg.m('Warm and getting warmer!')
            elif d > 3:
                self.msg.m("This thing is buring!")
            else:
                self.msg.m('You are at the spot. Look around.')

            self.achievements.use(item)

        elif item.sounding:
            k = draw_window(['Check in which direction?'], self.w, self.h, True)

            s = None
            if k == 'h': s = (-1, 0)
            elif k == 'j': s = (0, 1)
            elif k == 'k': s = (0, -1)
            elif k == 'l': s = (1, 0)
            else:
                return item

            n = 0
            x = self.px
            y = self.py
            while x >= 0 and y >= 0 and x < self.w and y < self.h:
                x += s[0]
                y += s[1]
                if (x,y) in self.walkmap:
                    break
                n += 1

            draw_window(['Rock depth: ' + str(n)], self.w, self.h)
            self.achievements.use(item)

        elif item.tracker:
            self.visitedmap[(self.px, self.py)] = 1
            self.msg.m("You mark this spot in your tracker's memory.")
            self.achievements.use(item)

        elif item.detector:
            s = []
            if item.detect_monsters:
                s.append('You detect the following monsters:')
                for v in self.monmap.itervalues():
                    s.append('  '+str(v))
                s.append('')

            if item.detect_items:
                s.append('You detect the following items:')
                for v in self.itemap.itervalues():
                    for vv in v:
                        s.append('  '+str(vv))
                s.append('')

            if len(s) > 19:
                s = s[:19]
                s.append('(There is more information, but it does not fit on the screen)')

            draw_window(s, self.w, self.h)
            self.achievements.use(item)

        elif item.cooling:
            self.cooling = max(int(random.gauss(*self.coef.coolingduration)), 1)
            self.msg.m("You cover yourself in cold mud.")

            self.achievements.use(item)
            return None

        elif item.wishing:
            self.wish()

            self.achievements.use(item)
            return None

        elif item.mapper:
            self.mapping = item.mapper

            self.achievements.use(item)
            return None

        elif item.jinni:
            l = []
            for x in xrange(-1, 2):
                for y in xrange(-1, 2):
                    if x != 0 or y != 0:
                        q = (self.px + x, self.py + y)
                        if q in self.walkmap and q not in self.monmap:
                            l.append(q)

            if len(l) == 0:
                self.msg.m('Nothing happened.')
                return None

            jinni = Monster('Jinni', level=self.plev+1,
                            attack=max(self.inv.get_attack(), 0.5),
                            defence=self.inv.get_defence(),
                            range=self.inv.get_lightradius(),
                            skin=('&', libtcod.yellow),
                            desc=['A supernatural fire fiend.'])

            self.msg.m('A malevolent spirit appears!')
            q = l[random.randint(0, len(l)-1)]
            jinni.x = q[0]
            jinni.y = q[1]
            jinni.items = [self.itemstock.get('wishing')]
            self.monmap[q] = jinni

            self.achievements.use(item)
            return None

        elif item.digray:
            if item.digray[0] == 1:
                for x in xrange(0, self.w):
                    self.convert_to_floor(x, self.py)
            if item.digray[1] == 1:
                for y in xrange(0, self.h):
                    self.convert_to_floor(self.px, y)
            self.msg.m('The wand explodes in a brilliant white flash!')

            self.achievements.use(item)
            return None

        elif item.jumprange:
            l = []
            for x in xrange(self.px - item.jumprange, self.px + item.jumprange + 1):
                for y in [self.py - item.jumprange, self.px + item.jumprange]:
                    if (x,y) in self.walkmap:
                        l.append((x,y))

            for y in xrange(self.py - item.jumprange - 1, self.py + item.jumprange):
                for x in [self.px - item.jumprange, self.px + item.jumprange]:
                    if (x,y) in self.walkmap:
                        l.append((x,y))

            l = l[random.randint(0, len(l)-1)]
            self.px = l[0]
            self.py = l[1]

            self.achievements.use(item)
            return None

        elif item.makestrap:
            if (self.px,self.py) in self.featmap:
                self.msg.m('Nothing happens.')
                return item

            if (self.px,self.py) in self.watermap:
                self.msg.m("That won't work while you're standing on water.")
                return item

            self.featmap[(self.px, self.py)] = '^'
            self.msg.m('You spread the glue liberally on the floor.')

            self.achievements.use(item)

            if item.count is None:
                return item
            return None

        elif item.rangeattack or item.rangeexplode:
            if item.ammo <= 0:
                self.msg.m("It's out of ammo!")
                return item

            while 1:
                nx, ny = self.target(item.range[1],
                                     minrange=item.range[0],
                                     monstop=item.straightline)
                if nx is not None:
                    break
            if nx < 0:
                return item

            item.ammo -= 1

            if item.rangeexplode:
                self.explode(nx, ny, item.radius)
            else:
                if (nx, ny) in self.monmap:
                    self.fight(self.monmap[(nx, ny)], True, item=item)

            if item.ammo <= 0:
                return None

            self.achievements.use(item)

        return item


    def descend(self):

        ss = self.try_feature(self.px, self.py, 'stairs')
        if not ss:
            self.msg.m('You can\'t descend, there is no hole here.')
            return

        self.msg.m('You climb down the hole.')
        self.dlev += ss

        b = self.try_feature(self.px, self.py, 'branch')
        if b:
            self.branch = b

        self.regen(self.w, self.h)
        self.place()
        self.tick()
        self.achievements.descend(self)


    def drop(self):
        slot = self.showinv()
        i = self.inv.drop(slot)
        if not i:
            if slot in 'abcdefghi':
                self.msg.m('There is no item in that slot.')
            return

        self.msg.m('You drop ' + str(i) +'.')
        if (self.px, self.py) in self.itemap:
            self.itemap[(self.px, self.py)].append(i)
        else:
            self.itemap[(self.px, self.py)] = [i]
        self.tick()



    def pick_one_item(self, items):
        c = 0
        if len(items) > 1:
            s = []
            for i in xrange(len(items)):
                if i == 0:
                    s.append('%c' % libtcod.COLCTRL_1)
                    s[-1] += '%c) %s' % (chr(97 + i), str(items[i]))
                elif i >= 5:
                    s.append('(There are other items here; clear away the pile to see more)')
                    break
                else:
                    s.append('%c) %s' % (chr(97 + i), str(items[i])))

            c = draw_window(s, self.w, self.h)
            c = ord(c) - 97

            if c < 0 or c >= len(items):
                return None, None

        i = items[c]
        return i, c

    def take(self):
        if (self.px, self.py) not in self.itemap:
            self.msg.m('You see no item here to take.')
            return

        items = self.itemap[(self.px, self.py)]

        i, c = self.pick_one_item(items)
        if not i:
            return

        did_scavenge = False

        for ii in self.inv:
            if ii and ii.name == i.name:
                if ii.stackrange and ii.count < ii.stackrange:
                    n = min(ii.stackrange - ii.count, i.count)
                    ii.count += n
                    i.count -= n

                    self.msg.m('You now have ' + str(ii))
                    did_scavenge = True

                    if i.count == 0:
                        del items[c]
                        if len(items) == 0:
                            del self.itemap[(self.px, self.py)]
                            break

                elif i.ammo > 0 and ii.ammo and ii.ammo < ii.ammochance[1]:
                    n = min(ii.ammochance[1] - ii.ammo, i.ammo)
                    ii.ammo += n
                    i.ammo -= n
                    self.msg.m("You find some ammo for your " + ii.name)
                    did_scavenge = True

        if did_scavenge:
            self.tick()
            return

        ok = self.inv.take(i)
        if ok:
            self.msg.m('You take ' + str(i) + '.')
            del items[c]
            if len(items) == 0:
                del self.itemap[(self.px, self.py)]
        else:
            self.msg.m('You have no free inventory slot for ' + str(i) + '!')

        self.tick()


    def ground_apply(self):
        if (self.px, self.py) not in self.itemap:
            self.msg.m('There is no item here to apply.')
            return

        items = self.itemap[(self.px, self.py)]
        items = [i for i in items if i.applies]

        if len(items) == 0:
            self.msg.m('There is no item here to apply.')

        i,c = self.pick_one_item(items)
        if not i:
            return

        i2 = self.apply(i)
        if not i2:
            if i.count > 1:
                i.count -= 1
                self.tick()
                return
            for ix in xrange(len(self.itemap[(self.px, self.py)])):
                if id(self.itemap[(self.px, self.py)][ix]) == id(i):
                    del self.itemap[(self.px, self.py)][ix]

                    if len(self.itemap[(self.px, self.py)]) == 0:
                        del self.itemap[(self.px, self.py)]
                    break

        self.tick()


    def handle_mondeath(self, mon, do_drop=True, do_gain=True):
        if do_gain and mon.level > self.plev:
            self.msg.m('You just gained level ' + str(mon.level) + '!', True)
            self.plev = mon.level

        if do_drop:
            if len(mon.items) > 0:
                if (mon.x, mon.y) in self.itemap:
                    self.itemap[(mon.x, mon.y)].extend(mon.items)
                else:
                    self.itemap[(mon.x, mon.y)] = mon.items

        if do_gain:
            self.achievements.mondeath(self, mon)

        if self.monsterstock.death(mon):
            while 1:
                c = draw_window(['Congratulations! You have won the game.', '', 'Press space to exit.'], self.w, self.h)
                if c == ' ': break

            self.stats.health.reason = 'winning'
            self.done = True
            self.dead = True
            self.achievements.winner()


    def rayblast(self, x0, y0, rad):

        libtcod.map_compute_fov(self.tcodmap, x0, y0, rad,
                                False, libtcod.FOV_RESTRICTIVE)

        def func1(x, y):
            return libtcod.map_is_in_fov(self.tcodmap, x, y)

        def func2(x, y):
            if x == self.px and y == self.py and \
                not (self.inv.trunk and self.inv.trunk.radimmune):
                self.stats.health.dec(self.coef.raddamage, "radiation")

            if (x, y) in self.monmap:
                mon = self.monmap[(x, y)]
                if not mon.radimmune:
                    mon.hp -= self.coef.raddamage
                    if mon.hp <= -3.0:
                        self.handle_mondeath(mon)
                        del self.monmap[(x, y)]

        draw_blast2(x0, y0, self.w, self.h, rad, func1, func2)


    def explode(self, x0, y0, rad):
        chains = set()
        def func(x, y):
            if random.randint(0, 5) == 0:
                self.set_feature(x, y, '*')
            else:
                self.set_feature(x, y, None)

            if x == self.px and y == self.py and \
                not (self.inv.trunk and self.inv.trunk.explodeimmune):
                self.stats.health.dec(6.0, "explosion")
                self.dead = True

            if (x, y) in self.itemap:
                for i in self.itemap[(x, y)]:
                    if i.explodes:
                        chains.add((x, y, i.radius))
                        break
                del self.itemap[(x, y)]

            if (x, y) in self.monmap:
                mon = self.monmap[(x, y)]
                if not mon.explodeimmune:
                    self.handle_mondeath(mon, do_drop=False)

                    for i in mon.items:
                        if i.explodes:
                            chains.add((x, y, i.radius))
                            break

                    del self.monmap[(x, y)]

        draw_blast(x0, y0, self.w, self.h, rad, func)

        for x, y, r in chains:
            self.explode(x, y, r)


    def fight(self, mon, player_move, item=None, attackstat=None):

        sm = str(mon)
        smu = sm[0].upper() + sm[1:]

        d = math.sqrt(math.pow(abs(mon.x - self.px), 2) +
                      math.pow(abs(mon.y - self.py), 2))
        d = int(round(d))

        if player_move and item:
            plev = min(max(self.plev - d + 1, 1), self.plev)
            attack = item.rangeattack
            #print '+', d, plev, attack

        elif player_move and attackstat:
            plev = attackstat[0]
            attack = attackstat[1]

        else:
            if self.b_grace and player_move:
                self.msg.m('Your religion prohibits you from fighting.')
                return

            plev = self.plev
            attack = max(self.inv.get_attack(), self.coef.unarmedattack)


        def roll(attack, leva, defence, levd):
            a = 0
            for x in xrange(leva):
                a += random.uniform(0, attack)
            d = 0
            for x in xrange(levd):
                d += random.uniform(0, defence)

            ret = max(a - d, 0)
            #print ' ->', ret, ':', attack, leva, '/', defence, levd
            return ret

        if player_move:

            defence = mon.defence
            if mon.glued:
                defence /= self.coef.gluedefencepenalty

            dmg = roll(attack, plev, defence, mon.level)

            mon.hp -= dmg

            if mon.hp <= -3.0:
                if mon.visible or mon.visible_old:
                    self.msg.m('You killed ' + sm + '!')
                self.handle_mondeath(mon)
                del self.monmap[(mon.x, mon.y)]
            else:

                fires = None
                ca = None

                if item:
                    ca = item.confattack
                    fires = item.fires
                elif not attackstat:
                    ca = self.inv.get_confattack()

                if ca and dmg > 0 and not mon.confimmune:
                    if mon.visible or mon.visible_old:
                        self.msg.m(smu + ' looks totally dazed!')
                    mon.confused += int(max(random.gauss(*ca), 1))

                elif fires and dmg > 0 and not mon.fireimmune:
                    if mon.visible or mon.visile_old:
                        self.msg.m('You set ' + sm + ' on fire!')

                    mon.onfire = fires
                    mon.fireduration = fires

                    if mon.fireattack:
                        mon.fireattack = (max(plev, mon.fireattack[0]), max(dmg, mon.fireattack[1]))
                    else:
                        mon.fireattack = (plev, dmg)

                elif not (mon.visible or mon.visible_old):
                    pass

                elif attackstat:
                    pass

                elif dmg > 4:
                    self.msg.m('You mortally wound ' + sm + '!')
                elif dmg > 2:
                    self.msg.m('You seriously wound ' + sm + '.')
                elif dmg > 0.5:
                    self.msg.m('You wound ' + sm + '.')
                elif dmg > 0:
                    self.msg.m('You barely wound ' + sm + '.')
                else:
                    self.msg.m('You miss ' + sm + '.')

            if dmg > 0 and (mon.visible or mon.visible_old):
                mon.known_px = self.px
                mon.known_py = self.py


        else:

            attack = None
            defence = None
            psy = False

            if d > 1 and mon.psyattack > 0:
                if self.inv.get_psyimmune():
                    return
                attack = mon.psyattack
                defence = self.coef.unarmeddefence
                psy = True
            else:
                attack = mon.attack
                defence = max(self.inv.get_defence(), self.coef.unarmeddefence)
                if self.glued:
                    defence /= self.coef.gluedefencepenalty


            if attack == 0:
                return

            dmg = roll(attack, mon.level, defence, plev)

            if psy:
                if dmg > 0:
                    self.msg.m(smu + ' is attacking your brain!')
            else:
                if dmg > 0:
                    self.msg.m(smu + ' hits!')
                else:
                    self.msg.m(smu + ' misses.')

            if mon.sleepattack:
                self.msg.m('You fall asleep!')
                self.start_sleep(force=True, quick=True, realforced=True)
                return

            if mon.hungerattack:
                self.stats.hunger.dec(dmg)
            else:
                self.stats.health.dec(dmg, sm)

            if self.resting:
                self.msg.m('You stop resting.')
                self.resting = False

            if self.digging:
                self.msg.m('You stop digging.')
                self.digging = None

            if self.sleeping and not self.forced2sleep:
                self.sleeping = 0

            if self.stats.health.x <= -3.0:
                self.dead = True


    def look(self):
        tx = self.px
        ty = self.py

        while 1:
            seen = self.draw(tx, ty)

            s = []

            if tx == self.px and ty == self.py:
                s.append('This is you.')
                s.append('')

            if not seen:
                s.append('You see nothing.')

            else:
                if (tx, ty) in self.monmap:
                    m = self.monmap[(tx, ty)]
                    s.append('You see ' + str(m) + ':')
                    s.append('')
                    s.extend(m.desc)
                    s.append('')

                if (tx, ty) in self.itemap:
                    i = self.itemap[(tx, ty)]
                    s.append('You see the following items:')
                    for ix in xrange(len(i)):
                        if ix >= 5:
                            s.append('(And some other items)')
                            break
                        s.append(str(i[ix]))
                    s.append('')

                if (tx, ty) in self.featmap:
                    f = self.featstock.f[self.featmap[(tx, ty)]]
                    s.append('You see ' + f.name + '.')

                elif (tx, ty) in self.walkmap:
                    if (tx, ty) in self.watermap:
                        s.append('You see a water-covered floor.')
                    else:
                        s.append('You see a cave floor.')

                else:
                        s.append('You see a cave wall.')

            k = draw_window(s, self.w, self.h, True)

            if   k == 'h': tx -= 1
            elif k == 'j': ty += 1
            elif k == 'k': ty -= 1
            elif k == 'l': tx += 1
            elif k == 'y':
                tx -= 1
                ty -= 1
            elif k == 'u':
                tx += 1
                ty -= 1
            elif k == 'b':
                tx -= 1
                ty += 1
            elif k == 'n':
                tx += 1
                ty += 1
            else:
                break

            if tx < 0: tx = 0
            elif tx >= self.w: tx = self.w - 1

            if ty < 0: ty = 0
            elif ty >= self.h: ty = self.h - 1


    def target(self, range, minrange=None, monstop=False):

        self.draw()

        monx = None
        mony = None
        for i in xrange(len(self.monsters_in_view)):
            mon = self.monsters_in_view[i]
            d = math.sqrt(math.pow(abs(self.px - mon.x), 2) +
                          math.pow(abs(self.py - mon.y), 2))
            if d > range:
                continue

            if minrange and d < minrange:
                continue

            monx = mon.x
            mony = mon.y
            del self.monsters_in_view[i]
            self.monsters_in_view.append(mon)
            break

        if monx is not None:
            self.draw(monx, mony)

        k = draw_window(['Pick a target. '
                         "HJKL YUBN for directions, "
                         "<space> and '.' to target a monster."],
                         self.w, self.h, True)

        if k == 'h':
            dx = max(self.px - range, 0)
            dy = self.py
        elif k == 'j':
            dx = self.px
            dy = min(self.py + range, self.h - 1)
        elif k == 'k':
            dx = self.px
            dy = max(self.py - range, 0)
        elif k == 'l':
            dx = min(self.px + range, self.w - 1)
            dy = self.py
        elif k == 'y':
            dx = max(self.px - int(range * 0.71), 0)
            dy = max(self.py - int(range * 0.71), 0)
        elif k == 'u':
            dx = min(self.px + int(range * 0.71), self.w - 1)
            dy = max(self.py - int(range * 0.71), 0)
        elif k == 'b':
            dx = max(self.px - int(range * 0.71), 0)
            dy = min(self.py + int(range * 0.71), self.h - 1)
        elif k == 'n':
            dx = min(self.px + int(range * 0.71), self.w - 1)
            dy = min(self.py + int(range * 0.71), self.h - 1)
        elif k == '.':
            if monx is not None:
                dx = monx
                dy = mony
            else:
                return (None, None)
        elif k == ' ':
            return (None, None)
        else:
            return -1, -1

        libtcod.line_init(self.px, self.py, dx, dy)
        xx = None
        yy = None
        while 1:
            tmpx, tmpy = libtcod.line_step()

            if tmpx is None:
                return (xx, yy)

            if (tmpx, tmpy) in self.walkmap or self.try_feature(tmpx, tmpy, 'shootable'):

                if minrange:
                    d = math.sqrt(math.pow(abs(tmpx - self.px), 2) +
                                  math.pow(abs(tmpy - self.py), 2))
                    if d < minrange:
                        continue

                xx = tmpx
                yy = tmpy

                if monstop and (tmpx, tmpy) in self.monmap:
                    return (xx, yy)

            else:
                return (xx, yy)


    def show_messages(self):
        self.msg.show_all(self.w, self.h)


    def wish(self, msg=None):
        s = ''
        while 1:
            if msg:
                k = draw_window([msg, '', 'Wish for what? : ' + s],
                                self.w, self.h)
            else:
                k = draw_window(['Wish for what? : ' + s], self.w, self.h)

            k = k.lower()
            if k in "abcdefghijklmnopqrstuvwxyz' -":
                s = s + k
            elif ord(k) == 8 or ord(k) == 127:
                if len(s) > 0:
                    s = s[:-1]
            elif k in '\r\n':
                break

        i = self.itemstock.find(s)

        self.achievements.wish()

        if not i:
            self.msg.m('Nothing happened!')
        else:
            self.msg.m('Suddenly, ' + str(i) + ' appears at your feet!')
            if (self.px, self.py) in self.itemap:
                self.itemap[(self.px, self.py)].append(i)
            else:
                self.itemap[(self.px, self.py)] = [i]


    def move_down(self): self.move(0, 1)
    def move_up(self): self.move(0, -1)
    def move_left(self): self.move(-1, 0)
    def move_right(self): self.move(1, 0)
    def move_upleft(self): self.move(-1, -1)
    def move_upright(self): self.move(1, -1)
    def move_downleft(self): self.move(-1, 1)
    def move_downright(self): self.move(1, 1)

    def quit(self):
        k = draw_window(["Really quit? Press 'y' if you are truly sure."], self.w, self.h)
        if k == 'y':
            self.stats.health.reason = 'quitting'
            self.done = True
            self.dead = True


    def show_help(self):
        s = ['%c' % libtcod.COLCTRL_1,
             "Movement keys: roguelike 'hjkl' 'yubn' or the numpad/arrow keys.",
             "",
             " . : Stand in place for one turn.",
             " s : Start sleeping.",
             " r : Start resting.",
             " q : Drink from the floor.",
             " p : Pray at a shrine.",
             " > : Descend down to the next level.",
             "",
             " a : Apply (use) an item from your inventory.",
             " A : Apply (use) an item from the ground.",
             " i : Manipulate your inventory.",
             " d : Drop an item from your inventory.",
             " , : Pick up an item from the floor.",
             "",
             " / : Look around at the terrain, items and monsters.",
             " P : Show a log of previous messages.",
             " Q : Quit the game by committing suicide.",
             " S : Save the game and quit.",
             " ? : Show this help."
        ]
        draw_window(s, self.w, self.h)



    def make_keymap(self):
        self.ckeys = {
            'h': self.move_left,
            'j': self.move_down,
            'k': self.move_up,
            'l': self.move_right,
            'y': self.move_upleft,
            'u': self.move_upright,
            'b': self.move_downleft,
            'n': self.move_downright,
            '.': self.rest,
            's': self.start_sleep,
            'r': self.start_rest,
            'q': self.drink,
            'p': self.pray,
            'a': self.showinv_apply,
            'A': self.ground_apply,
            'i': self.showinv_interact,
            '>': self.descend,
            'd': self.drop,
            ',': self.take,
            '/': self.look,
            'P': self.show_messages,
            'Q': self.quit,
            '?': self.show_help,
            'S': self.save
            }
        self.vkeys = {
            libtcod.KEY_KP4: self.move_left,
            libtcod.KEY_KP6: self.move_right,
            libtcod.KEY_KP8: self.move_up,
            libtcod.KEY_KP2: self.move_down,
            libtcod.KEY_KP7: self.move_upleft,
            libtcod.KEY_KP9: self.move_upright,
            libtcod.KEY_KP1: self.move_downleft,
            libtcod.KEY_KP3: self.move_downright,

            libtcod.KEY_LEFT: self.move_left,
            libtcod.KEY_RIGHT: self.move_right,
            libtcod.KEY_UP: self.move_up,
            libtcod.KEY_DOWN: self.move_down,
            libtcod.KEY_HOME: self.move_upleft,
            libtcod.KEY_PAGEUP: self.move_upright,
            libtcod.KEY_END: self.move_downleft,
            libtcod.KEY_PAGEDOWN: self.move_downright
            }


    def walk_monster(self, mon, dist, x, y):

        if mon.slow and (self.t & 1) == 0:
            return None, None

        if mon.glued > 0:
            mon.glued -= 1
            if mon.glued == 0:
                del self.featmap[(mon.x, mon.y)]
            else:
                return None, None

        rang = mon.range

        if self.b_grace:
            rang = 12 - int(9 * (float(self.b_grace) / self.coef.graceduration))
            rang = min(rang, mon.range)

        if self.inv.trunk and self.inv.trunk.camorange:
            rang = min(rang, self.inv.trunk.camorange)

        if dist > rang or mon.confused or (mon.sleepattack and self.sleeping):
            mdx = x + random.randint(-1, 1)
            mdy = y + random.randint(-1, 1)
            if (mdx, mdy) not in self.walkmap:
                mdx = None
                mdy = None
            if mon.confused:
                mon.confused -= 1

        else:

            if mon.psyrange > 0 and dist <= mon.psyrange:
                self.fight(mon, False)

            if mon.known_px is None or mon.known_py is None:
                mon.known_px = self.px
                mon.known_py = self.py

            elif self.inv.trunk and self.inv.trunk.repelrange and \
                 dist <= self.inv.trunk.repelrange and dist > 1:
                 return None, None

            elif mon.heatseeking and \
                 ((self.px, self.py) in self.watermap or self.cooling):
                pass
            else:
                mon.known_px = self.px
                mon.known_py = self.py

            if mon.straightline:
                libtcod.line_init(x, y, mon.known_px, mon.known_py)
                mdx, mdy = libtcod.line_step()
            else:
                libtcod.path_compute(self.floorpath, x, y, mon.known_px, mon.known_py)
                mdx, mdy = libtcod.path_walk(self.floorpath, True)

        if mon.stoneeating:
            if mdx is not None:
                if (mdx, mdy) not in self.walkmap:
                    self.convert_to_floor(mdx, mdy, rubble=1)

        return mdx, mdy

    def process_monstep(self, mon):
        mdx = mon.x
        mdy = mon.y

        if self.try_feature(mdx, mdy, 'sticky') and not mon.flying:
            if mon.visible or mon.visible_old:
                mn = str(mon)
                mn = mn[0].upper() + mn[1:]
                self.msg.m(mn + ' gets stuck in some glue!')
            mon.glued = max(int(random.gauss(*self.coef.glueduration)), 1)


    def summon(self, x, y, monname, n):
        m = self.monsterstock.find(monname, n, self.itemstock)
        if len(m) == 0:
            return []

        l = []
        for xx in xrange(x-1,x+2):
            for yy in xrange(y-1,y+2):
                if (xx,yy) in self.walkmap and \
                   (xx,yy) not in self.monmap and \
                   (xx != self.px or yy != self.py):
                    l.append((xx,yy))

        ret = []
        for i in xrange(len(m)):
            if len(l) == 0:
                return ret
            j = random.randint(0, len(l)-1)
            xx,yy = l[j]
            del l[j]

            m[i].x = xx
            m[i].y = yy
            self.monmap[(xx, yy)] = m[i]
            ret.append(m[i])

        return ret

    def process_world(self):

        explodes = set()
        mons = []
        delitems = []
        rblasts = []

        for k,v in self.itemap.iteritems():
            for i in v:
                if i.liveexplode > 0:
                    i.liveexplode -= 1
                    if i.liveexplode == 0:
                        if i.summon:
                            self.summon(k[0], k[1], i.summon[0], i.summon[1])
                            delitems.append(k)
                        elif i.radexplode:
                            rblasts.append((k[0], k[1], i.radius))
                            delitems.append(k)
                        else:
                            explodes.add((k[0], k[1], i.radius))

        for x,y,r in rblasts:
            self.rayblast(x, y, r)

        for ix,iy in delitems:
            for i in xrange(len(self.itemap[(ix,iy)])):
                if self.itemap[(ix,iy)][i].liveexplode == 0:
                    del self.itemap[(ix,iy)][i]
                    if len(self.itemap[(ix,iy)]) == 0:
                        del self.itemap[(ix,iy)]

        summons = []
        fired = []

        for k,mon in self.monmap.iteritems():

            if mon.summon and mon.visible and (self.t % mon.summon[1]) == 0:
                summons.append((k, mon))
                continue

            mon.visible_old = mon.visible
            mon.visible = False

            if mon.onfire > 0:
                fired.append(mon)

            if not mon.did_move:
                x, y = k
                dist = math.sqrt(math.pow(abs(self.px - x), 2) + math.pow(abs(self.py - y), 2))

                mdx, mdy = self.walk_monster(mon, dist, x, y)

                if mdx is not None:
                    if mdx == self.px and mdy == self.py:
                        if mon.selfdestruct:
                            smu = str(mon)
                            smu = smu[0].upper() + smu[1:]
                            self.msg.m(smu + ' suddenly self-destructs!')
                            self.handle_mondeath(mon, do_gain=False)
                            mon.do_die = True
                        else:
                            self.fight(mon, False)
                    else:
                        mon.do_move = (mdx, mdy)

                    mon.did_move = True
                    mons.append(mon)

        for k,mon in summons:
            smu = str(mon)
            smu = smu[0].upper() + smu[1:]
            q = self.summon(k[0], k[1], mon.summon[0], 1)
            if len(q) > 0:
                self.msg.m(smu + ' summons ' + str(q[0]) + '!')
            else:
                mon.summon = None

        for mon in mons:
            if mon.do_move:
                mon.old_pos = (mon.x, mon.y)
                del self.monmap[(mon.x, mon.y)]
            elif mon.do_die:
                del self.monmap[(mon.x, mon.y)]

        for mon in mons:
            if mon.do_move:
                if mon.do_move in self.monmap:
                    mon.do_move = mon.old_pos

                mon.x = mon.do_move[0]
                mon.y = mon.do_move[1]
                self.monmap[mon.do_move] = mon
                mon.do_move = None

                self.process_monstep(mon)

            mon.did_move = False

        for mon in fired:
            self.fight(mon, True, attackstat=mon.fireattack)
            mon.onfire -= 1
            if mon.onfire <= 0:
                mon.fireattack = None
                mon.fireduration = 0

        for x, y, r in explodes:
            del self.itemap[(x, y)]
            self.explode(x, y, r)



    def draw(self, _hlx=None, _hly=None):
        withtime = False
        if self.oldt != self.t:
            withtime = True

        default_back = libtcod.black

        lightradius = min(max(self.inv.get_lightradius(), 2), 15)

        if self.blind:
            lightradius /= 2

        if self.b_grace:
            n = int(15 * (float(self.b_grace) / self.coef.graceduration))
            lightradius = max(lightradius, n)

        if self.mapping > 0:
            if withtime:
                self.mapping -= 1
            if self.mapping > 0:
                lightradius = 25


        if withtime:
            self.process_world()

        monsters_in_view = []
        did_highlight = False

        libtcod.map_compute_fov(self.tcodmap, self.px, self.py, lightradius,
                                True, libtcod.FOV_RESTRICTIVE)

        for x in xrange(self.w):
            for y in xrange(self.h):

                fore = self.theme[self.branch][0] #libtcod.lightest_green

                if self.inv.neck and self.inv.neck.tracker:
                    if (x, y) in self.visitedmap:
                        if self.visitedmap[(x, y)]:
                            back = libtcod.red
                        else:
                            back = libtcod.darkest_gray
                    else:
                        back = libtcod.black

                if self.mapping:
                    in_fov = True
                else:
                    in_fov = libtcod.map_is_in_fov(self.tcodmap, x, y)

                is_lit = False

                if self.inv.head and self.inv.head.telepathyrange:
                    if (x, y) in self.monmap:
                        d = math.sqrt(math.pow(abs(y - self.py),2) + math.pow(abs(x - self.px),2))
                        if d <= self.inv.head.telepathyrange:
                            in_fov = True
                            is_lit = True


                back = default_back

                if not in_fov:
                    c = ' '
                    fore = libtcod.black

                else:

                    if x == self.px and y == self.py:
                        fore = libtcod.white
                        c = '@'
                        if self.sleeping > 1 and (self.t & 1) == 1:
                            c = '*'
                        elif self.resting and (self.t & 1) == 1:
                            c = '.'
                        elif self.digging and (self.t & 1) == 1:
                            c = '('

                    elif (x, y) in self.monmap:
                        mon = self.monmap[(x, y)]
                        mon.visible = True
                        c, fore = mon.skin
                        monsters_in_view.append(mon)

                        if mon.onfire:
                            back = libtcod.color_lerp(libtcod.orange, default_back,
                                                      1.0 - (float(mon.onfire) / mon.fireduration))


                    elif (x, y) in self.itemap:
                        c, fore = self.itemap[(x, y)][0].skin

                    elif (x, y) in self.featmap:
                        f = self.featstock.f[self.featmap[(x, y)]]
                        c, fore = f.skin

                    elif (x, y) in self.walkmap:
                        if (x,y) in self.watermap:
                            c = '-'
                            fore = libtcod.dark_azure #libtcod.Color(80, 80, 255)
                        else:
                            c = 250
                    else:
                        if (x,y) in self.watermap:
                            fore = libtcod.desaturated_blue #libtcod.Color(100, 128, 255)
                        c = '#'

                    if not is_lit:
                        d = math.sqrt(math.pow(abs(y - self.py),2) + math.pow(abs(x - self.px),2))

                        fore = libtcod.color_lerp(fore, back, min(d/lightradius, 1.0))

                    if x == _hlx and y == _hly:
                        back = libtcod.white
                        did_highlight = True

                libtcod.console_put_char_ex(None, x, y, c, fore, back)

        if self.px > self.w / 2:
            self.stats.draw(0, 0)
        else:
            self.stats.draw(self.w - 14, 0)

        if self.py > self.h / 2:
            self.msg.draw(15, 0, self.w - 30)
        else:
            self.msg.draw(15, self.h - 3, self.w - 30)


        # hack
        if withtime:
            self.monsters_in_view = []
            for mon in monsters_in_view:
                if (mon.x, mon.y) in self.monmap:
                    self.monsters_in_view.append(mon)

        if withtime:
            self.oldt = self.t

        return did_highlight


    def save(self):
        # HACK! For supporting replays of games that have been saved and then loaded.
        print 'SAVING!'
        if self.save_disabled:
            random.seed(self._seed)
            return


        f = None
        atts = [
          'grid', 'walkmap', 'watermap', 'exit', 'itemap', 'monmap', 'visitedmap',
          'featmap', 'px', 'py', 'w', 'h',
          'done', 'dead', 'stats', 'msg', 'coef', 'inv', 'itemstock', 'monsterstock', 'branch',
          'dlev', 'plev', 't', 'oldt', 'sleeping', 'resting', 'cooling', 'digging', 'blind',
          'mapping', 'glued', 's_grace', 'b_grace', 'v_grace', 'forcedsleep',
          'forced2sleep',
          '_seed', '_inputs', 'featstock', 'vaultstock',
          'achievements', 'bones'
          ]
        state = {}

        for x in atts:
            state[x] = getattr(self, x)

        if 1: #try:
            f = open('savefile', 'w')
            cPickle.dump(state, f)
        #except:
        #    return
        self.msg.m('Saved!')
        self.done = True


    def load_bones(self):
        print 'LOADING BONES!'
        self.bones = []
        try:
            bf = open('bones', 'r')
            self.bones = cPickle.load(bf)
        except:
            pass


    def load(self):
        print 'LOADING!'
        f = None
        state = None

        try:
            f = open('savefile', 'r')
            state = cPickle.load(f)
        except:
            return False

        for k,v in state.iteritems():
            setattr(self, k, v)

        random.seed(self._seed)
        global _inputs
        _inputs = self._inputs

        self.make_map()
        self.make_paths()
        return True


    def form_highscore(self):

        # Clobber the savefile.
        try:
            open('savefile', 'w').truncate(0)
        except:
            pass

        # Form bones.
        bones = []
        try:
            bf = open('bones', 'r')
            bones = cPickle.load(bf)
        except:
            pass

        bones.append((self.plev, self.dlev, [i for i in self.inv if i is not None and i.liveexplode is None]))
        bones = bones[-3:]

        try:
            bf = open('bones', 'w')
            cPickle.dump(bones, bf)
        except:
            pass

        # Save to highscore.

        self.achievements.finish(self)


        conn = sqlite3.connect('highscore.db')
        c = conn.cursor()

        tbl_games = 'Games%s' % _version.replace('.', '')
        tbl_achievements = 'Achievements%s' % _version.replace('.', '')

        c.execute('create table if not exists ' + tbl_games + \
                  ' (id INTEGER PRIMARY KEY, seed INTEGER, score INTEGER, bones BLOB, inputs BLOB)')
        c.execute('create table if not exists ' + tbl_achievements + \
                  ' (achievement TEXT, game_id INTEGER)')

        score = (self.plev * 5) + (self.dlev * 5) + sum(x[0] for x in self.achievements.killed_monsters)


        c.execute('insert into ' + tbl_games + '(id, seed, score, bones, inputs) values (NULL, ?, ?, ?, ?)',
                  (self._seed, score,
                   sqlite3.Binary(cPickle.dumps(self.bones)),
                   sqlite3.Binary(cPickle.dumps(self._inputs))))

        gameid = c.lastrowid

        for a in self.achievements:
            c.execute('insert into ' + tbl_achievements + '(achievement, game_id) values (?, ?)',
                      (a.tag, gameid))

        conn.commit()


        # Show placements.

        c.execute(('select sum(score >= %d),count(*) from ' % score) + tbl_games)
        place, total = c.fetchone()

        atotals = []

        for a in self.achievements:
            c.execute(('select sum(score >= %d),count(*) from ' % score) + \
                      (' %s join %s on (game_id = id)' % (tbl_games, tbl_achievements)) + \
                      ' where achievement = ?', (a.tag,))
            p1,t1 = c.fetchone()
            atotals.append((p1, 100 - a.weight, t1, a.desc))

        c.close()
        conn.close()

        atotals.sort()

        if len(atotals) >= 5:
            atotals = atotals[:5]

        s = []

        s.append('%cYour score: %c%d%c.    (#%c%d%c of %d%s)' % \
                (libtcod.COLCTRL_5, libtcod.COLCTRL_1, score, libtcod.COLCTRL_5,
                 libtcod.COLCTRL_1, place, libtcod.COLCTRL_5, total, '!' if place == 1 else '.'))
        s.append('')
        s.append('Your achievements:')
        s.append('')

        for p1,w,t1,a in atotals:
            s.append('%c%s%c:%s     #%c%d%c of %d%s' % (libtcod.COLCTRL_1, a, libtcod.COLCTRL_5,
                     ' '*max(0, 50 - len(a)), libtcod.COLCTRL_1, p1,
                     libtcod.COLCTRL_5, t1, '!' if p1 == 1 else '.'))
            s.append('')

        s.append('-' * 50)
        s.extend((x[1] for x in self.msg.strings[2:8]))
        s.append('')
        s.append('Press space to try again.')

        while 1:
            if draw_window(s, self.w, self.h) == ' ':
                break



def start_game(world, w, h, oldseed=None, oldbones=None):

    if oldseed or not world.load():
        if oldseed:
            world._seed = oldseed
        else:
            world._seed = int(time.time())

        if oldbones is not None:
            world.bones = oldbones
        else:
            world.load_bones()

        random.seed(world._seed)
        global _inputs
        _inputs = world._inputs

        world.regen(w, h)
        world.place()
        world.generate_inv()
        world.msg.m("Kill all the monsters in the dungeon to win the game.")
        world.msg.m("Please press '?' to see help.")

def check_autoplay(world):

    if world.sleeping > 0:
        if world.stats.sleep.x >= 3.0 and not world.forcedsleep and not world.forced2sleep:
            world.msg.m('You wake up.')
            world.sleeping = 0
            return 1
        else:
            world.sleep()
            return -1

    if world.resting:
        if world.stats.tired.x >= 3.0:
            world.msg.m('You stop resting.')
            world.resting = False
            return 1
        else:
            world.rest()
            return -1

    if world.digging:
        if world.grid[world.digging[1]][world.digging[0]] <= -10:
            world.convert_to_floor(world.digging[0], world.digging[1])
            world.digging = None
            return 1
        else:
            world.grid[world.digging[1]][world.digging[0]] -= 0.1
            world.tick()
            return -1

    return 0


def main(replay=None):

    global qqq1
    qqq1 = open('qqq1', 'a')
    print >> qqq1, 'START'

    oldseed = None
    oldbones = None

    if replay is not None:
        oldseed = replay[0]
        oldinputs = replay[1]
        oldbones = replay[2]

        global _inputqueue
        _inputqueue = oldinputs

    w = 80
    h = 25


    #libtcod.sys_set_renderer(libtcod.RENDERER_SDL)

    font = 'terminal10x16_gs_ro.png'
    libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(w, h, 'Diggr', False, libtcod.RENDERER_SDL)
    libtcod.sys_set_fps(30)
    #cons = libtcod.console_new(w, h)
    #cons = None

    world = World()
    world.make_keymap()

    if replay is not None:
        world.save_disabled = True

    start_game(world, w, h, oldseed=oldseed, oldbones=oldbones)

    while 1:

        if libtcod.console_is_window_closed():
            if replay is None:
                # MEGATON-SIZED HACK!
                # To make replays work.
                _inputs.append((ord('S'), 0))

                world.save()
            break

        if world.done or world.dead: break

        world.draw()
        libtcod.console_flush()

        r = check_autoplay(world)
        if r == -1:
            libtcod.console_check_for_keypress()
            continue
        elif r == 1:
            world.draw()
            libtcod.console_flush()


        if world.dead: break

        #key = libtcod.console_wait_for_keypress(True)
        #world._inputs.append((key.c, key.vk))
        key = console_wait_for_keypress()

        if chr(key.c) in world.ckeys:
            world.ckeys[chr(key.c)]()

        elif key.vk in world.vkeys:
            world.vkeys[key.vk]()


    if world.dead and not world.done:
        world.msg.m('You die.', True)

    world.oldt = world.t
    world.msg.m('*** Press any key ***', True)
    world.draw()
    libtcod.console_flush()
    libtcod.console_wait_for_keypress(True)

    if replay is None and world.dead:
        world.form_highscore()

    print >> qqq1, 'DONE'
    qqq1.close()

    return world.done


#import cProfile
#cProfile.run('main()')

if __name__=='__main__':
    while 1:
        if main():
            break
