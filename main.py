import sched, time
import datetime

# from subprocess import call
import alsaaudio

class Singleton(type):
    _instances = {}

    def __cal__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton)
        return cls._instances[cls]
        


class SystemVolumeController(metaclass=Singleton):

    def __init__(self):
        self.volume = 0
        self.default_volume = 70
        self.policy = SilencePolicy(silence_from_minute= 59, sound_from_minute = 7)
        self.volume_handler = VolumePCHandler()
        self.previous_volume = self.volume_handler.get_volume()

    def update_volume(self,new_volume : int):
        self.previous_volume = self.volume
        print(f"New Volume = {new_volume}, Previous Volume = {self.previous_volume}")
        self.volume_handler.set_volume(new_volume)
        self.volume = new_volume

    def is_silent(self):
        if self.volume < 5:
            return True
        else:
            return False

    def should_be_silent(self, time):
        should_be_silent = self.policy.check_silence(time)
        return should_be_silent

    def check_for_updates(self, time):
        print(f"check for updates at: {time}")
        system_volume = self.volume_handler.get_volume()
        print(system_volume)
        if self.volume !=system_volume :
            self.update_volume(system_volume)

        if ((not self.is_silent()) and (self.should_be_silent(time))):
            self.update_volume(2)
        if ((self.is_silent()) and (not self.should_be_silent(time))):
            self.update_volume(self.previous_volume)


class VolumePCHandler:
    def __init__(self):
        self.m = alsaaudio.Mixer()

    def set_volume(self, new_volume):
        valid = False

        while not valid:
            try:
                new_volume = int(new_volume)

                if (new_volume <= 100) and (new_volume >= 0):
                   self.m.setvolume(new_volume)
                   valid = True
            except ValueError:
                pass

    def get_volume(self):
        self.m.close()
        self.m = alsaaudio.Mixer()
        [volume1, _] = self.m.getvolume()
        print(f"current volume ss= {volume1}")
        return volume1



class SilencePolicy():

    def __init__(self, silence_from_minute, sound_from_minute):
        self.silence_from_minute = silence_from_minute
        self.sound_from_minute = sound_from_minute

    def check_silence(self, current_time):
        if self.silence_from_minute < self.sound_from_minute:
            if current_time > silence_from_minute and current_time < sound_from_minute:
                return True
            else:
                return False
        if self.sound_from_minute < self.silence_from_minute:
            if current_time > self.silence_from_minute:
                return True
            elif current_time < self.sound_from_minute:
                return True
            else:
                return False
        if self.sound_from_minute == self.silence_from_minute:
            print(f"warning Silence policy has same value for sound and silence from minute")
            return False


if __name__ == "__main__":
    volume_handler = SystemVolumeController()
    

    running = True
    while running:
        now = datetime.datetime.now()
        minutes = now.minute
        volume_handler.check_for_updates(minutes)
        time.sleep(3)