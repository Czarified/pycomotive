#!/usr/bin/env python
# coding: utf-8



import sys
import os
import datetime
import time
import copy
from collections import deque
import random
from tqdm import tqdm_notebook as tqdm



###################
###   Classes   ###
###################
class Locomotive():
    '''
    A locomotive has certain attributes and actions.
    
    Locomomtives have a name (str), class (str), weight (int),
    power (int), and max speed (int).
    
    There is currently no validation on these properties. When creating
    a consist, you should use consistent units.
    '''
    def __init__(self, name, number, lclass, road, length, weight, power, maxspeed):
        self.name = name
        self.number = number
        self.road = road
        self.lclass = lclass
        self.length = length
        self.weight = weight
        self.power = power
        self.maxspeed = maxspeed
        
        
    def __repr__(self):
        return '<Locomotive: {}, {}, {} #{}>'.format(self.lclass,
                                                     self.road,
                                                     self.name,
                                                     self.number
                                                    )
        
        
        
    def info(self):
        out = ''
        for k,v in self.__dict__.items():
            out += '\n{}: {}'.format(k.title(), v)
            
        return out
    

class RollingStock():
    '''
    A car holding goods, which can be pulled by a locomotive.
    
    Rolling Stock have a type (str), Railroad owner (str), number (int), length (int),
    dry mass (int), total capacity (int), current load mass (int), and a max speed (int).
    
    load_mass and maxspeed are optional, and defaulted to 0 (empty), and 1000 (no speed limit).
    
    There is currently no validation on these properties. When creating
    a consist, you should use consistent units.
    '''
    def __init__(self, car_type, road, number, color, length, dry_mass, capacity, load_mass=0, maxspeed=1000):
        self.car_type = car_type
        self.road = road
        self.number = number
        self.color = color
        self.length = length
        self.dry_mass = dry_mass
        self.weight = dry_mass + load_mass
        self.capacity = capacity
        self.maxspeed = maxspeed
        
    def __repr__(self):
        return '<{}: {}, {} #{}>'.format(self.car_type, self.road, self.color, self.number)
        
    
    @property
    def isfull(self):
        '''
        Property of a rolling stock car which represents how much cargo it currently holds.
        Returns percent of load relative to total capacity (0 to 1).
        '''
        return (self.weight - self.dry_mass)/self.capacity
    
    
    def info(self):
        '''
        Returns a string which can be easily printed to show all current properties of the rolling stock.
        '''
        out = ''
        for k,v in self.__dict__.items():
            out += '\n{}: {}'.format(k.title(), v)
            
        return out
    
    
    def load(self, mass):
        '''
        Load an amount of mass in the rolling stock.
        
        Returns 0 if all mass is loaded, remaining mass if excess.
        '''
        # If the mass to load is less than the remaining capacity
        if mass <= (1-self.isfull)*self.capacity:
            # Load all the mass
            self.weight += mass
            return 0
        else:
            # Store the available mass for return operation
            e = (1-self.isfull)*self.capacity
            # Fill up the cargo
            self.weight = self.dry_mass + self.capacity
            # Return the difference
            return mass - e
        
        
    def unload(self, p=1) -> float:
        '''
        Unloads a percentage of mass from the rolling stock.
        Default to fully unload.
        
        Returns the mass removed.
        '''
        if p > self.isfull:
            p = self.isfull
        
        mass = p*(self.weight-self.dry_mass)
        self.weight -= mass
        return mass
        
    
    
