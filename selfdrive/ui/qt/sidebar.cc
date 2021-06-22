#include "selfdrive/ui/qt/sidebar.h"
#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/common/util.h"
#include "selfdrive/hardware/hw.h"
#include "selfdrive/ui/qt/util.h"

void Sidebar::drawMetric(QPainter &p, const QString &label, const QString &val, QColor c, int y) {
  const QRect rect = {30, y, 240, val.isEmpty() ? (label.contains("\n") ? 124 : 100) : 148};

  p.setPen(Qt::NoPen);
  p.setBrush(QBrush(c));
  p.setClipRect(rect.x() + 6, rect.y(), 18, rect.height(), Qt::ClipOperation::ReplaceClip);
  p.drawRoundedRect(QRect(rect.x() + 6, rect.y() + 6, 100, rect.height() - 12), 10, 10);
  p.setClipping(false);

  QPen pen = QPen(QColor(0xff, 0xff, 0xff, 0x55));
  pen.setWidth(2);
  p.setPen(pen);
  p.setBrush(Qt::NoBrush);
  p.drawRoundedRect(rect, 20, 20);

  p.setPen(QColor(0xff, 0xff, 0xff));
  if (val.isEmpty()) {
    configFont(p, "Open Sans", 35, "Bold");
    const QRect r = QRect(rect.x() + 35, rect.y(), rect.width() - 50, rect.height());
    p.drawText(r, Qt::AlignCenter, label);
  } else {
    configFont(p, "Open Sans", 58, "Bold");
    p.drawText(rect.x() + 50, rect.y() + 71, val);
    configFont(p, "Open Sans", 35, "Regular");
    p.drawText(rect.x() + 50, rect.y() + 50 + 77, label);
  }
}

