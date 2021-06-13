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
    # dp
    ret.lateralTuning.init('pid')
    ret.safetyModel = car.CarParams.SafetyModel.allOutput

    ret.steerActuatorDelay = 0.15
    ret.steerLimitTimer = 0.4

    if candidate == CAR.SMART_ROADSTER_COUPE:
        ret.lateralTuning.init('pid')
        ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.05], [0.008]]
        ret.lateralTuning.pid.kf = 0.   #was 0.00007818594
        ret.safetyParam = 100
        ret.wheelbase = 2.36
        ret.steerRatio = 14.8
        tire_stiffness_factor = 0.444
        ret.mass = 810 + STD_CARGO_KG
        ret.steerRateCost = 1.
        ret.centerToFront = ret.wheelbase * 0.44


    #ret = common_interface_get_params_lqr(ret)

    ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront,
                                                                         tire_stiffness_factor=tire_stiffness_factor)

    ret.enableGasInterceptor = True
    ret.enableCruise = True         #not found in toyota interface
    ret.enableDsu = False            #maybe this needs disabed for long control
    ret.stoppingControl = True      #should these be enabled for long control
    ret.enableCamera = True
    ret.openpilotLongitudinalControl = True
    cloudlog.warning("ECU Gas Interceptor: %r", ret.enableGasInterceptor)
    ret.minEnableSpeed = -1.

    #Longitudinal deadzone values
    ret.longitudinalTuning.deadzoneBP = [0., 9.]
    ret.longitudinalTuning.deadzoneV = [0., .15]
    
    #Longitudinal Proportional values
    ret.longitudinalTuning.kpBP = [0., 5., 35.]
    ret.longitudinalTuning.kpV = [1., 0.6, 0.3]
    
    #Longitudinal Integral Values
    ret.longitudinalTuning.kiBP = [0., 55.]
    ret.longitudinalTuning.kiV = [0.18, 0.1]

    #Gas maximum values
    ret.gasMaxBP = [0., 9., 35]
    ret.gasMaxV = [0.2, 0.3, 0.4]

    #Brake maximum values
    ret.brakeMaxBP = [5., 20.]
    ret.brakeMaxV = [1., 0.9]
    ret.stoppingBrakeRate = 0.16 # reach stopping target smoothly

    

    return ret

  # returns a car.CarState
  def update(self, c, can_strings, dragonconf):
    buttonEvents = []
    # ******************* do can recv *******************
    self.cp.update_strings(can_strings)
    self.cp_body.update_strings(can_strings)

    ret = self.CS.update(self.cp, self.cp_body, c.enabled)

    # dp
    # self.dragonconf = dragonconf
    # ret.cruiseState.enabled = common_interface_atl(ret, dragonconf.dpAtl)

    ret.canValid = self.cp.can_valid and self.cp_body.can_valid
    ret.steeringRateLimited = self.CC.steer_rate_limited if self.CC is not None else False
    ret.engineRPM = self.CS.engineRPM

    # events
    events = self.create_common_events(ret)
    if not ret.cruiseState.enabled:
      events.add(EventName.pcmDisable)
    # Attempt OP engagement only on rising edge of stock ACC engagement.
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

  # pass in a car.CarControl
  # to be called @ 100hz
  def apply(self, c):

    can_sends = self.CC.update(c.enabled, self.CS, self.frame,
                               c.actuators, c.cruiseControl.cancel,
                               c.hudControl.visualAlert, c.hudControl.leftLaneVisible,
                               c.hudControl.rightLaneVisible, c.hudControl.leadVisible,
                               c.hudControl.leftLaneDepart, c.hudControl.rightLaneDepart, self.dragonconf)

    self.frame += 1
    return can_sends
