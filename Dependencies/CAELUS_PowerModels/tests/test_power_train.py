from PowerModels.PowerTrain.batt_disc import batt_disc
from PowerModels.PowerTrain.power_train_esc_motor import powertrain_ESC_Motor

def test_battery_discharge():
    dod, vbatt = batt_disc(100, 10, 22)
    assert round(dod,4) == 145.4545
    assert round(vbatt, 4) == round(24.167369040000040, 4)

def test_powertrain():
    w,thrust,mod,qcon,idis = powertrain_ESC_Motor(-1, 10, 5, 1/3600)
    assert round(w,4) == 663.6258
    assert round(thrust,4) == 27.3048
    assert round(mod,4) == 5.8616
    assert round(qcon,4) == 0.05
    assert round(idis,4) == 200.1543