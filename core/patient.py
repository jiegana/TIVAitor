class Patient:
    def __init__(self, age: int, height_cm: float, weight_kg: float, sex: str):
        self.age = age
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.sex = sex.upper()
        
        # Basic calculations
        self.height_m = self.height_cm / 100.0
        self.bmi = self.weight_kg / (self.height_m ** 2)
        
        # Calculate all weight scalars immediately
        self.ibw_devine = self._calc_devine()
        self.ibw_robinson = self._calc_robinson()
        self.ibw_lorentz = self._calc_lorentz()
        
        # Adjusted Body Weight (Standard formula uses Devine IBW)
        # If patient is underweight, ABW equals actual weight
        if self.weight_kg > self.ibw_devine:
            self.abw = self.ibw_devine + 0.4 * (self.weight_kg - self.ibw_devine)
        else:
            self.abw = self.weight_kg
            
        self.lbm_james = self._calc_james()
        self.ffm = self._calc_ffm() # Janmahasatian

    def _calc_devine(self) -> float:
        if self.sex == 'M': return 50.0 + 0.91 * (self.height_cm - 152.4)
        return 45.5 + 0.91 * (self.height_cm - 152.4)

    def _calc_robinson(self) -> float:
        if self.sex == 'M': return 52.0 + 0.75 * (self.height_cm - 152.4)
        return 49.0 + 0.67 * (self.height_cm - 152.4)

    def _calc_lorentz(self) -> float:
        if self.sex == 'M': return self.height_cm - 100 - ((self.height_cm - 150) / 4)
        return self.height_cm - 100 - ((self.height_cm - 150) / 2.5)

    def _calc_james(self) -> float:
        # James formula for Lean Body Mass
        if self.sex == 'M': return 1.1 * self.weight_kg - 128 * (self.weight_kg / self.height_cm) ** 2
        return 1.07 * self.weight_kg - 148 * (self.weight_kg / self.height_cm) ** 2

    def _calc_ffm(self) -> float:
        # Janmahasatian formula for Fat-Free Mass
        if self.sex == 'M': return (9270.0 * self.weight_kg) / (6680.0 + 216.0 * self.bmi)
        return (9270.0 * self.weight_kg) / (8780.0 + 244.0 * self.bmi)

if __name__ == "__main__":
    p = Patient(40, 170, 70, 'M')
    print(f"BMI: {p.bmi:.1f}, IBW Devine: {p.ibw_devine:.1f}, LBM James: {p.lbm_james:.1f}")