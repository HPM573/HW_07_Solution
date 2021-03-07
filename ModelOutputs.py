import SimPy.SamplePath as Path
import SimPy.FormatFunctions as F
import InputData as D


class SimOutputs:
    # to collect the outputs of a simulation run

    def __init__(self, sim_cal, trace_on=False):
        """
        :param sim_cal: simulation calendar
        :param trace_on: set to True to report patient summary
        """

        self.simCal = sim_cal           # simulation calendar (to know the current time)
        self.traceOn = trace_on         # if should prepare patient summary report
        self.nPatientsArrived = 0       # number of patients arrived
        self.nPatientsServed = 0         # number of patients served
        self.nPatientsReceivedConsult = 0 # number of patients who received MH consultation
        self.patientTimeInSystem = []   # observations on patients time in urgent care
        self.patientTimeInWaitingRoom = []  # observations on patients time in the waiting room
        self.patientTimeInMentalHealthWaiting = []  # observations on patients time in MH waiting room

        self.patientSummary = []    # id, tArrived, tLeft, duration waited, duration in the system
        if self.traceOn:
            self.patientSummary.append(
                ['Patient', 'Time Arrived', 'Time Left', 'Time Waited', 'Time In the System'])

        # sample path for the patients waiting: CONTINUOUS
        # prevalence sample path: # of people in the waiting room
        self.nPatientsWaiting = Path.PrevalenceSamplePath(
            name='Number of patients waiting', initial_size=0)

        # sample path for the patients waiting for MHS
        self.nPatientsWaitingMH = Path.PrevalenceSamplePath(
            name='Number of patients waiting for MHS', initial_size=0)

        # sample path for the patients in system
        self.nPatientInSystem = Path.PrevalenceSamplePath(
            name='Number of patients in the urgent care', initial_size=0)

        # sample path for PCP utilization
        self.nExamRoomBusy = Path.PrevalenceSamplePath(
            name='Utilization of PCP', initial_size=0
        )

        # sample path for MHS utilization
        self.nMentalHealthBusy = Path.PrevalenceSamplePath(
            name='Utilization of Mental Health Specialist', initial_size=0
        )

    def collect_patient_arrival(self, patient):
        """ collects statistics upon arrival of a patient
        :param patient: the patient who just arrived
        """

        # increment the number of patients arrived
        self.nPatientsArrived += 1

        # update the sample path of patients in the system
        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=1)

        # store arrival time of this patient
        patient.tArrived = self.simCal.time

    def collect_patient_joining_waiting_room(self, patient):
        """ collects statistics when a patient joins the waiting room
        :param patient: the patient who is joining the waiting room
        """

        # store the time this patient joined the waiting room
        patient.tJoinedWaitingRoom = self.simCal.time

        # update the sample path of patients waiting
        self.nPatientsWaiting.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_joining_mh_waiting_room(self, patient):
        """ collects statistics when a patient joins the waiting room
        :param patient: the patient who is joining the waiting room
        """

        # store the time this patient joined the waiting room
        patient.tJoinedWaitingRoomMH = self.simCal.time

        # update the sample path of patients waiting
        self.nPatientsWaitingMH.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_leaving_waiting_room(self, patient):
        """ collects statistics when a patient leave the waiting room
        :param patient: the patient who is leave the waiting room
        """

        # store the time this patient leaves the waiting room
        patient.tLeftWaitingRoom = self.simCal.time

        # update the sample path
        self.nPatientsWaiting.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_leaving_mh_waiting_room(self, patient):
        """ collects statistics when a patient leave the waiting room
        :param patient: the patient who is leave the waiting room
        """

        # store the time this patient leaves the waiting room
        patient.tLeftWaitingRoomMH = self.simCal.time

        # update the sample path
        self.nPatientsWaitingMH.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_departure(self, patient):
        """ collects statistics for a departing patient
        :param patient: the departing patient
        """

        self.nPatientsServed += 1
        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=-1)

        time_in_system = self.simCal.time - patient.tArrived
        time_waiting_exam = patient.tLeftWaitingRoom - patient.tJoinedWaitingRoom
        self.patientTimeInWaitingRoom.append(time_waiting_exam)
        self.patientTimeInSystem.append(time_in_system)

        if patient.ifWithDepression:
            self.nPatientsReceivedConsult += 1
            time_waiting_mh = patient.tLeftWaitingRoomMH - patient.tJoinedWaitingRoomMH
            self.patientTimeInMentalHealthWaiting.append(time_waiting_mh)
            self.nMentalHealthBusy.record_increment(time=self.simCal.time, increment=-1)

        # build the patient summary
        if self.traceOn:
            self.patientSummary.append([
                str(patient),        # name
                patient.tArrived,    # time arrived
                self.simCal.time,    # time left
                time_waiting_exam,        # time waiting
                time_in_system]      # time in the system
            )

    def collect_patient_starting_exam(self):
        """ collects statistics for a patient who just started the exam """

        self.nExamRoomBusy.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_ending_exam(self):

        self.nExamRoomBusy.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_starting_mh_exam(self):
        """ collects statistics for a patient who just started the mh consult """

        self.nMentalHealthBusy.record_increment(time=self.simCal.time, increment=1)

    def collect_end_of_simulation(self):
        """
        collects the performance statistics at the end of the simulation
        """

        # update sample paths
        self.nPatientsWaitingMH.close(time=self.simCal.time)
        self.nPatientsWaiting.close(time=self.simCal.time)
        self.nPatientInSystem.close(time=self.simCal.time)
        self.nExamRoomBusy.close(time=self.simCal.time)
        self.nMentalHealthBusy.close(time=self.simCal.time)

    def get_ave_patient_time_in_system(self):
        """
        :return: average patient time in system
        """

        return sum(self.patientTimeInSystem)/len(self.patientTimeInSystem)

    def get_ave_patient_waiting_time(self):
        """
        :return: average patient waiting time
        """

        return sum(self.patientTimeInWaitingRoom)/len(self.patientTimeInWaitingRoom)

    def get_ave_patient_mh_waiting_time(self):
        """
        :return: average patient waiting time for MHS
        """

        return sum(self.patientTimeInMentalHealthWaiting)/len(self.patientTimeInMentalHealthWaiting)
