import numpy as _np
import matplotlib.pyplot as _plt
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
        sound_velocity = self._ccp * self._ugc * self._temperature
        sound_velocity /= self._mol_mass
        sound_velocity = _np.sqrt(sound_velocity)
        return sound_velocity
    
    @property
    def sound_velocity(self):
        return self._sound_velocity
    
    @sound_velocity.setter
    def set_sound_velocity(self, ccp, ugc, temperature, molar_mass):
        new_sound_velocity = ccp * ugc * temperature
        new_sound_velocity /= molar_mass
        self._sound_velocity = _np.sqrt(new_sound_velocity)

    def _time_elapsed_calculator(self, final_time):
        time_elapsed = _np.linspace(0, final_time)

        return time_elapsed

    
    def _beholder_and_source_velocity(self, time_elapsed,
                                linear_coef, angular_coef=0):
        """This method supports only MU and MUV"""
        size_time_array = time_elapsed.size
        ones = _np.ones(size_time_array)
        velocity = angular_coef * time_elapsed + linear_coef * ones

        return velocity
    
    def _frequencyMUV_calculator(self, f0, 
                             beholder_velocity, source_velocity, 
                             distance_increases, same_direction):
        """This method works only if the velocities are positive"""

        if distance_increases:
            source_velocity = -source_velocity

        if not same_direction:
            beholder_velocity = -beholder_velocity

        numerator = self.sound_velocity + source_velocity
        denominator = self.sound_velocity + beholder_velocity 

        fixed_frequency = f0*numerator
        fixed_frequency /= denominator
        
        return fixed_frequency
    
    def doppler_graphic_generator(self, f0, beholder_linear_coef, 
                                  beholder_ang_coef,source_linear_coef, 
                                  source_ang_coef, final_time, 
                                  distance_increases, same_direction):
        
        time_elapsed = self._time_elapsed_calculator(final_time)

        source_velocity = self._beholder_and_source_velocity(time_elapsed,
                                        source_linear_coef, source_ang_coef)
        
        beholder_velocity = self._beholder_and_source_velocity(time_elapsed,
                                    beholder_linear_coef, beholder_ang_coef)

        fixed_frequencies = self._frequencyMUV_calculator(f0,
                                        beholder_velocity,source_velocity,
                                        distance_increases, same_direction)
        

        fig, ax = _plt.subplots(figsize=(12,7))
        ax.set_title("Gráfico da frequência aparente", fontsize=18)

        ax.plot(time_elapsed, fixed_frequencies, color="blue")
        ax.tick_params(axis="both", labelsize=15)
        ax.set_xlabel(r"Tempo transcorrido ($s$)", fontsize=16)
        ax.set_ylabel(r"Frequência observada ($Hz$)", fontsize=16)

    def screen_dimensions(self):
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()

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

    def image_increment_calculator(self, image_index, size_array_image):
        if image_index == size_array_image-1:
            return 0
        else:
            return image_index + 1

    def car_position_reset(self, x_car, count, screen_width,
                        instant_source_speed, image_index, size_array_image):
        positive_direction_end = instant_source_speed > 0 and x_car[count] > screen_width
        negative_direction_end = instant_source_speed < 0 and x_car[count] < -450
        index = self.image_increment_calculator(image_index, size_array_image)

        if positive_direction_end:
            return 0, index
        elif negative_direction_end:
            return _np.argmin(_np.abs(x_car - screen_width)), index
        
        return count, index - 1
    
    def return_params(self, instant_source_speed):
        screen_width, screen_height = self.screen_dimensions()
        screen = self.screen_element(screen_width, screen_height)

        x_char, y_char = self.character_position(screen_width, screen_height)
        time_elapsed = _np.linspace(-50, screen_width, 1000)
        x_car = instant_source_speed * time_elapsed

        return screen, screen_width, screen_height, x_char, y_char, x_car


    def create_doppler_animation(self, character, vehicles_array, instant_source_speed):

        self.on_off_simulation(on_button=True)
        screen, screen_width, screen_height, x_char, y_char, x_car = self.return_params(instant_source_speed)
    
        image_index, count, correction_factor  = 0, 0, 1
        if instant_source_speed < 0:
            correction_factor = -1

        array_size = vehicles_array.size
        keepGoing = True

        while keepGoing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False

            self.set_background_image(screen_width, screen_height, screen)
            count, image_index = self.car_position_reset(correction_factor* x_car, count, 
                                                         screen_width, instant_source_speed, 
                                                         image_index, array_size)
            self.pygame_render(screen, character, 
                               vehicles_array[image_index], x_char, y_char,
                               correction_factor * x_car[count], 0.65*screen_height)
            
            if instant_source_speed > 0:
                count+=1
            else:
                count-=1

        self.on_off_simulation(on_button=False)  