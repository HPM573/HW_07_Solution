from deampy.sample_path import PrevalenceSamplePath


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
        self.nPatientsReceivedMHConsult = 0  # number of patients who received MH consultation
        self.patientTimeInSystem = []   # observations on patients time in urgent care
        self.patientTimeInPCPWaitingRoom = []  # observations on patients time in the waiting room
        self.patientTimeInMHWaitingRoom = []  # observations on patients time in MH waiting room

        self.patientSummary = []    # id, tArrived, tLeft, duration waited, duration in the system
        if self.traceOn:
            self.patientSummary.append(
                ['Patient', 'Time Arrived', 'Time Left', 'Time Waited', 'Time In the System'])

        # sample path for the patients waiting
        # prevalence sample path: # of people in the waiting room to see a PCP
        self.nPatientsWaitingPCP = PrevalenceSamplePath(
            name='Number of patients waiting for PCP', initial_size=0)

        # sample path for the patients waiting for MHS
        self.nPatientsWaitingMH = PrevalenceSamplePath(
            name='Number of patients waiting for MHS', initial_size=0)

        # sample path for the patients in system
        self.nPatientInSystem = PrevalenceSamplePath(
            name='Number of patients in the urgent care', initial_size=0)

        # sample path for PCP utilization
        self.nPCPBusy = PrevalenceSamplePath(
            name='Utilization of PCP', initial_size=0
        )

        # sample path for MHS utilization
        self.nMHSBusy = PrevalenceSamplePath(
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

    def collect_patient_joining_pcp_waiting_room(self, patient):
        """ collects statistics when a patient joins the pcp waiting room
        :param patient: the patient who is joining the pcp waiting room
        """

        # store the time this patient joined the pcp waiting room
        patient.tJoinedPCPWaitingRoom = self.simCal.time

        # update the sample path of patients waiting for see pcp
        self.nPatientsWaitingPCP.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_joining_mh_waiting_room(self, patient):
        """ collects statistics when a patient joins the waiting room for mental health specialist (MHS)
        :param patient: the patient who is joining the waiting room for MHS
        """

        # store the time this patient joined the waiting room
        patient.tJoinedMHWaitingRoom = self.simCal.time

        # update the sample path of patients waiting
        self.nPatientsWaitingMH.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_leaving_pcp_waiting_room(self, patient):
        """ collects statistics when a patient leave the PCP waiting room
        :param patient: the patient who is leave the PCP waiting room
        """

        # store the time this patient leaves the PCP waiting room
        patient.tLeftPCPWaitingRoom = self.simCal.time

        # update the sample path
        self.nPatientsWaitingPCP.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_leaving_mh_waiting_room(self, patient):
        """ collects statistics when a patient leave the MHS waiting room
        :param patient: the patient who is leave the MHS waiting room
        """

        # store the time this patient leaves the MHS waiting room
        patient.tLeftMHWaitingRoom = self.simCal.time

        # update the sample path
        self.nPatientsWaitingMH.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_departure(self, patient):
        """ collects statistics for a departing patient
        :param patient: the departing patient
        """

        self.nPatientsServed += 1
        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=-1)

        time_in_system = self.simCal.time - patient.tArrived
        if patient.tJoinedPCPWaitingRoom is None:
            time_waiting_pcp = 0
        else:
            time_waiting_pcp = patient.tLeftPCPWaitingRoom - patient.tJoinedPCPWaitingRoom

        self.patientTimeInPCPWaitingRoom.append(time_waiting_pcp)
        self.patientTimeInSystem.append(time_in_system)

        if patient.ifWithDepression:
            self.nPatientsReceivedMHConsult += 1
            if patient.tJoinedMHWaitingRoom is None:
                time_waiting_mh = 0
            else:
                time_waiting_mh = patient.tLeftMHWaitingRoom - patient.tJoinedMHWaitingRoom

            self.patientTimeInMHWaitingRoom.append(time_waiting_mh)
            self.nMHSBusy.record_increment(time=self.simCal.time, increment=-1)

        # build the patient summary
        if self.traceOn:
            self.patientSummary.append([
                str(patient),        # name
                patient.tArrived,    # time arrived
                self.simCal.time,    # time left
                time_waiting_pcp,        # time waiting
                time_in_system]      # time in the system
            )

    def collect_patient_starting_pcp_exam(self):
        """ collects statistics for a patient who just started the exam with a pcp """

        self.nPCPBusy.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_ending_pcp_exam(self):

        self.nPCPBusy.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_starting_mh_exam(self):
        """ collects statistics for a patient who just started the mh consult """

        self.nMHSBusy.record_increment(time=self.simCal.time, increment=1)

    def collect_end_of_simulation(self):
        """
        collects the performance statistics at the end of the simulation
        """

        # update sample paths
        self.nPatientsWaitingMH.close(time=self.simCal.time)
        self.nPatientsWaitingPCP.close(time=self.simCal.time)
        self.nPatientInSystem.close(time=self.simCal.time)
        self.nPCPBusy.close(time=self.simCal.time)
        self.nMHSBusy.close(time=self.simCal.time)

    def get_ave_patient_time_in_system(self):
        """
        :return: average patient time in system
        """

        return sum(self.patientTimeInSystem)/len(self.patientTimeInSystem)

    def get_ave_patient_waiting_time(self):
        """
        :return: average patient waiting time
        """

        return sum(self.patientTimeInPCPWaitingRoom)/len(self.patientTimeInPCPWaitingRoom)

    def get_ave_patient_mh_waiting_time(self):
        """
        :return: average patient waiting time for MHS
        """

        return sum(self.patientTimeInMHWaitingRoom)/len(self.patientTimeInMHWaitingRoom)
