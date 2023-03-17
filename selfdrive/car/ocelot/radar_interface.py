#!/usr/bin/env python3
import time
from cereal import car
from opendbc.can.parser import CANParser
from selfdrive.car.ocelot.values import DBC
from selfdrive.car.interfaces import RadarInterfaceBase
from math import cos, sin

RADAR_MSGS = list(range(0x120, 0x15F))

def _create_radar_can_parser(car_fingerprint):
  msg_n = len(RADAR_MSGS)
  signals = list(zip(['CAN_DET_RANGE'] * msg_n + ['CAN_DET_AZIMUTH'] * msg_n + ['CAN_DET_RANGE_RATE'] * msg_n + ['CAN_DET_VALID_LEVEL'] * msg_n + ['CAN_DET_AMPLITUDE'] * msg_n + ['CAN_SCAN_INDEX_2LSB'] * msg_n,
                     RADAR_MSGS * 6,
                     [0] * msg_n + [0] * msg_n + [0] * msg_n + [0] * msg_n + [0] * msg_n + [0] * msg_n))
  checks = list(zip(RADAR_MSGS, [20]*msg_n))

  return CANParser(DBC[car_fingerprint]['radar'], signals, checks, 2)

class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP):
    super().__init__(CP)

    self.updated_messages = set()
    
    self.validCnt = {key: 0 for key in RADAR_MSGS}
    self.track_id = 0
    self.radar_ts = CP.radarTimeStep

    self.rcp = _create_radar_can_parser(CP.carFingerprint)
    self.trigger_msg = 0x15E
    self.updated_messages = set()

    #Disable radar for vision only testing
    self.no_radar = False

  def update(self, can_strings):
    if self.no_radar:
      #time.sleep(0.02)
      #return car.RadarData.new_message()
      #time.sleep(self.radar_ts)
      return super().update(None)
      
    
    vls = self.rcp.update_strings(can_strings)
    self.updated_messages.update(vls)

    if self.trigger_msg not in self.updated_messages:
      return None

    vls = self.rcp.update_strings(can_strings)
    self.updated_messages.update(vls)

    if self.trigger_msg not in self.updated_messages:
      return None

    rr = self._update(self.updated_messages)
    self.updated_messages.clear()

    return rr

  def _update(self, updated_messages):
    ret = car.RadarData.new_message()
    errors = []
    if not self.rcp.can_valid:
      errors.append("canError")
    ret.errors = errors

    for ii in sorted(self.updated_messages):
      cpt = self.rcp.vl[ii]

      if cpt['CAN_DET_VALID_LEVEL'] > 0 and 0 < cpt['CAN_DET_AMPLITUDE_'] <= 15:
        if ii not in self.pts:
          self.pts[ii] = car.RadarData.RadarPoint.new_message()
          self.pts[ii].trackId = self.track_id
          self.track_id += 1
          self.pts[ii].dRel = cos(cpt['CAN_DET_AZIMUTH']) * cpt['CAN_DET_RANGE']
          self.pts[ii].yRel = -sin(cpt['CAN_DET_AZIMUTH']) * cpt['CAN_DET_RANGE']
          self.pts[ii].vRel = cpt['CAN_DET_RANGE_RATE']
          self.pts[ii].aRel = float('nan')
          self.pts[ii].yvRel = float('nan')
          self.pts[ii].measured = True
      else:
        if ii in self.pts:
          del self.pts[ii]

    ret.points = list(self.pts.values())
    self.updated_messages.clear()
    return ret

