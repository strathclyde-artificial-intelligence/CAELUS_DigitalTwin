from PowerModels.ChargeModel.charge_cccv import charge_cccv, batt_chg_cell

def test_charge_cccv():
    assert charge_cccv(100, 1) == 1.49

def test_charge_batt_cell():
    assert batt_chg_cell(22, 22) == 2.7500



