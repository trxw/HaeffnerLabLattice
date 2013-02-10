from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence 

class doppler_cooling(pulse_sequence):
    
    
    required_parameters = [
                           'doppler_cooling_frequency_397', 
                           'doppler_cooling_amplitude_397', 
                           'doppler_cooling_frequency_866', 
                           'doppler_cooling_amplitude_866', 
                           'doppler_cooling_duration',
                           'doppler_cooling_repump_additional'
                           ]
    
    def sequence(self):
        pulses = self.dds_pulses
        repump_duration = self.doppler_cooling_duration + self.doppler_cooling_repump_additional
        pulses.append( ('110DP',self.start, self.doppler_cooling_duration, self.doppler_cooling_frequency_397, self.doppler_cooling_amplitude_397) )
        pulses.append( ('866DP',self.start, repump_duration, self.doppler_cooling_frequency_866, self.doppler_cooling_amplitude_866) )
        self.end = self.start + repump_duration