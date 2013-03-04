from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from RabiExcitation import rabi_excitation
from treedict import TreeDict
from labrad.units import WithUnit

class tomography_excitation(pulse_sequence):
    
    required_parameters = [ 
                           ('Tomography','rabi_pi_time'),
                           ('Tomography','iteration'),
                           ('Tomography','tomography_excitation_frequency'),
                           ('Tomography','tomography_excitation_amplitude'),
                          ]

    required_subsequences = [rabi_excitation]
    
    def sequence(self):
        print 'in tomography excitation, my frequency is: ', self.parameters.Tomography.tomography_excitation_frequency
        print 'in tomography excitation, my rabi pi time is: ', self.parameters.Tomography.rabi_pi_time
        
        t = self.parameters.Tomography
        iteration = int(t.iteration)
        if not iteration in range(3):
            raise Exception ("Incorrect iteration of tomography {}".format(iteration))
        if iteration == 0:
            pass
        elif iteration == 1:
            replace = TreeDict.fromdict({
                                        'Excitation_729.rabi_excitation_frequency':t.tomography_excitation_frequency,
                                        'Excitation_729.rabi_excitation_amplitude':t.tomography_excitation_amplitude,
                                        'Excitation_729.rabi_excitation_duration':t.rabi_pi_time / 2.0,
                                        'Excitation_729.rabi_excitation_phase':WithUnit(0, 'deg'),
                                        })
            self.addSequence(rabi_excitation, replace)
        elif iteration == 2:
            replace = TreeDict.fromdict({
                            'Excitation_729.rabi_excitation_frequency':t.tomography_excitation_frequency,
                            'Excitation_729.rabi_excitation_amplitude':t.tomography_excitation_amplitude,
                            'Excitation_729.rabi_excitation_duration':t.rabi_pi_time / 2.0,
                            'Excitation_729.rabi_excitation_phase':WithUnit(90, 'deg'),
                            })
            self.addSequence(rabi_excitation, replace)