class Consist():
    '''
    A Consist is a set of train classes. This can or cannot include a locomotive.
    Order matters in a consist.
    '''    
    def __init__(self, number, *argv):
        # The stock of a consist contains all the cars and locomotives, and their order.
        
        # If only 1 additional argument is given,
        # assume it's a deque to be used as the new stock
        if len(argv) == 1:
            self.stock = deque(argv[0])
        else:
            self.stock = deque(argv)
            
        self.number = number        
            
    
    def __repr__(self):
        rep = '<< Consist #{}:'.format(self.number)
        for car in self.stock:
            rep += '\n{}'.format(car)
        
        rep += ' >>'
            
        return rep
    
    
    @property
    def length(self):
        '''
        Consist length property.
        '''
        length = 0
        for car in self.stock:
            length += car.length
            
        return length
            
    
    @property
    def weight(self):
        '''
        Consist weight property.
        '''
        weight = 0
        for car in self.stock:
            weight += car.weight
        
        return weight
            
    
    def attach(self, car):
        '''
        This method attaches a car at the end of the consist stock.
        '''
        self.stock.append(car)
        
    
    def separate(self, car):
        '''
        This method splits the consist in two. The car provided
        will be the lead car in the new consist (aka separate the consist
        _before_ the provided car).
        '''
        idx = self.stock.index(car)
        self.stock.rotate(-idx)
        
        new_stock = deque()
        for i in range(len(self.stock)-idx):
            new_stock.append(self.stock.popleft())
            
        return Consist(self.number+1, new_stock)
    



    



############################
###   Global Variables   ###
############################
# lib contains subclasses
import lib

COLORS = ['red', 'blue', 'yellow', 'green', 'brown', 'white', 'grey', 'black', 'orange']
ROADS = ['UP', 'NO', 'SOO', 'CSX', 'CC', 'TS', 'BNSF', 'ICG', 'ED&T']
TYPS = [lib.Boxcar, lib.Gondola, lib.Hopper, lib.Flatcar]
LOAD_TIME = 0.05


#####################
###   Functions   ###
#####################
def load_consist(cargo, con, typ=None):
    '''
    This function will take an input cargo stock, and consist, and load
    each car in the consist to full, until entire consist is full, or
    no cargo remains.
    
    Optionally, it can be set to only load on cars in the consist which have
    a matching car_type attribute.
    
    Returns remaining cargo mass, and loaded consist.
    '''
    if typ is None:
        for car in tqdm(con.stock):
            if cargo == 0:
                return cargo, con
            else:
                time.sleep(LOAD_TIME)
                cargo = car.load(cargo)
        
        return cargo, con
    else:
        for car in tqdm(con.stock):
            if isinstance(car, Locomotive):
                continue
            
            if cargo == 0:
                return cargo, con
            elif car.car_type == typ.title():
                time.sleep(LOAD_TIME)
                cargo = car.load(cargo)
        
        return cargo, con
    

def random_consist(loco,
                   num,
                   carrange: tuple = (1,20),
                   numrange: tuple = (100,99999),
                   colors = COLORS,
                   roads = ROADS,
                   car_types = TYPS
                  ):
    '''
    Generates a random consist with the specified variables.
    
    Returns the consist, and prints results.
    '''
    train = Consist(num)
    train.attach(loco)
    for i in range(carrange[0], carrange[1]):
        num = random.randint(numrange[0], numrange[1])
        color = random.choice(colors)
        road = random.choice(roads)
        car = random.choice(car_types)
        train.attach(car(road=road, number=num, color=color))

    print('')
    print(train)
    print('')
    print('Consist Length: {:.2f}[m]'.format(train.length))
    print('Consist Weight: {:.3f}[kg]'.format(train.weight))
    
    return train




loco = UP_BigBoy(4004)

train = random_consist(loco, random.randint(0,9999))

rock = 220 # kg





print('Loading rock in gondolas only...')
rock, train = load_consist(rock, train, typ='gondola')
print('Rock remaining after consist load: {:.3f}[kg]'.format(rock))
print('')

for car in train.stock:
    if isinstance(car, Locomotive):
        continue
    if car.isfull == 0:
        print('{} {} is empty.'.format(car.car_type, car.number))
    else:
        print('{} {} is {:.1%} full.'.format(car.car_type, car.number, car.isfull))
        
print('')
print('After loading, consist weighs: {:.3f}[kg]'.format(train.weight))


