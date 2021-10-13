#ifndef __PROPELLERCONTRO_H__
#define __PROPELLERCONTRO_H__

class PropellerControl : public AsyncDroneControl {
private:
    Eigen::VectorXd last_control;
public:
    Eigen::VectorXd get_control(double dt) override;
    Eigen::VectorXd last_control() override;
    void set_control(Eigen::VectorXd c) override;
}

#endif // __PROPELLERCONTRO_H__