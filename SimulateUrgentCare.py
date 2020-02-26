import UrgentCareModel as M
import InputData as D
import ModelParameters as P
import SimPy.Plots.SamplePaths as Path


# create an urgent care model
urgentCareModel = M.UrgentCareModel(id=1, parameters=P.Parameters())

# simulate the urgent care
urgentCareModel.simulate(sim_duration=D.SIM_DURATION)

print('Total patients arrived:', urgentCareModel.urgentCare.nPatientsArrived)
print('Total patients served:', urgentCareModel.urgentCare.nPatientsServed)
print('Patients received mental health consultation',  urgentCareModel.urgentCare.nPatientsReceivedConsult)

print('Average patient time in system:', urgentCareModel.simOutputs.get_ave_patient_time_in_system())
print('Average patient waiting time:', urgentCareModel.simOutputs.get_ave_patient_waiting_time())
print('Average patient wait time for MHS:', urgentCareModel.simOutputs.get_ave_patient_mh_waiting_time())

# sample path for patients in the system
Path.plot_sample_path(
    sample_path=urgentCareModel.simOutputs.nPatientInSystem,
    title='Patients In System',
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

# print trace
urgentCareModel.print_trace()
