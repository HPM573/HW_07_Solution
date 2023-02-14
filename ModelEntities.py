from ModelEvents import Arrival, EndOfExam, EndOfMentalHealthConsult


class Patient:
    def __init__(self, id, if_with_depression):
        """ create a patient
        :param id: (integer) patient ID
        :param if_with_depression: (bool) set to true if the patient has depression
        """
        self.id = id
        self.ifWithDepression = if_with_depression
        self.tJoinedPCPWaitingRoom = None
        self.tLeftPCPWaitingRoom = None
        self.tJoinedMHWaitingRoom = None
        self.tLeftMHWaitingRoom = None

    def __str__(self):
        return "Patient " + str(self.id)


class PCPWaitingRoom:
    def __init__(self, sim_out, trace):
        """ create a waiting room
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        self.patientsWaiting = []   # list of patients in the waiting room
        self.simOut = sim_out
        self.trace = trace

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # update statistics for the patient who joins the waiting room
        self.simOut.collect_patient_joining_pcp_waiting_room(patient=patient)

        # add the patient to the list of patients waiting
        self.patientsWaiting.append(patient)

        # trace
        self.trace.add_message(
            str(patient) + ' joins the waiting room. Number waiting = ' + str(len(self.patientsWaiting)) + '.')

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """

        # update statistics for the patient who leaves the waiting room
        self.simOut.collect_patient_leaving_pcp_waiting_room(patient=self.patientsWaiting[0])

        # trace
        self.trace.add_message(
            str(self.patientsWaiting[0]) + ' leaves the waiting room. Number waiting = '
            + str(len(self.patientsWaiting) - 1) + '.')

        # pop the patient
        return self.patientsWaiting.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patientsWaiting)


class MHWaitingRoom:
    def __init__(self, sim_out, trace):
        """ create a waiting room
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        self.patientsWaitingMH = []   # list of patients in the MH waiting room
        self.simOut = sim_out
        self.trace = trace

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # update statistics for the patient who joins the waiting room
        self.simOut.collect_patient_joining_mh_waiting_room(patient=patient)

        # add the patient to the list of patients waiting
        self.patientsWaitingMH.append(patient)

        # trace
        self.trace.add_message(
            str(patient) + ' joins the MH waiting room. Number waiting = ' + str(len(self.patientsWaitingMH)) + '.')

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """

        # update statistics for the patient who leaves the waiting room
        self.simOut.collect_patient_leaving_mh_waiting_room(patient=self.patientsWaitingMH[0])

        # trace
        self.trace.add_message(
            str(self.patientsWaitingMH[0]) + ' leaves the MH waiting room. Number waiting = '
            + str(len(self.patientsWaitingMH) - 1) + '.')

        # pop the patient
        return self.patientsWaitingMH.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patientsWaitingMH)


class Physician:
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create a physician
        :param id: (integer) the physician ID
        :param service_time_dist: distribution of service time
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        self.id = id
        self.serviceTimeDist = service_time_dist
        self.urgentCare = urgent_care
        self.simCal = sim_cal
        self.simOut = sim_out
        self.trace = trace
        self.isBusy = False
        self.patientBeingServed = None  # the patient who is being served


class PCP(Physician):
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create a primary care physician
        :param id: (integer) id
        :param service_time_dist: distribution of service time
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        Physician.__init__(self, id=id, service_time_dist=service_time_dist, urgent_care=urgent_care, sim_cal=sim_cal,
                           sim_out=sim_out, trace=trace)

    def __str__(self):
        """ :returns (string) the PCP ID """
        return "PCP " + str(self.id)

    def exam(self, patient, rng):
        """ starts examining on the patient
        :param patient: a patient
        :param rng: random number generator
        """

        # the physician is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # collect statistics
        self.simOut.collect_patient_starting_pcp_exam()

        # find the exam completion time (current time + service time)
        exam_completion_time = self.simCal.time + self.serviceTimeDist.sample(rng=rng)

        # schedule the end of exam
        self.simCal.add_event(
            event=EndOfExam(time=exam_completion_time, physician=self, urgent_care=self.urgentCare)
        )

    def remove_patient(self):
        """ :returns the patient that was being served by this physician"""

        # store the patient to be returned and set the patient that was being served to None
        returned_patient = self.patientBeingServed
        self.patientBeingServed = None

        # the physician is idle now
        self.isBusy = False

        # collect statistics
        self.simOut.collect_patient_ending_pcp_exam()

        if returned_patient.ifWithDepression is False:
            # collect statistics
            self.simOut.collect_patient_departure(patient=returned_patient)

            # trace
            self.trace.add_message(str(returned_patient) + ' leaves ' + str(self) + '.')

        return returned_patient


