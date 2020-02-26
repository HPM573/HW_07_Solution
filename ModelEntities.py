import SimPy.DiscreteEventSim as SimCls
import SimPy.RandomVariantGenerators as RVGs
import ModelEvents as E


class Patient:
    def __init__(self, id, if_with_depression):
        """ create a patient
        :param id: (integer) patient ID
        :param if_with_depression: (bool) set to true if the patient has depression
        """
        self.id = id
        self.ifWithDepression = if_with_depression
        self.tJoinedWaitingRoom = 0
        self.tLeftWaitingRoom = 0
        self.tLeftWaitingRoomMH = 0
        self.tJoinedWaitingRoomMH = 0

    def __str__(self):
        return "Patient " + str(self.id)


class WaitingRoom:
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
        self.simOut.collect_patient_joining_waiting_room(patient=patient)

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
        self.simOut.collect_patient_leaving_waiting_room(patient=self.patientsWaiting[0])

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
        self.patientsWaiting = []   # list of patients in the MH waiting room
        self.simOut = sim_out
        self.trace = trace

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # update statistics for the patient who joins the waiting room
        self.simOut.collect_patient_joining_mh_waiting_room(patient=patient)

        # add the patient to the list of patients waiting
        self.patientsWaiting.append(patient)

        # trace
        self.trace.add_message(
            str(patient) + ' joins the MH waiting room. Number waiting = ' + str(len(self.patientsWaiting)) + '.')

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """

        # update statistics for the patient who leaves the waiting room
        self.simOut.collect_patient_leaving_mh_waiting_room(patient=self.patientsWaiting[0])

        # trace
        self.trace.add_message(
            str(self.patientsWaiting[0]) + ' leaves the MH waiting room. Number waiting = '
            + str(len(self.patientsWaiting) - 1) + '.')

        # pop the patient
        return self.patientsWaiting.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patientsWaiting)


class Room:
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create an exam room
        :param id: (integer) the room ID
        :param service_time_dist: distribution of service time in thisroom
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


class ExamRoom(Room):
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create an exam room
        :param id: (integer) the exam room ID
        :param service_time_dist: distribution of service time in this exam room
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        Room.__init__(self, id=id, service_time_dist=service_time_dist, urgent_care=urgent_care, sim_cal=sim_cal,
                      sim_out=sim_out, trace=trace)

    def __str__(self):
        """ :returns (string) the exam room number """
        return "Exam Room " + str(self.id)

    def exam(self, patient, rng):
        """ starts examining on the patient
        :param patient: a patient
        :param rng: random number generator
        """

        # the exam room is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # collect statistics
        self.simOut.collect_patient_starting_exam()

        # find the exam completion time (current time + service time)
        exam_completion_time = self.simCal.time + self.serviceTimeDist.sample(rng=rng)

        # schedule the end of exam
        self.simCal.add_event(
            event=E.EndOfExam(time=exam_completion_time, exam_room=self, urgent_care=self.urgentCare)
        )

    def remove_patient(self):
        """ :returns the patient that was being served in this exam room"""

        # store the patient to be returned and set the patient that was being served to None
        returned_patient = self.patientBeingServed
        self.patientBeingServed = None

        # the exam room is idle now
        self.isBusy = False

        # collect statistics
        self.simOut.collect_patient_ending_exam()

        # collect statistics IF not going to mhs
        self.simOut.collect_patient_departure(patient=returned_patient)

        # trace
        self.trace.add_message(str(returned_patient) + ' leaves ' + str(self) + '.')

        return returned_patient


class ConsultRoom(Room):
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create an exam room
        :param id: (integer) the room ID
        :param service_time_dist: distribution of service time in this consult room
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        Room.__init__(self, id=id, service_time_dist=service_time_dist,urgent_care=urgent_care, sim_cal=sim_cal,
                      sim_out=sim_out, trace=trace)

    def __str__(self):
        """ :returns (string) the exam room number """
        return "Consult Room " + str(self.id)

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
            event=E.EndOfMentalHealthConsult(time=exam_completion_time,
                                             consult_room=self,
                                             urgent_care=self.urgentCare)
        )

    def remove_mh_patient(self):
        """ :returns the patient that was being served in this exam room"""

        # store the patient to be returned and set the patient that was being served to None
        returned_patient = self.patientBeingServed
        self.patientBeingServed = None

        # the exam room is idle now
        self.isBusy = False

        # collect statistics
        self.simOut.collect_patient_ending_mh_exam()

        # collect statistics
        self.simOut.collect_mh_patient_departure(patient=returned_patient)

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

        # model entities
        self.patients = []  # list of patients

        # waiting room
        self.waitingRoom = WaitingRoom(sim_out=self.simOutputs,
                                       trace=self.trace)

        # exam rooms
        self.examRooms = []
        for i in range(0, self.params.nExamRooms):
            self.examRooms.append(ExamRoom(id=i,
                                           service_time_dist=self.params.examTimeDist,
                                           urgent_care=self,
                                           sim_cal=self.simCal,
                                           sim_out=self.simOutputs,
                                           trace=self.trace))

        # waiting room for mental health consultation
        self.consultWaitingRoom = MHWaitingRoom(sim_out=self.simOutputs,
                                                trace=self.trace)

        # create the mental health consultation room
        self.consultRoom = ConsultRoom(id=0,
                                       service_time_dist=self.params.mentalHealthConsultDist,
                                       urgent_care=self,
                                       sim_cal=self.simCal,
                                       sim_out=self.simOutputs,
                                       trace=self.trace)

        # statistics
        self.nPatientsArrived = 0           # number of patients arrived
        self.nPatientsServed = 0            # number of patients served
        self.nPatientsReceivedConsult = 0   # number of patients received mental health consultation

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

        self.nPatientsArrived += 1

        # add the new patient to the list of patients
        self.patients.append(patient)

        # collect statistics on new patient
        self.simOutputs.collect_patient_arrival(patient=patient)

        # find an idle exam room
        idle_room_found = False
        for room in self.examRooms:
            # if this room is busy
            if not room.isBusy:
                # send the last patient to this exam room
                room.exam(patient=patient, rng=rng)
                idle_room_found = True
                # break the for loop
                break

        # if no idle room was found
        if idle_room_found is False:
            # add the patient to the waiting room
            self.waitingRoom.add_patient(patient=patient)

        # find the arrival time of the next patient (current time + time until next arrival)
        next_arrival_time = self.simCal.time + self.params.arrivalTimeDist.sample(rng=rng)

        # find the depression status of the next patient
        if_with_depression = False
        if rng.sample() < self.params.probDepression:
            if_with_depression = True

        # schedule the arrival of the next patient
        self.simCal.add_event(
            event=E.Arrival(
                time=next_arrival_time,
                patient=Patient(id=patient.id + 1, if_with_depression=if_with_depression),
                urgent_care=self
            )
        )

    def process_end_of_exam(self, exam_room, rng):
        """ processes the end of exam in the specified exam room
        :param exam_room: the exam room where the service is ended
        :param rng: random number generator
        """

        # trace
        self.trace.add_message('Processing end of exam in ' + str(exam_room) + '.')

        # get the patient who is about to be discharged
        this_patient = exam_room.remove_patient()

        # check the mental health status of the patient
        if this_patient.ifWithDepression:
            # send the patient to the mental health specialist
            # if the mental health specialist is busy
            if self.consultRoom.isBusy:
                # the patient will join the waiting room in the mental health unity
                self.consultWaitingRoom.add_patient(patient=this_patient)
            else:
                # this patient starts receiving mental health consultation
                self.consultRoom.consult(patient=this_patient, rng=rng)
        else:
            # remove the discharged patient from the list of patients
            self.patients.remove(this_patient)
            self.nPatientsServed += 1

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:

            # start serving the next patient in line
            exam_room.exam(patient=self.waitingRoom.get_next_patient(), rng=rng)

    def process_end_of_consultation(self, consult_room, rng):
        """ process the end of mental health consultation
        :param consult_room: consultation room
        :param rng: random number generator
        """

        # trace
        self.trace.add_message('Processing end of mental health consult in ' + str(consult_room) + '.')

        # get the patient who is about to be discharged
        this_patient = consult_room.remove_mh_patient()

        # remove the discharged patient from the list of patients
        self.patients.remove(this_patient)
        self.nPatientsServed += 1
        self.nPatientsReceivedConsult += 1

        # check if there is any patient waiting
        if self.consultWaitingRoom.get_num_patients_waiting() > 0:
            # start serving the next patient in line
            consult_room.consult(patient=self.consultWaitingRoom.get_next_patient(), rng=rng)

    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # trace
        self.trace.add_message('Processing the closing of the urgent care.')

        # close the urgent care
        self.ifOpen = False

