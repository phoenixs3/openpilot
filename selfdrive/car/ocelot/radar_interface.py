#!/usr/bin/env python3
import time
from cereal import car
from opendbc.can.parser import CANParser
from selfdrive.car.ocelot.values import DBC
from selfdrive.car.interfaces import RadarInterfaceBase
from math import cos, sin

DELPHI_MRR_RADAR_START_ADDR = 0x120
DELPHI_MRR_RADAR_MSG_COUNT = 64

def _create_delphi_mrr_radar_can_parser(car_fingerprint):
  signals = []
  checks = []

  for i in range(1, DELPHI_MRR_RADAR_MSG_COUNT + 1):
    msg = f"MRR_Detection_{i:03d}"
    signals += [
      (f"CAN_DET_VALID_LEVEL_{i:02d}", msg),
      (f"CAN_DET_AZIMUTH_{i:02d}", msg),
      (f"CAN_DET_RANGE_{i:02d}", msg),
      (f"CAN_DET_RANGE_RATE_{i:02d}", msg),
      (f"CAN_DET_AMPLITUDE_{i:02d}", msg),
      (f"CAN_SCAN_INDEX_2LSB_{i:02d}", msg),
    ]
    checks += [(msg, 20)]

  return CANParser(DBC[car_fingerprint]['radar'], signals, checks, 2)

class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP):
    super().__init__(CP)

    self.updated_messages = set()
    
    #self.validCnt = {key: 0 for key in RADAR_MSGS}
    self.track_id = 0
    #self.radar_ts = CP.radarTimeStep
    #self.no_radar_sleep = 'NO_RADAR_SLEEP' in os.environ

    self.rcp = _create_delphi_mrr_radar_can_parser(CP.carFingerprint)
    self.trigger_msg = DELPHI_MRR_RADAR_START_ADDR + DELPHI_MRR_RADAR_MSG_COUNT - 1

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

    ret = car.RadarData.new_message()
    errors = []
    if not self.rcp.can_valid:
      errors.append("canError")
    ret.errors = errors
    self._update_delphi_mrr()

    ret.points = list(self.pts.values())
    self.updated_messages.clear()
    return ret

  def _update_delphi_mrr(self):
    for ii in range(1, DELPHI_MRR_RADAR_MSG_COUNT + 1):
      msg = self.rcp.vl[f"MRR_Detection_{ii:03d}"]

      # SCAN_INDEX rotates through 0..3 on each message
      # treat these as separate points
      scanIndex = msg[f"CAN_SCAN_INDEX_2LSB_{ii:02d}"]
      i = (ii - 1) * 4 + scanIndex

      if i not in self.pts:
        self.pts[i] = car.RadarData.RadarPoint.new_message()
        self.pts[i].trackId = self.track_id
        self.pts[i].aRel = float('nan')
        self.pts[i].yvRel = float('nan')
        self.track_id += 1

      valid = bool(msg[f"CAN_DET_VALID_LEVEL_{ii:02d}"])
      amplitude = msg[f"CAN_DET_AMPLITUDE_{ii:02d}"]            # dBsm [-64|63]

      if valid and 0 < amplitude <= 15:
        azimuth = msg[f"CAN_DET_AZIMUTH_{ii:02d}"]              # rad [-3.1416|3.13964]
        dist = msg[f"CAN_DET_RANGE_{ii:02d}"]                   # m [0|255.984]
        distRate = msg[f"CAN_DET_RANGE_RATE_{ii:02d}"]          # m/s [-128|127.984]

        # *** openpilot radar point ***
        self.pts[i].dRel = cos(azimuth) * dist                  # m from front of car
        self.pts[i].yRel = -sin(azimuth) * dist                 # in car frame's y axis, left is positive
        self.pts[i].vRel = distRate                             # m/s

        self.pts[i].measured = True

      else:
        del self.pts[i]
