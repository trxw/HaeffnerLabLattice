from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.PulseSequences.branching_ratio import branching_ratio as sequence
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.fly_processing import Binner
import time
import numpy
       
class branching_ratio(experiment):
    
    name = 'BranchingRatio'
    
    required_parameters = [
                           ('BranchingRatio','save_timetags_every'),
                           ('BranchingRatio','pulse_sequence_repetition'),
                           ]
    required_parameters.extend(sequence.required_parameters)
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = cxn.data_vault
        self.pulser = cxn.pulser
        self.binned_save_context = cxn.context()
        self.timetags_since_last_binsave = 0
        self.save_timetags_every = 25000
        
        #calculate cycle. from sequence? self.binner = Binner(self.timetag_record_cycle, 100e-9)

    
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.spectrum_save_context)
        self.dv.new('Spectrum {}'.format(datasetNameAppend),[('Freq', 'MHz')],[('Excitation Probability','Arb','Arb')], context = self.spectrum_save_context)
        window_name = self.parameters.get('Spectrum.window_name', ['Spectrum'])
        self.dv.add_parameter('Window', window_name, context = self.spectrum_save_context)
        self.dv.add_parameter('plotLive', True, context = self.spectrum_save_context)
        
        
        self.dv.cd(directory , context = self.binned_save_context)
        
    def setup_pulser(self):
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
        self.program_pulser()
        self.pulser.reset_timetags()
        
    def program_pulser(self):
        seq = sequence(**self.sequence_parameters)
        seq.programSequence(self.pulser)
        self.timetag_record_cycle = seq.timetag_record_cycle['s']
        self.start_recording_timetags = seq.start_recording_timetags['s']

    def run(self):
        sequences_back_to_back = int(self.check_parameter(self.p.sequences_back_to_back, keep_units = False))
        total_cycles = int(self.check_parameter(self.p.total_cycles, keep_units = False))
        cycles_per_sequence = int(self.sequence_parameters['cycles_per_sequence'].value)
        cycles_per_timetags_transfer = cycles_per_sequence * sequences_back_to_back
        transfers = int(total_cycles / float(cycles_per_timetags_transfer))
        #make sure do at least one transfer
        transfers = max(transfers, 1)
        self.dv.add_parameter('transfers', transfers)
        for index in range(transfers):  
            self.percentDone = 100.0 * index / float(transfers)
            should_continue = self.sem.block_experiment(self.experimentPath, self.percentDone)
            if not should_continue:
                print 'Not Continuing'
                return
            else:
                #run back to back sequences
                self.pulser.start_number(sequences_back_to_back)
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                #get timetags and save
                timetags = self.pulser.get_timetags().asarray
                if timetags.size >= 32767:
                    raise Exception("Timetags Overflow, should reduce number of back to back pulse sequences")
                iters = index * numpy.ones_like(timetags)
                #save timetags as we get them
                self.dv.add(numpy.vstack((iters,timetags)).transpose())
                #collapse the timetags onto a single cycle starting at 0
                timetags = timetags - self.start_recording_timetags
                timetags = timetags % self.timetag_record_cycle
                self.binner.add(timetags, sequences_back_to_back * cycles_per_sequence)
                print 'saved {} timetags'.format(len(timetags))
                self.timetags_since_last_binsave += timetags.size
                if self.timetags_since_last_binsave > self.save_timetags_every:
                    self.save_histogram()
                    self.timetags_since_last_binsave = 0
                    self.save_timetags_every *= 2
        self.percentDone = 100.0
                
    def save_histogram(self, force = False):
        bins, hist = self.binner.getBinned()
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        self.dv.new('Binned {}'.format(datasetNameAppend),[('Time', 'us')],[('CountRate','Counts/sec','Counts/sec')], context = self.binned_save_context )
        self.dv.add_parameter('plotLive',self.p.plot_live_parameter, context = self.binned_save_context)
        self.dv.add_parameter('Window', self.p.window_name, context = self.binned_save_context)
        self.dv.add(numpy.vstack((bins,hist)).transpose(), context = self.binned_save_context )
    
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.spectrum_save_context)
    
    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)
        
    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)          

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = branching_ratio(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)