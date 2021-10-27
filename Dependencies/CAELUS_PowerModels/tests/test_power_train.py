from PowerModels.PowerTrain.batt_disc import batt_disc
from PowerModels.PowerTrain.power_train_esc_motor import powertrain_ESC_Motor

def test_battery_discharge():
    dod, vbatt = batt_disc(0, 11, 22)
    assert round(dod,4) == 50.0
    assert round(vbatt, 4) == 23.9631

def test_powertrain():
    w,thrust,mod,qcon,idis = powertrain_ESC_Motor(0.5,  0.3, 22, 0.004)
    print(w, thrust, mod, qcon, idis)
    assert round(w,4) == 331.6732
    assert round(thrust,4) == 6.8204
    assert round(mod,4) == 0.2676
    assert round(qcon,4) == 0.18
    assert round(idis,4) == 49.9965