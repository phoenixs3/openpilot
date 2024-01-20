#!/usr/bin/env python3
from cereal import car
from selfdrive.car.ocelot.values import CAR, BUTTON_STATES
from selfdrive.car import STD_CARGO_KG, scale_rot_inertia, scale_tire_stiffness, gen_empty_fingerprint
from selfdrive.swaglog import cloudlog
from selfdrive.car.interfaces import CarInterfaceBase

EventName = car.CarEvent.EventName

class CarInterface(CarInterfaceBase):
  @staticmethod
  def compute_gb(accel, speed):
    return float(accel) / 3.0

  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)

    self.gas_pressed_prev = False
    self.brake_pressed_prev = False
    self.cruise_enabled_prev = False
    self.buttonStatesPrev = BUTTON_STATES.copy()

  @staticmethod
  def get_params(candidate, fingerprint=gen_empty_fingerprint(), car_fw=[]):  # pylint: disable=dangerous-default-value
    ret = CarInterfaceBase.get_std_params(candidate, fingerprint)

    ret.carName = "ocelot"
    ret.lateralTuning.init('pid')
    ret.safetyModel = car.CarParams.SafetyModel.allOutput

    ret.steerActuatorDelay = 0.05       #too small: doesnt look far enough ahead, enters and exists curves late, corrects often in curve
                                        #too large: looks too far ahead, dives into corners too early, hugs inside then exits too early
                                        #going to the outside of the curve
    ret.steerLimitTimer = 0.4           #time between wheel nudge alerts

    if candidate == CAR.SMART_ROADSTER_COUPE:
        ret.lateralTuning.init('pid')
        ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.045], [0.008]]
        ret.lateralTuning.pid.kf = 0.   #was 0.00007818594
        ret.safetyParam = 100           #alloutput for now
        ret.wheelbase = 2.36
        ret.steerRatio = 21
        tire_stiffness_factor = 0.444
        ret.mass = 810 + STD_CARGO_KG
        ret.steerRateCost = 0.4
        ret.centerToFront = ret.wheelbase * 0.44

    ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront,
                                                                         tire_stiffness_factor=tire_stiffness_factor)

    ret.enableGasInterceptor = True
    #ret.stoppingControl = True       #somthing to do with toyota
    ret.enableCamera = True
    ret.openpilotLongitudinalControl = True
    ret.minEnableSpeed = -1.

    ret.stoppingBrakeRate = 0.1 # reach stopping target smoothly (default 0.2)
    ret.startingBrakeRate = 2.0 # release brakes fast (default 0.8)

    #Longitudinal deadzone values
    ret.longitudinalTuning.deadzoneBP = [0., 9.]   #0mph, 20mph
    ret.longitudinalTuning.deadzoneV = [0.05, .15]
    
    #Longitudinal Proportional values
    ret.longitudinalTuning.kpBP = [0., 5., 35.]    #0mph, 11mph, 78mph
    #ret.longitudinalTuning.kpV = [0.45, 0.35, 0.3]  #originals
    ret.longitudinalTuning.kpV = [1.3, 1.0, 0.6]
    
    #Longitudinal Integral Values
    ret.longitudinalTuning.kiBP = [0., 45.]       #0mph, 100mph   
    #ret.longitudinalTuning.kiV = [0.13, 0.1]     #originals
    ret.longitudinalTuning.kiV = [0.2, 0.09]

    #Gas maximum values
    ret.gasMaxBP = [0., 2., 6., 35.]               #0mph, 5mph, 13mph, 78mph
    #ret.gasMaxV = [0.24, 0.3, 0.35, 0.4]          #originals
    ret.gasMaxV = [0.24, 0.3, 0.35, 0.5]

    #Brake maximum values
    ret.brakeMaxBP = [0., 2., 35.]             #0mph, 4.5mph, 78mph
    ret.brakeMaxV = [.28, 0.35, .48]            #0.26*20 = 5.2mm, 0.45*20 = 9mm

    return ret

  #returns a car.CarState
  def update(self, c, can_strings):
    buttonEvents = []
    # ******************* do can recv *******************
    self.cp.update_strings(can_strings)
    self.cp_body.update_strings(can_strings)

    ret = self.CS.update(self.cp, self.cp_body, c.enabled)

    ret.canValid = self.cp.can_valid and self.cp_body.can_valid
    ret.steeringRateLimited = self.CC.steer_rate_limited if self.CC is not None else False
    ret.engineRPM = self.CS.engineRPM
    ret.coolantTemp = self.CS.coolantTemp
    ret.boostPressure = self.CS.boostPressure

    # events
    events = self.create_common_events(ret)
    if not ret.cruiseState.enabled:
      events.add(EventName.pcmDisable)
    # Attempt OP engagement only on rising edge of stock cruise engagement
    elif not self.cruise_enabled_prev:
      events.add(EventName.pcmEnable)

    ret.events = events.to_msg()
    ret.buttonEvents = buttonEvents

    # update previous car states
    self.gas_pressed_prev = ret.gasPressed
    self.brake_pressed_prev = ret.brakePressed
    self.cruise_enabled_prev = ret.cruiseState.enabled
    self.buttonStatesPrev = self.CS.buttonStates.copy()

    self.CS.out = ret.as_reader()
    return self.CS.out

  #Pass in a car.CarControl, to be called @ 100hz
  def apply(self, c):
    can_sends = self.CC.update(c.enabled, self.CS, self.frame,
                               c.actuators, c.cruiseControl.cancel,
                               c.hudControl.visualAlert, c.hudControl.leftLaneVisible,
                               c.hudControl.rightLaneVisible, c.hudControl.leadVisible,
                               c.hudControl.leftLaneDepart, c.hudControl.rightLaneDepart)
    self.frame += 1
    return can_sends
