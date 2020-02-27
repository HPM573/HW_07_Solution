import UrgentCareModel as M
import InputData as D
import ModelParameters as P
import SimPy.Plots.SamplePaths as Path
import SimPy.Plots.Histogram as Hist


# create an urgent care model
urgentCareModel = M.UrgentCareModel(id=1, parameters=P.Parameters())

# simulate the urgent care
urgentCareModel.simulate(sim_duration=D.SIM_DURATION)

print('Total patients arrived:', urgentCareModel.urgentCare.simOutputs.nPatientsArrived)
print('Total patients served:', urgentCareModel.urgentCare.simOutputs.nPatientsServed)
print('Patients received mental health consultation',  urgentCareModel.urgentCare.simOutputs.nPatientsReceivedConsult)

print('Average patient time in system:', urgentCareModel.simOutputs.get_ave_patient_time_in_system())
print('Average patient waiting time:', urgentCareModel.simOutputs.get_ave_patient_waiting_time())
print('Average patient wait time for MHS:', urgentCareModel.simOutputs.get_ave_patient_mh_waiting_time())

# sample path for patients in the system
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientInSystem,
    title='Patients In System',
    x_label='Simulation time (hours)',
)

# sample path for patients waiting to see a physician
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientsWaiting,
    title='Patients Waiting to See a Physician',
    x_label='Simulation time (hours)',
)

# sample path for patients waiting to see MHS
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientsWaitingMH,
    title='Patients Waiting to see MHS',
    x_label='Simulation time (hours)',
)

# sample path for utilization of PCP
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nExamRoomBusy,
    title='Utilization of PCP',
    x_label='Simulation time (hours)'
)

# sample path for utilization of MHS
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nMentalHealthBusy,
    title='Utilization of MHS',
    x_label='Simulation time (hours)'
)

Hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInSystem,
    title='Patients Time in System',
    x_label='Hours',
    #bin_width=.2
)
Hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInWaitingRoom,
    title='Patients Time in Waiting Room',
    x_label='Hours',
    #bin_width=0.2
)
Hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInMentalHealthWaiting,
    title='Patients Time in MHS Waiting Room',
    x_label='Hours',
    #bin_width=0.2
)

# print trace
urgentCareModel.print_trace()