class MHP(Physician):
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create a mental health physician
        :param id: (integer) the room ID
        :param service_time_dist: distribution of service time
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        Physician.__init__(self, id=id, service_time_dist=service_time_dist, urgent_care=urgent_care, sim_cal=sim_cal,
                           sim_out=sim_out, trace=trace)

    def __str__(self):
        """ :returns (string) the mental health physican id """
        return "MHP " + str(self.id)

    def consult(self, patient, rng):
        """ starts mental health consultation for this patient
        :param patient: a patient
        :param rng: random number generator
        """

        # the room is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # collect statistics
        self.simOut.collect_patient_starting_mh_exam()

        # find the exam completion time (current time + service time)
        exam_completion_time = self.simCal.time + self.serviceTimeDist.sample(rng=rng)

        # schedule the end of exam
        self.simCal.add_event(
            event=EndOfMentalHealthConsult(time=exam_completion_time,
                                           consult_room=self,
                                           urgent_care=self.urgentCare)
        )

    def remove_mh_patient(self):
        """ :returns the patient that was being served by mental health physician """

        # store the patient to be returned and set the patient that was being served to None
        returned_patient = self.patientBeingServed
        self.patientBeingServed = None

        # the physician is idle now
        self.isBusy = False

        # collect statistics
        self.simOut.collect_patient_departure(patient=returned_patient)

        # trace
        self.trace.add_message(str(returned_patient) + ' leaves ' + str(self) + '.')

        return returned_patient


class UrgentCare:
    def __init__(self, id, parameters, sim_cal, sim_out, trace):
        """ creates an urgent care
        :param id: ID of this urgent care
        :param sim_cal: simulation calendar
        :parameters: parameters of this urgent care
        """

        self.id = id                   # urgent care id
        self.params = parameters  # parameters of this urgent care
        self.simCal = sim_cal
        self.simOutputs = sim_out
        self.trace = trace

        self.ifOpen = True  # if the urgent care is open and admitting new patients

        # waiting room
        self.waitingRoom = PCPWaitingRoom(sim_out=self.simOutputs,
                                          trace=self.trace)

        # PCPs
        self.PCPs = []
        for i in range(0, self.params.nPCPs):
            self.PCPs.append(PCP(id=i,
                                 service_time_dist=self.params.examTimeDist,
                                 urgent_care=self,
                                 sim_cal=self.simCal,
                                 sim_out=self.simOutputs,
                                 trace=self.trace))

        # waiting room for mental health consultation
        self.mhConsultWaitingRoom = MHWaitingRoom(sim_out=self.simOutputs,
                                                  trace=self.trace)

        # create the mental health consultation room
        self.MHP = MHP(id=0,
                       service_time_dist=self.params.mentalHealthConsultDist,
                       urgent_care=self,
                       sim_cal=self.simCal,
                       sim_out=self.simOutputs,
                       trace=self.trace)

    def process_new_patient(self, patient, rng):
        """ receives a new patient
        :param patient: the new patient
        :param rng: random number generator
        """

        # trace
        self.trace.add_message(
            'Processing arrival of ' + str(patient) + '.')

        # do not admit the patient if the urgent care is closed
        if not self.ifOpen:
            self.trace.add_message('Urgent care is closed. '+str(patient)+' does not get admitted.')
            return

        # collect statistics on new patient
        self.simOutputs.collect_patient_arrival(patient=patient)

        # check if anyone is waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:
            # if anyone is waiting, add the patient to the waiting room
            self.waitingRoom.add_patient(patient=patient)
        else:
            # find an idle physician
            idle_pcp_found = False
            for pcp in self.PCPs:
                # if this pcp is busy
                if not pcp.isBusy:
                    # send the last patient to this pcp
                    pcp.exam(patient=patient, rng=rng)
                    idle_pcp_found = True
                    # break the for loop
                    break

            # if no idle pcp was found
            if not idle_pcp_found:
                # add the patient to the waiting room
                self.waitingRoom.add_patient(patient=patient)

        # find the arrival time of the next patient (current time + time until next arrival)
        next_arrival_time = self.simCal.time + self.params.arrivalTimeDist.sample(rng=rng)

        # find the depression status of the next patient
        if_with_depression = False
        if rng.random_sample() < self.params.probDepression:
            if_with_depression = True

        # schedule the arrival of the next patient
        self.simCal.add_event(
            event=Arrival(
                time=next_arrival_time,
                patient=Patient(id=patient.id + 1, if_with_depression=if_with_depression),
                urgent_care=self
            )
        )

    def process_end_of_exam(self, physician, rng):
        """ processes the end of exam in the specified exam room
        :param physician: the exam room where the service is ended
        :param rng: random number generator
        """

        # trace
        self.trace.add_message('Processing end of exam in ' + str(physician) + '.')

        # get the patient who is about to be discharged
        this_patient = physician.remove_patient()

        # check the mental health status of the patient
        if this_patient.ifWithDepression:
            # send the patient to the mental health specialist
            # if the mental health specialist is busy
            if self.MHP.isBusy:
                # the patient will join the waiting room in the mental health unity
                self.mhConsultWaitingRoom.add_patient(patient=this_patient)
            else:
                # this patient starts receiving mental health consultation
                self.MHP.consult(patient=this_patient, rng=rng)

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:

            # start serving the next patient in line
            physician.exam(patient=self.waitingRoom.get_next_patient(), rng=rng)

    def process_end_of_consultation(self, mhp, rng):
        """ process the end of mental health consultation
        :param mhp: mental health physician
        :param rng: random number generator
        """

        # trace
        self.trace.add_message('Processing end of mental health consult in ' + str(mhp) + '.')

        # get the patient who is about to be discharged
        this_patient = mhp.remove_mh_patient()

        # check if there is any patient waiting
        if self.mhConsultWaitingRoom.get_num_patients_waiting() > 0:
            # start serving the next patient in line
            mhp.consult(patient=self.mhConsultWaitingRoom.get_next_patient(), rng=rng)

    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # trace
        self.trace.add_message('Processing the closing of the urgent care.')

        # close the urgent care
        self.ifOpen = False

