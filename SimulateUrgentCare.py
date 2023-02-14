import deampy.plots.histogram as hist
import deampy.plots.sample_paths as path

import InputData as D
import ModelParameters as P
import UrgentCareModel as M

# create an urgent care model
urgentCareModel = M.UrgentCareModel(id=1, parameters=P.Parameters())

# simulate the urgent care
urgentCareModel.simulate(sim_duration=D.SIM_DURATION)

print('Total patients arrived:', urgentCareModel.urgentCare.simOutputs.nPatientsArrived)
print('Total patients served:', urgentCareModel.urgentCare.simOutputs.nPatientsServed)
print('Patients received mental health consultation', urgentCareModel.urgentCare.simOutputs.nPatientsReceivedMHConsult)

print('Average patient time in system:', urgentCareModel.simOutputs.get_ave_patient_time_in_system())
print('Average patient waiting time:', urgentCareModel.simOutputs.get_ave_patient_waiting_time())
print('Average patient wait time for MHS:', urgentCareModel.simOutputs.get_ave_patient_mh_waiting_time())

# sample path for patients in the system
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientInSystem,
    title='Patients In System',
    x_label='Simulation time (hours)',
)

# sample path for patients waiting to see a physician
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientsWaitingPCP,
    title='Patients Waiting to See a PCP',
    x_label='Simulation time (hours)',
)

# sample path for patients waiting to see MHS
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientsWaitingMH,
    title='Patients Waiting to see MHS',
    x_label='Simulation time (hours)',
)

# sample path for utilization of PCP
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPCPBusy,
    title='Utilization of PCP',
    x_label='Simulation time (hours)'
)

# sample path for utilization of MHS
path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nMHSBusy,
    title='Utilization of MHS',
    x_label='Simulation time (hours)'
)

hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInSystem,
    title='Patients Time in System',
    x_label='Hours',
    #bin_width=.2
)
hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInPCPWaitingRoom,
    title='Patients Time in PCP Waiting Room',
    x_label='Hours',
    #bin_width=0.2
)
hist.plot_histogram(
    data=urgentCareModel.simOutputs.patientTimeInMHWaitingRoom,
    title='Patients Time in MHS Waiting Room',
    x_label='Hours',
    #bin_width=0.2
)

# print trace
urgentCareModel.print_trace()
