from cereal import car
from common.numpy_fast import clip
from selfdrive.config import Conversions as CV
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.ocelot.ocelotcan import create_steer_command, create_ibst_command, \
                                           create_pedal_command, create_msg_command
from selfdrive.car.ocelot.values import SteerLimitParams
from opendbc.can.packer import CANPacker

VisualAlert = car.CarControl.HUDControl.VisualAlert

class CarController():
  def __init__(self, dbc_name, CP, VM):
    self.last_steer = 0
    self.last_standstill = False
    self.last_fault_frame = -200
    self.steer_rate_limited = False
    self.packer = CANPacker(dbc_name)

  def update(self, enabled, CS, frame, actuators, pcm_cancel_cmd, hud_alert,
             left_line, right_line, lead, left_lane_depart, right_lane_depart):

    # *** compute control surfaces ***

    # gas
    apply_gas = clip(actuators.gas, 0., 1.)

    if CS.out.brakePressed:
      apply_gas = 0.0

    # steer torque
    new_steer = int(round(actuators.steer * SteerLimitParams.STEER_MAX))
    apply_steer = apply_std_steer_torque_limits(new_steer, self.last_steer, CS.out.steeringTorque, SteerLimitParams)
    self.steer_rate_limited = new_steer != apply_steer

    # only cut torque when steer state is a known fault
    if CS.brakeUnavailable:
      self.last_fault_frame = frame

    # Cut steering for 2s after fault
    if not enabled or (frame - self.last_fault_frame < 200):
      apply_steer = 0
      apply_steer_req = 0
    else:
      apply_steer_req = 1

    self.last_steer = apply_steer
    self.last_standstill = CS.out.standstill

    can_sends = []

    #*** control msgs ***
    #print("steer {0} {1} {2} {3}".format(apply_steer, min_lim, max_lim, CS.steer_torque_motor)

    #If low speed and no gas request then hold brakes on (now using stock op stoppingcontrol feature)
    if CS.out.vEgo < 0.05 and apply_gas < 0.005:
      apply_brakes = 0.37                         #0.37*20 = 7.4mm travel
    else:
      apply_brakes = actuators.brake

    #apply_brakes = actuators.brake

    can_sends.append(create_steer_command(self.packer, apply_steer, apply_steer_req, frame))
    can_sends.append(create_ibst_command(self.packer, enabled, apply_brakes, frame))
    can_sends.append(create_pedal_command(self.packer, apply_gas, frame))

    #UI mesg is at 100Hz but we send asap if:
    if (frame % 100 == 0):
      can_sends.append(create_msg_command(self.packer, enabled, CS.out.cruiseState.speed * CV.MS_TO_MPH, CS.out.vEgo * CV.MS_TO_MPH))

    return can_sends