Sidebar::Sidebar(QWidget *parent) : QFrame(parent) {
  home_img = QImage("../assets/images/button_home.png").scaled(180, 180, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  settings_img = QImage("../assets/images/button_settings.png").scaled(settings_btn.width(), settings_btn.height(), Qt::IgnoreAspectRatio, Qt::SmoothTransformation);;

  setFixedWidth(300);
  setMinimumHeight(vwp_h);
  setStyleSheet("background-color: rgb(57, 57, 57);");
}

void Sidebar::mousePressEvent(QMouseEvent *event) {
  if (settings_btn.contains(event->pos())) {
    emit openSettings();
  }
}

void Sidebar::update(const UIState &s) {
  if (s.sm->frame % (6*UI_FREQ) == 0) {
    connect_str = "OK";
    int battery = (int)s.scene.deviceState.getBatteryPercent();
    connect_status = danger_color;

    if (battery > 20){connect_status = warning_color;}
    if (battery > 90){connect_status = good_color;}

    if(battery == 1){connect_str = "1%";}
    if(battery == 2){connect_str = "2%";}
    if(battery == 3){connect_str = "3%";}
    if(battery == 4){connect_str = "4%";}
    if(battery == 5){connect_str = "5%";}
    if(battery == 6){connect_str = "6%";}
    if(battery == 7){connect_str = "7%";}
    if(battery == 8){connect_str = "8%";}
    if(battery == 9){connect_str = "9%";}
    if(battery == 10){connect_str = "10%";}

    if(battery == 11){connect_str = "11%";}
    if(battery == 12){connect_str = "12%";}
    if(battery == 13){connect_str = "13%";}
    if(battery == 14){connect_str = "14%";}
    if(battery == 15){connect_str = "15%";}
    if(battery == 16){connect_str = "16%";}
    if(battery == 17){connect_str = "17%";}
    if(battery == 18){connect_str = "18%";}
    if(battery == 19){connect_str = "19%";}
    if(battery == 20){connect_str = "20%";}

    if(battery == 21){connect_str = "21%";}
    if(battery == 22){connect_str = "22%";}
    if(battery == 23){connect_str = "23%";}
    if(battery == 24){connect_str = "24%";}
    if(battery == 25){connect_str = "25%";}
    if(battery == 26){connect_str = "26%";}
    if(battery == 27){connect_str = "27%";}
    if(battery == 28){connect_str = "28%";}
    if(battery == 29){connect_str = "29%";}
    if(battery == 30){connect_str = "30%";}

    if(battery == 31){connect_str = "31%";}
    if(battery == 32){connect_str = "32%";}
    if(battery == 33){connect_str = "33%";}
    if(battery == 34){connect_str = "34%";}
    if(battery == 35){connect_str = "35%";}
    if(battery == 36){connect_str = "36%";}
    if(battery == 37){connect_str = "37%";}
    if(battery == 38){connect_str = "38%";}
    if(battery == 39){connect_str = "39%";}
    if(battery == 40){connect_str = "40%";}

    if(battery == 41){connect_str = "41%";}
    if(battery == 42){connect_str = "42%";}
    if(battery == 43){connect_str = "43%";}
    if(battery == 44){connect_str = "44%";}
    if(battery == 45){connect_str = "45%";}
    if(battery == 46){connect_str = "46%";}
    if(battery == 47){connect_str = "47%";}
    if(battery == 48){connect_str = "48%";}
    if(battery == 49){connect_str = "49%";}
    if(battery == 50){connect_str = "50%";}

    if(battery == 51){connect_str = "51%";}
    if(battery == 52){connect_str = "52%";}
    if(battery == 53){connect_str = "53%";}
    if(battery == 54){connect_str = "54%";}
    if(battery == 55){connect_str = "55%";}
    if(battery == 56){connect_str = "56%";}
    if(battery == 57){connect_str = "57%";}
    if(battery == 58){connect_str = "58%";}
    if(battery == 59){connect_str = "59%";}
    if(battery == 60){connect_str = "60%";}

    if(battery == 71){connect_str = "71%";}
    if(battery == 72){connect_str = "72%";}
    if(battery == 73){connect_str = "73%";}
    if(battery == 74){connect_str = "74%";}
    if(battery == 75){connect_str = "75%";}
    if(battery == 76){connect_str = "76%";}
    if(battery == 77){connect_str = "77%";}
    if(battery == 78){connect_str = "78%";}
    if(battery == 79){connect_str = "79%";}
    if(battery == 80){connect_str = "80%";}

    if(battery == 81){connect_str = "81%";}
    if(battery == 82){connect_str = "82%";}
    if(battery == 83){connect_str = "83%";}
    if(battery == 84){connect_str = "84%";}
    if(battery == 85){connect_str = "85%";}
    if(battery == 86){connect_str = "86%";}
    if(battery == 87){connect_str = "87%";}
    if(battery == 88){connect_str = "88%";}
    if(battery == 89){connect_str = "89%";}
    if(battery == 90){connect_str = "90%";}

    if(battery == 91){connect_str = "91%";}
    if(battery == 92){connect_str = "92%";}
    if(battery == 93){connect_str = "93%";}
    if(battery == 94){connect_str = "94%";}
    if(battery == 95){connect_str = "95%";}
    if(battery == 96){connect_str = "96%";}
    if(battery == 97){connect_str = "97%";}
    if(battery == 98){connect_str = "98%";}
    if(battery == 99){connect_str = "99%";}
    if(battery == 100){connect_str = "100%";}

    
    //snprintf(connect_str, sizeof(connect_str), "%d%%%s", s.scene.deviceState.getBatteryPercent(), s.scene.deviceState.getBatteryStatus() == "Charging" ? "+" : "-");
    //connect_str = QString("%1").arg(s.scene.deviceState.getBatteryPercent);


    //connect_status = warning_color;
    //connect_status = good_color;
    //connect_status = danger_color;
    repaint();
  }

  net_type = s.scene.deviceState.getNetworkType();
  strength = s.scene.deviceState.getNetworkStrength();

  temp_status = danger_color;
  auto ts = s.scene.deviceState.getThermalStatus();
  if (ts == cereal::DeviceState::ThermalStatus::GREEN) {
    temp_status = good_color;
  } else if (ts == cereal::DeviceState::ThermalStatus::YELLOW) {
    temp_status = warning_color;
  }
  temp_val = (int)s.scene.deviceState.getAmbientTempC();


  panda_str = "VEHICLE\nONLINE";
  panda_status = good_color;
  if (s.scene.pandaType == cereal::PandaState::PandaType::UNKNOWN) {
    panda_status = danger_color;
    panda_str = "NO\nPANDA";
  } else if (Hardware::TICI() && s.scene.started) {
    panda_str = QString("SAT CNT\n%1").arg(s.scene.satelliteCount);
    panda_status = s.scene.gpsOK ? good_color : warning_color;
  }

  if (s.sm->updated("deviceState") || s.sm->updated("pandaState")) {
    repaint();
  }
}

void Sidebar::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.setPen(Qt::NoPen);
  p.setRenderHint(QPainter::Antialiasing);

  // static imgs
  p.setOpacity(0.65);
  p.drawImage(settings_btn.x(), settings_btn.y(), settings_img);
  p.setOpacity(1.0);
  p.drawImage(60, 1080 - 180 - 40, home_img);

  // network
  p.drawImage(58, 196, signal_imgs[strength]);
  configFont(p, "Open Sans", 35, "Regular");
  p.setPen(QColor(0xff, 0xff, 0xff));
  const QRect r = QRect(50, 247, 100, 50);
  p.drawText(r, Qt::AlignCenter, network_type[net_type]);

  // metrics
  drawMetric(p, "TEMP", QString("%1°C").arg(temp_val), temp_status, 338);
  drawMetric(p, panda_str, "", panda_status, 518);
  drawMetric(p, "BATTERY\n" + connect_str, "", connect_status, 676);
}
