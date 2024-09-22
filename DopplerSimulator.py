import numpy as _np
import matplotlib.pyplot as plt
import tkinter as tk
from scipy.io import wavfile
import pygame

class DopplerSimulator:
    def __init__(self, cal_cap_ratio,
                 universal_gases_constant, temperature, molar_mass):
        self._ccp = cal_cap_ratio # calorific capacities ratio
        self._ugc = universal_gases_constant # universal gases constant
        self._temperature = temperature
        self._mol_mass = molar_mass
        self._sound_velocity = self._sound_velocity_calculator()

    def _sound_velocity_calculator(self): # calculates the sound velocity in a predetermined medium
        sound_velocity = self._ccp * self._ugc * self.temperature
        sound_velocity /= self.mol_mass
        sound_velocity = _np.sqrt(sound_velocity)
        return sound_velocity
    
    @property
    def sound_velocity(self):
        return self._sound_velocity
    
    @property.setter
    def set_sound_velocity(self, ccp, ugc, temperature, molar_mass):
        new_sound_velocity = ccp * ugc * temperature
        new_sound_velocity /= molar_mass
        self._sound_velocity = _np.sqrt(new_sound_velocity)
    
    def _beholder_and_source_velocity(self, final_time,
                                linear_coef, angular_coef=0):
        """This method supports only MU and MUV"""
        time_elapsed = _np.linspace(0, final_time)
        size_time_array = time_elapsed.size
        ones = _np.ones(size_time_array)
        velocity = angular_coef * time_elapsed + linear_coef * ones

        return velocity
    
    def frequency_calculator(self, f0, 
                             beholder_velocity, source_velocity, 
                             distance_increases, same_direction):
        """This method works only if the velocities are positive"""

        if distance_increases:
            source_velocity = -source_velocity

        if not same_direction:
            beholder_velocity = -beholder_velocity

        numerator = self.sound_velocity() + source_velocity
        denominator = self.sound_velocity() + beholder_velocity 

        fixed_frequency = f0*numerator
        fixed_frequency /= denominator
        
        return fixed_frequency

    def screen_dimensions(self):
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy

        return screen_width, screen_height

    def on_off_simulation(self, on_button):
        if on_button:
            pygame.init()
            return
        
        pygame.quit()

    def screen_element(self, screen_width, screen_height):
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Doppler simulator")

        return screen


    def set_background_image(self, screen_width, screen_height, screen):
        background_image = pygame.image.load("road-image.jpg")
        background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
        screen.blit(background_image, (0, 0))

    def character_position(self, screen_width, screen_height):
        x_character_position = 0.7*screen_width 
        y_character_position = 0.5*screen_height

        return x_character_position, y_character_position

    def pygame_render(self, screen, character, car,
                    x_char, y_char, car_x, car_y):
        
        screen.blit(character, (x_char, y_char))
        screen.blit(car, (car_x, car_y))
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    def car_position_reset(self, x_car, count, screen_width,
                        instant_source_speed):
        positive_direction_end = instant_source_speed > 0 and x_car[count] > screen_width
        negative_direction_end = instant_source_speed < 0 and x_car[count] < -450

        if positive_direction_end:
            return 0
        elif negative_direction_end:
            return _np.argmin(_np.abs(x_car - screen_width))
        
        return count

    def create_doppler_animation(self, character, car, instant_source_speed):

        self.on_off_simulation(on_button=True)

        screen_width, screen_height = self.screen_dimensions()
        screen = self.screen_element(screen_width, screen_height)

        x_char, y_char = self.character_position(screen_width, screen_height)
        time_elapsed = _np.linspace(-50, screen_width, 1000)
        x_car = instant_source_speed * time_elapsed

        count=0
        keepGoing = True

        while keepGoing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False

            self.set_background_image(screen_width, screen_height, screen)
            
            if instant_source_speed > 0:
                count = self.car_position_reset(x_car, count, screen_width, instant_source_speed)
                self.pygame_render(screen, character, car, x_char, y_char, x_car[count], 0.65*screen_height)
                count+=1
            else:
                count = self.car_position_reset(-x_car, count, screen_width, instant_source_speed)
                self.pygame_render(screen, character, car, x_char, y_char, -x_car[count], 0.65*screen_height)
                count-=1

        self.on_off_simulation(on_button=False)  